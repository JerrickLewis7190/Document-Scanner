import React, { useState, useEffect } from 'react';
import { Container, Grid, Box, Alert, Snackbar, Paper, Button, Typography } from '@mui/material';
import UploadForm from './components/UploadForm';
import DocumentViewer from './components/DocumentViewer';
import FieldEditor from './components/FieldEditor';
import DocumentHistory from './components/DocumentHistory';
import api, { Document, Field } from './services/api';
import AddIcon from '@mui/icons-material/Add';
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

  const handleFieldSave = async (fields: Field[]) => {
    if (!selectedDocument) {
      logger.warn('Attempted to save fields with no document selected');
      return;
    }

    logger.info(`Saving fields for document ID: ${selectedDocument.id}`);
    setLoading(true);
    setError(null);

    try {
      logger.debug('Updating document fields in API');
      const updatedDoc = await api.getDocument(selectedDocument.id);
      logger.info('Document fields updated successfully');
      setDocuments(prev =>
        prev.map(doc => (doc.id === updatedDoc.id ? updatedDoc : doc))
      );
      setSelectedDocument(updatedDoc);
    } catch (err) {
      const errorMessage = 'Failed to save changes';
      logger.error(errorMessage, err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentSelect = (document: Document) => {
    logger.info(`Selected document ID: ${document.id}`);
    setSelectedDocument(document);
    setCurrentFile(undefined);
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
    <Container maxWidth="xl" sx={{ height: '100vh', py: 3 }}>
      <Grid container spacing={2} sx={{ height: '100%' }}>
        {/* Left Panel */}
        <Grid item xs={3} sx={{ height: '100%' }}>
          <Paper elevation={3} sx={{ height: '100%', p: 2, display: 'flex', flexDirection: 'column' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => setShowUploadForm(true)}
              sx={{ mb: 2 }}
              size="large"
            >
              Extract New Document {documents.length > 0 && `(${documents.length})`}
            </Button>
            
            <Typography variant="h6" sx={{ mb: 2 }}>Recent extractions</Typography>
            
            <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
              <DocumentHistory
                documents={documents}
                selectedDocument={selectedDocument}
                onSelectDocument={handleDocumentSelect}
                onDeleteDocument={handleDocumentDelete}
                onDeleteAllDocuments={handleDeleteAll}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Middle Panel - Document Viewer */}
        <Grid item xs={6} sx={{ height: '100%' }}>
          <Paper elevation={3} sx={{ height: '100%', p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Original document view</Typography>
            <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
              {showUploadForm ? (
                <UploadForm onFileUpload={handleFileUpload} />
              ) : (
                <DocumentViewer
                  file={currentFile}
                  loading={loading}
                />
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Right Panel - Field Editor */}
        <Grid item xs={3} sx={{ height: '100%' }}>
          <Paper elevation={3} sx={{ height: '100%', p: 2, display: 'flex', flexDirection: 'column' }}>
            {selectedDocument ? (
              <>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Extracted Fields
                </Typography>
                <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
                  <FieldEditor
                    fields={selectedDocument.fields}
                    onSave={handleFieldSave}
                    loading={loading}
                  />
                </Box>
              </>
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <Typography color="textSecondary">
                  Select a document to view extracted fields
                </Typography>
              </Box>
            )}
          </Paper>
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
    </Container>
  );
}

export default App;
