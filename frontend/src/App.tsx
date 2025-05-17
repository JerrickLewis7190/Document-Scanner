import React, { useState, useEffect } from 'react';
import { Grid, Box, Alert, Snackbar, Typography, AppBar, Toolbar, Button } from '@mui/material';
import UploadForm from './components/UploadForm';
import DocumentViewer from './components/DocumentViewer';
import DocumentFields from './components/DocumentFields';
import HistorySidebar from './components/HistorySidebar';
import { Document, Field } from './types';
import api from './services/api';
import { logger } from './utils/logger';

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [currentFile, setCurrentFile] = useState<File | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUploadForm, setShowUploadForm] = useState(false);

  useEffect(() => {
    logger.info('App component mounted, loading initial documents');
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      logger.debug('Fetching documents from API');
      const docs = await api.getDocuments();
      logger.info(`Successfully loaded ${docs.length} documents`);
      setDocuments(docs);
    } catch (err) {
      const errorMessage = 'Failed to load documents';
      logger.error(errorMessage, err);
      setError(errorMessage);
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
    } catch (err) {
      const errorMessage = 'Failed to process document';
      logger.error(errorMessage, err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleFieldsUpdate = async (documentId: number, fields: Field[]) => {
    try {
      setLoading(true);
      const updatedDoc = await api.updateDocumentFields(documentId, fields);
      setSelectedDocument(updatedDoc);
      setDocuments(prev => prev.map(doc => (doc.id === updatedDoc.id ? updatedDoc : doc)));
      logger.info('Document fields updated successfully');
    } catch (error) {
      logger.error('Failed to update document fields:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentSelect = (document: Document) => {
    logger.info(`Selected document ID: ${document.id}`);
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

  const handleDeleteAll = async () => {
    logger.info('Deleting all documents');
    try {
      await api.deleteAllDocuments();
      logger.info('All documents deleted successfully');
      setDocuments([]);
      setSelectedDocument(null);
      setCurrentFile(undefined);
    } catch (err) {
      const errorMessage = 'Failed to delete all documents';
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
              onDeleteAll={handleDeleteAll}
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
