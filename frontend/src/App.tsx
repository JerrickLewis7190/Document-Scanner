import React, { useState, useEffect } from 'react';
import { Grid, Box, Alert, Snackbar, Typography, AppBar, Toolbar, Button } from '@mui/material';
import UploadForm from './components/UploadForm';
import DocumentViewer from './components/DocumentViewer';
import DocumentFields from './components/DocumentFields';
import HistorySidebar from './components/HistorySidebar';
import { Document, Field } from './types';
import api from './services/api';
import { logger } from './utils/logger';

// Local storage keys
const STORAGE_KEY_SELECTED_DOC = 'documentScanner_selectedDocument';

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [currentFile, setCurrentFile] = useState<File | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUploadForm, setShowUploadForm] = useState(false);

  // Load documents and restore selected document from localStorage
  useEffect(() => {
    logger.info('App component mounted, loading initial documents');
    loadDocuments().then(() => {
      // Try to restore selected document from localStorage
      const savedDocId = localStorage.getItem(STORAGE_KEY_SELECTED_DOC);
      if (savedDocId) {
        try {
          const docId = parseInt(savedDocId);
          logger.info(`Attempting to restore document ID: ${docId} from localStorage`);
          api.getDocument(docId)
            .then(doc => {
              logger.info(`Successfully restored document ID: ${docId}`);
              setSelectedDocument(doc);
            })
            .catch(err => {
              logger.warn(`Failed to restore document ID: ${docId}, it may have been deleted`);
              localStorage.removeItem(STORAGE_KEY_SELECTED_DOC);
            });
        } catch (err) {
          logger.error('Error parsing saved document ID', err);
          localStorage.removeItem(STORAGE_KEY_SELECTED_DOC);
        }
      }
    });
  }, []);

  // Save selected document ID to localStorage whenever it changes
  useEffect(() => {
    if (selectedDocument) {
      localStorage.setItem(STORAGE_KEY_SELECTED_DOC, selectedDocument.id.toString());
    } else {
      localStorage.removeItem(STORAGE_KEY_SELECTED_DOC);
    }
  }, [selectedDocument]);

  const loadDocuments = async () => {
    try {
      logger.debug('Fetching documents from API');
      const docs = await api.getDocuments();
      logger.info(`Successfully loaded ${docs.length} documents`);
      setDocuments(docs);
      return docs;
    } catch (err) {
      const errorMessage = 'Failed to load documents';
      logger.error(errorMessage, err);
      setError(errorMessage);
      return [];
    }
  };

  const handleFileUpload = async (file: File) => {
    logger.info(`Starting upload process for file: ${file.name}`);
    setCurrentFile(file);
    setLoading(true);
    setError(null);
    setShowUploadForm(false);

    try {
      logger.debug('Uploading document to API');
      const document = await api.uploadDocument(file);
      logger.info(`Document uploaded successfully, ID: ${document.id}`);
      setDocuments(prev => [document, ...prev]);
      setSelectedDocument(document);
    } catch (err: any) {
      // Extract more detailed error message if available
      const errorMessage = err.message || 'Failed to process document';
      logger.error(errorMessage, err);
      setError(errorMessage);
      // Show upload form again if there was an error
      setShowUploadForm(true);
    } finally {
      setLoading(false);
    }
  };

  const handleFieldsUpdate = async (documentId: number, fields: Field[]) => {
    try {
      setLoading(true);
      console.log('Starting field update for document ID:', documentId);
      console.log('Fields to update:', fields);
      
      await api.updateDocumentFields(documentId, fields);
      console.log('Backend update successful, now fetching updated document');
      
      // Re-fetch the updated document
      const updatedDoc = await api.getDocument(documentId);
      console.log('Fetched updated document:', updatedDoc);
      
      setSelectedDocument((prevDoc: Document | null) => {
        console.log('Previous selected document:', prevDoc);
        console.log('New selected document:', updatedDoc);
        return updatedDoc;
      });
      
      setDocuments(prev => {
        const newDocs = prev.map(doc => (doc.id === updatedDoc.id ? updatedDoc : doc));
        console.log('Updated documents list');
        return newDocs;
      });
      
      logger.info('Document fields updated successfully');
    } catch (error) {
      console.error('Error in handleFieldsUpdate:', error);
      logger.error('Failed to update document fields:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentSelect = (document: Document) => {
    logger.info(`Selected document ID: ${document.id}, image URL: ${document.image_url}`);
    
    // Pre-fetch image to check if it exists
    if (document.image_url) {
      const fullUrl = document.image_url.startsWith('http') 
        ? document.image_url
        : document.image_url.startsWith('/')
          ? `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'}${document.image_url}`
          : `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'}/${document.image_url}`;
      
      logger.info(`Pre-fetching document image from: ${fullUrl}`);
      
      // For PDFs, check if the file exists with a HEAD request
      if (document.image_url.toLowerCase().endsWith('.pdf')) {
        fetch(fullUrl, { method: 'HEAD' })
          .then(response => {
            if (!response.ok) {
              logger.error(`Document image not available: ${response.status} ${response.statusText}`);
              setError(`The document image is not available (${response.status})`);
            } else {
              logger.info('Document image is available');
              setError(null);
            }
          })
          .catch(err => {
            logger.error(`Error checking document image: ${err.message}`);
            setError(`Error accessing document: ${err.message}`);
          });
      }
    }
    
    setSelectedDocument(document);
    setShowUploadForm(false);
  };

  const handleDocumentDelete = async (documentId: number) => {
    logger.info(`Deleting document ID: ${documentId}`);
    try {
      await api.deleteDocument(documentId);
      logger.info('Document deleted successfully');
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      if (selectedDocument?.id === documentId) {
        setSelectedDocument(null);
      }
    } catch (err) {
      const errorMessage = 'Failed to delete document';
      logger.error(errorMessage, err);
      setError(errorMessage);
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Document Scanner
          </Typography>
        </Toolbar>
      </AppBar>
      <Grid container sx={{ flexGrow: 1, height: 'calc(100vh - 64px)', overflow: 'hidden' }}>
        {/* Left Sidebar */}
        <Grid item sx={{ width: 300, minWidth: 250, maxWidth: 350, bgcolor: '#f7f7f7', borderRight: '1px solid #ddd', display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Box sx={{ p: 2, borderBottom: '1px solid #ddd' }}>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={() => setShowUploadForm(!showUploadForm)}
              sx={{ mb: 2 }}
            >
              {showUploadForm ? 'Cancel' : 'Extract New Document'}
            </Button>
          </Box>
          <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
            <HistorySidebar
              documents={documents}
              onDocumentSelect={handleDocumentSelect}
              onDocumentDelete={handleDocumentDelete}
              selectedDocumentId={selectedDocument?.id}
            />
          </Box>
        </Grid>
        {/* Center Panel */}
        <Grid item sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', bgcolor: '#fff', borderRight: '1px solid #eee', minWidth: 0, height: '100%', overflow: 'hidden' }}>
          <Box sx={{ flexGrow: 1, height: '100%', p: 2 }}>
            {showUploadForm ? (
              <UploadForm onFileUpload={handleFileUpload} />
            ) : selectedDocument ? (
              <DocumentViewer
                file={currentFile}
                loading={loading}
                imageUrl={selectedDocument.image_url}
              />
            ) : (
              <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="textSecondary" variant="h6">
                  No document selected
                </Typography>
              </Box>
            )}
          </Box>
        </Grid>
        {/* Right Panel */}
        <Grid item sx={{ width: 400, minWidth: 320, maxWidth: 500, bgcolor: '#fafbfc', height: '100%', overflow: 'auto', p: 2 }}>
          {selectedDocument && !showUploadForm ? (
            <DocumentFields
              document={selectedDocument}
              onFieldsUpdate={handleFieldsUpdate}
            />
          ) : (
            <Box sx={{ p: 4, textAlign: 'center', color: 'text.secondary' }}>
              <Typography variant="h6">No document selected</Typography>
              <Typography variant="body2">Select a document to view its fields.</Typography>
            </Box>
          )}
        </Grid>
      </Grid>
      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default App;
