import React, { useState, useEffect } from 'react';
import { Paper, Box, Typography, CircularProgress, Button } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';

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
  const [retryCount, setRetryCount] = useState(0);

  // Reset error state when imageUrl changes
  useEffect(() => {
    if (imageUrl) {
      setImageError(false);
    }
  }, [imageUrl]);

  const handleRetry = () => {
    setImageError(false);
    setRetryCount(prev => prev + 1);
  };

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

  // Handle backend image URL with improved URL construction
  const fullImageUrl = imageUrl?.startsWith('http') 
    ? imageUrl 
    : imageUrl 
      ? imageUrl.startsWith('/') 
        ? `${BACKEND_URL}${imageUrl}` 
        : `${BACKEND_URL}/${imageUrl}`
      : undefined;

  // Prevent caching issues by adding cache-busting parameter on retries
  const urlWithCacheBuster = retryCount > 0 && fullImageUrl
    ? `${fullImageUrl}?v=${Date.now()}`
    : fullImageUrl;

  // Check if URL points to a PDF file
  const isPdfUrl = urlWithCacheBuster?.toLowerCase().endsWith('.pdf');

  // Handle PDF from URL
  if (isPdfUrl && urlWithCacheBuster) {
    return (
      <Paper elevation={3} sx={{ height: '100%' }}>
        <Box
          component="object"
          data={urlWithCacheBuster}
          type="application/pdf"
          sx={{
            width: '100%',
            height: '100%'
          }}
        >
          <Typography sx={{ p: 3, textAlign: 'center' }}>
            Your browser does not support PDF viewing. 
            <Button 
              component="a" 
              href={urlWithCacheBuster} 
              target="_blank"
              variant="outlined"
              sx={{ ml: 2 }}
            >
              Download PDF
            </Button>
          </Typography>
        </Box>
      </Paper>
    );
  }

  // Handle image from URL (non-PDF)
  if (urlWithCacheBuster && !imageError && !isPdfUrl) {
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
          src={urlWithCacheBuster}
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

  if (imageError && urlWithCacheBuster) {
    return (
      <Paper
        elevation={3}
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3
        }}
      >
        <Typography color="error" gutterBottom>
          Error loading image
        </Typography>
        <Button 
          startIcon={<RefreshIcon />} 
          variant="outlined" 
          color="primary"
          onClick={handleRetry}
          sx={{ mt: 2 }}
        >
          Retry
        </Button>
      </Paper>
    );
  }

  if (!file && !urlWithCacheBuster) {
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

  // Handle PDF files from file object
  if (file && file.type === 'application/pdf' && fileUrl) {
    return (
      <Paper elevation={3} sx={{ height: '100%' }}>
        <Box
          component="object"
          data={fileUrl}
          type="application/pdf"
          sx={{
            width: '100%',
            height: '100%'
          }}
        >
          <Typography sx={{ p: 3, textAlign: 'center' }}>
            Your browser does not support PDF viewing.
          </Typography>
        </Box>
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
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            p: 3
          }}
        >
          <Typography color="error" gutterBottom>
            Error loading image
          </Typography>
          <Button 
            startIcon={<RefreshIcon />} 
            variant="outlined" 
            color="primary"
            onClick={() => setImageError(false)}
            sx={{ mt: 2 }}
          >
            Retry
          </Button>
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