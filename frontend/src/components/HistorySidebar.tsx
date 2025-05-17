import React from 'react';
import {
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Button,
  Box,
  Divider,
  ListItemButton
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import { Document } from '../services/api';

interface HistorySidebarProps {
  documents: Document[];
  onDocumentSelect: (document: Document) => void;
  onDocumentDelete: (documentId: number) => void;
  onDeleteAll: () => void;
  selectedDocumentId?: number;
}

const HistorySidebar: React.FC<HistorySidebarProps> = ({
  documents,
  onDocumentSelect,
  onDocumentDelete,
  onDeleteAll,
  selectedDocumentId
}) => {
  const formatDocumentType = (type: string): string => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Paper elevation={3} sx={{ height: '100%', overflow: 'hidden' }}>
      <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">Document History</Typography>
        <Button
          startIcon={<DeleteSweepIcon />}
          color="error"
          onClick={onDeleteAll}
          disabled={documents.length === 0}
        >
          Clear All
        </Button>
      </Box>
      <Divider />
      <List sx={{ overflow: 'auto', maxHeight: 'calc(100vh - 200px)' }}>
        {documents.map((doc) => (
          <ListItem
            key={doc.id}
            component="div"
            disablePadding
          >
            <ListItemButton
              selected={doc.id === selectedDocumentId}
              onClick={() => onDocumentSelect(doc)}
            >
              <ListItemText
                primary={doc.filename}
                secondary={
                  <>
                    {formatDocumentType(doc.document_type)}
                    <br />
                    {formatDate(doc.created_at)}
                  </>
                }
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => onDocumentDelete(doc.id)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItemButton>
          </ListItem>
        ))}
        {documents.length === 0 && (
          <Box p={3} textAlign="center">
            <Typography color="textSecondary">
              No documents processed yet
            </Typography>
          </Box>
        )}
      </List>
    </Paper>
  );
};

export default HistorySidebar; 