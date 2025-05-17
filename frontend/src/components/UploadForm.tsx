import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Paper, Button } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ImageResolutionValidator from './ImageResolutionValidator';

interface UploadFormProps {
  onFileUpload: (file: File) => void;
}

const UploadForm: React.FC<UploadFormProps> = ({ onFileUpload }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isValid, setIsValid] = useState<boolean>(true);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const handleUpload = useCallback(() => {
    if (selectedFile && isValid) {
      onFileUpload(selectedFile);
    }
  }, [selectedFile, isValid, onFileUpload]);

  const handleValidationResult = useCallback((valid: boolean) => {
    setIsValid(valid);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  return (
    <Paper
      elevation={3}
      sx={{
        p: 3,
        textAlign: 'center',
        backgroundColor: 'background.paper'
      }}
    >
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : (selectedFile && !isValid ? 'error.main' : 'grey.300'),
          borderRadius: 2,
          p: 3,
          cursor: 'pointer',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover'
          }
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop the file here' : 'Drag & drop a document here'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          or click to select a file
        </Typography>
        <Typography variant="caption" color="textSecondary" display="block" mt={1}>
          Supported formats: PDF, PNG, JPG
        </Typography>
        {selectedFile && (
          <Typography variant="body2" sx={{ mt: 2 }}>
            Selected: {selectedFile.name}
          </Typography>
        )}
      </Box>

      {/* Client-side resolution validation */}
      <ImageResolutionValidator 
        file={selectedFile} 
        minWidth={500} 
        minHeight={300} 
        onValidationResult={handleValidationResult}
      />

      {selectedFile && (
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleUpload} 
          disabled={!isValid}
          sx={{ mt: 2 }}
        >
          Process Document
        </Button>
      )}
    </Paper>
  );
};

export default UploadForm; 