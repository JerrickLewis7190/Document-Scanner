import React from 'react';
import {
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  ListItemButton,
  Box
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { Document } from '../types';

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
    <Paper elevation={0} sx={{ height: '100%', overflow: 'hidden', bgcolor: 'transparent', boxShadow: 'none' }}>
      <Box p={2} pb={1}>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
          Recent extractions
        </Typography>
      </Box>
      <List sx={{ overflowY: 'auto', maxHeight: 'calc(100vh - 180px)', px: 1 }}>
        {documents.map((doc) => (
          <ListItem
            key={doc.id}
            component="div"
            disablePadding
            sx={{ mb: 1, borderRadius: 1, bgcolor: doc.id === selectedDocumentId ? '#e3f2fd' : 'transparent' }}
          >
            <ListItemButton
              selected={doc.id === selectedDocumentId}
              onClick={() => onDocumentSelect(doc)}
              sx={{ borderRadius: 1 }}
            >
              <ListItemText
                primary={doc.filename}
                secondary={formatDocumentType(doc.document_type)}
                primaryTypographyProps={{ fontWeight: doc.id === selectedDocumentId ? 'bold' : 'normal' }}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => onDocumentDelete(doc.id)}
                  size="small"
                >
                  <DeleteIcon fontSize="small" />
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