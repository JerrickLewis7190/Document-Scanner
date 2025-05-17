import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Paper } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

interface UploadFormProps {
  onFileUpload: (file: File) => void;
}

const UploadForm: React.FC<UploadFormProps> = ({ onFileUpload }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

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
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
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
      </Box>
    </Paper>
  );
};

export default UploadForm; 