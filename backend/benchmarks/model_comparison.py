import time
from typing import Dict, List
import torch
from transformers import (
    LayoutLMv2Processor, 
    LayoutLMv2ForSequenceClassification,
    LayoutLMForSequenceClassification,
    BertForSequenceClassification
)
import pytesseract
from PIL import Image
import numpy as np
from pathlib import Path
import json

class ModelBenchmark:
    def __init__(self, test_data_dir: str):
        self.test_data_dir = Path(test_data_dir)
        self.results = {}
        
    def setup_models(self):
        """Initialize all models for comparison"""
        self.models = {
            'layoutlmv2': {
                'processor': LayoutLMv2Processor.from_pretrained("microsoft/layoutlmv2-base-uncased"),
                'model': LayoutLMv2ForSequenceClassification.from_pretrained("microsoft/layoutlmv2-base-uncased")
            },
            'layoutlm': {
                'processor': LayoutLMForSequenceClassification.from_pretrained("microsoft/layoutlm-base-uncased"),
                'model': LayoutLMForSequenceClassification.from_pretrained("microsoft/layoutlm-base-uncased")
            },
            'bert': {
                'processor': None,  # Using Tesseract for text extraction
                'model': BertForSequenceClassification.from_pretrained("bert-base-uncased")
            },
            'tesseract': {
                'processor': None,
                'model': None
            }
        }
        
    def benchmark_model(self, model_name: str, image_path: str) -> Dict:
        """Benchmark a single model on one image"""
        start_time = time.time()
        
        if model_name in ['layoutlmv2', 'layoutlm']:
            # Process with LayoutLM models
            image = Image.open(image_path)
            processor = self.models[model_name]['processor']
            model = self.models[model_name]['model']
            
            encoding = processor(image, return_tensors="pt")
            outputs = model(**encoding)
            
        elif model_name == 'bert':
            # Extract text with Tesseract, then process with BERT
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            model = self.models[model_name]['model']
            
            # Process text with BERT
            inputs = model.tokenizer(text, return_tensors="pt")
            outputs = model(**inputs)
            
        else:  # tesseract
            # Basic OCR
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            outputs = {'text': text}
            
        end_time = time.time()
        
        return {
            'processing_time': end_time - start_time,
            'outputs': outputs
        }
        
    def run_benchmarks(self):
        """Run benchmarks on all test images"""
        self.setup_models()
        
        # Process each test image
        for image_path in self.test_data_dir.glob('*.png'):
            image_results = {}
            
            # Test each model
            for model_name in self.models.keys():
                try:
                    results = self.benchmark_model(model_name, str(image_path))
                    image_results[model_name] = results
                except Exception as e:
                    print(f"Error benchmarking {model_name} on {image_path}: {str(e)}")
                    
            self.results[image_path.name] = image_results
            
    def evaluate_accuracy(self, ground_truth_file: str):
        """Evaluate accuracy against ground truth data"""
        with open(ground_truth_file) as f:
            ground_truth = json.load(f)
            
        accuracy_scores = {model: [] for model in self.models.keys()}
        
        for image_name, truth in ground_truth.items():
            if image_name in self.results:
                for model_name in self.models.keys():
                    if model_name in self.results[image_name]:
                        # Compare extracted fields with ground truth
                        extracted = self.results[image_name][model_name]['outputs']
                        score = self._calculate_accuracy(extracted, truth)
                        accuracy_scores[model_name].append(score)
                        
        # Calculate average accuracy for each model
        for model_name in accuracy_scores:
            scores = accuracy_scores[model_name]
            if scores:
                avg_accuracy = sum(scores) / len(scores)
                self.results[f"{model_name}_accuracy"] = avg_accuracy
                
    def _calculate_accuracy(self, extracted: Dict, truth: Dict) -> float:
        """Calculate accuracy score for extracted fields"""
        if not truth or not extracted:
            return 0.0
            
        correct = 0
        total = len(truth)
        
        for field, value in truth.items():
            if field in extracted and extracted[field] == value:
                correct += 1
                
        return correct / total
        
    def save_results(self, output_file: str):
        """Save benchmark results to file"""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
if __name__ == "__main__":
    # Run benchmarks
    benchmark = ModelBenchmark("tests/test_data")
    benchmark.run_benchmarks()
    benchmark.evaluate_accuracy("tests/ground_truth.json")
    benchmark.save_results("benchmark_results.json") 