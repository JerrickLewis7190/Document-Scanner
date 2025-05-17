import React, { useState } from 'react';
import { Paper, Box, Typography, CircularProgress } from '@mui/material';

interface DocumentViewerProps {
  file?: File;
  loading?: boolean;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  file,
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

  if (!file) {
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
          Upload a document to view it here
        </Typography>
      </Paper>
    );
  }

  const fileUrl = URL.createObjectURL(file);

  if (file.type === 'application/pdf') {
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

  return (
    <Paper elevation={3} sx={{ height: '100%', overflow: 'hidden' }}>
      {imageError ? (
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          height="100%"
          p={3}
        >
          <Typography color="error">
            Error loading image
          </Typography>
        </Box>
      ) : (
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
      )}
    </Paper>
  );
};

export default DocumentViewer; 