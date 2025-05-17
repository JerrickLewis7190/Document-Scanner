import React, { useState } from 'react';
import { Paper, Box, Typography, CircularProgress } from '@mui/material';

interface DocumentViewerProps {
  file?: File;
  imageUrl?: string;
  loading?: boolean;
}

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  file,
  imageUrl,
  loading = false
}) => {
  const [imageError, setImageError] = useState(false);

  if (loading) {
    return (
      <Paper
        elevation={3}
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <CircularProgress />
      </Paper>
    );
  }

  // Handle backend image URL
  const fullImageUrl = imageUrl?.startsWith('http') 
    ? imageUrl 
    : imageUrl 
      ? `${BACKEND_URL}${imageUrl}` 
      : undefined;

  if (fullImageUrl && !imageError) {
    return (
      <Paper 
        elevation={3} 
        sx={{ 
          height: '100%', 
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <Box
          component="img"
          src={fullImageUrl}
          alt="Document Preview"
          onError={() => setImageError(true)}
          sx={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain'
          }}
        />
      </Paper>
    );
  }

  if (!file && !fullImageUrl) {
    return (
      <Paper
        elevation={3}
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3
        }}
      >
        <Typography color="textSecondary">
          No document to display
        </Typography>
      </Paper>
    );
  }

  const fileUrl = file ? URL.createObjectURL(file) : undefined;

  // Handle PDF files
  if (file && file.type === 'application/pdf' && fileUrl) {
    return (
      <Paper elevation={3} sx={{ height: '100%' }}>
        <Box
          component="iframe"
          src={fileUrl}
          sx={{
            width: '100%',
            height: '100%',
            border: 'none'
          }}
          title="PDF Viewer"
        />
      </Paper>
    );
  }

  // Handle image files
  return (
    <Paper elevation={3} sx={{ height: '100%', overflow: 'hidden' }}>
      {imageError ? (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            p: 3
          }}
        >
          <Typography color="error">
            Error loading image
          </Typography>
        </Box>
      ) : fileUrl ? (
        <Box
          component="img"
          src={fileUrl}
          alt="Document Preview"
          onError={() => setImageError(true)}
          sx={{
            width: '100%',
            height: '100%',
            objectFit: 'contain'
          }}
        />
      ) : (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            p: 3
          }}
        >
          <Typography color="textSecondary">
            No preview available
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default DocumentViewer; 