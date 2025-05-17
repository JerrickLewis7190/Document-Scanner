import React from 'react';
import { Box, CircularProgress } from '@mui/material';
import { useDropzone } from 'react-dropzone';

interface DocumentUploaderProps {
  onUpload: (file: File) => void;
  loading: boolean;
}

const DocumentUploader: React.FC<DocumentUploaderProps> = ({ onUpload, loading }) => {
  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    onDrop: files => {
      if (files.length > 0) {
        onUpload(files[0]);
      }
    }
  });

  return (
    <Box
      {...getRootProps()}
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        cursor: 'pointer',
        opacity: 0,
        zIndex: 2,
      }}
    >
      <input {...getInputProps()} id="document-upload" />
    </Box>
  );
};

export default DocumentUploader; 