import React, { useState, useCallback } from 'react';
import { Alert } from '@mui/material';

interface ImageResolutionValidatorProps {
  file: File | null;
  minWidth?: number;
  minHeight?: number;
  onValidationResult?: (isValid: boolean) => void;
}

/**
 * Component to validate image resolution before uploading to the server
 * This can prevent unnecessary API calls for images that will be rejected
 */
const ImageResolutionValidator: React.FC<ImageResolutionValidatorProps> = ({
  file,
  minWidth = 500,
  minHeight = 300,
  onValidationResult
}) => {
  const [error, setError] = useState<string | null>(null);
  
  // Validate image dimensions when file changes
  const validateImage = useCallback(async (file: File) => {
    // Only validate images, not PDFs
    if (!file.type.startsWith('image/')) {
      setError(null);
      onValidationResult?.(true);
      return;
    }
    
    try {
      // Create a URL for the image file
      const url = URL.createObjectURL(file);
      
      // Create an image element to check dimensions
      const img = new Image();
      
      // Set up promise to resolve when image loads
      const checkDimensions = new Promise<{ width: number, height: number }>((resolve, reject) => {
        img.onload = () => {
          resolve({ width: img.width, height: img.height });
          URL.revokeObjectURL(url); // Clean up the URL object
        };
        img.onerror = () => {
          reject(new Error('Failed to load image'));
          URL.revokeObjectURL(url);
        };
      });
      
      // Set the source to trigger the load
      img.src = url;
      
      // Wait for the image to load and get dimensions
      const { width, height } = await checkDimensions;
      
      // Check if image meets minimum requirements
      if (width < minWidth || height < minHeight) {
        const errorMsg = `Image resolution too low (${width}x${height}). Minimum required is ${minWidth}x${minHeight} for accurate processing.`;
        setError(errorMsg);
        onValidationResult?.(false);
      } else {
        setError(null);
        onValidationResult?.(true);
      }
    } catch (err) {
      setError('Error validating image dimensions');
      onValidationResult?.(false);
    }
  }, [minWidth, minHeight, onValidationResult]);
  
  // Validate when file changes
  React.useEffect(() => {
    if (file) {
      validateImage(file);
    } else {
      setError(null);
    }
  }, [file, validateImage]);
  
  // Only render error message if there is an error
  if (!error) return null;
  
  return (
    <Alert severity="warning" sx={{ mt: 2, mb: 2 }}>
      {error}
    </Alert>
  );
};

export default ImageResolutionValidator; 