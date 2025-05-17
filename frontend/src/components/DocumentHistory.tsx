import React, { useState } from 'react';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  IconButton,
  Box,
  Divider,
  Paper
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { Document } from '../types';
import { logger } from '../utils/logger';

interface DocumentHistoryProps {
  documents: Document[];
  selectedId?: number;
  onSelect: (document: Document) => void;
  onDelete: (documentId: number) => Promise<void>;
}

const DocumentHistory: React.FC<DocumentHistoryProps> = ({
  documents,
  selectedId,
  onSelect,
  onDelete
}) => {
  const [loading, setLoading] = useState(false);

  const handleDelete = async (documentId: number) => {
    try {
      setLoading(true);
      await onDelete(documentId);
    } catch (error) {
      logger.error('Failed to delete document:', error);
    } finally {
      setLoading(false);
    }
  };

  if (documents.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
        <Typography color="textSecondary" align="center">
          No documents yet
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Document History
      </Typography>
      <List>
        {documents.map((doc) => (
          <ListItem
            key={doc.id}
            disablePadding
            secondaryAction={
              <IconButton
                edge="end"
                aria-label="delete"
                onClick={() => handleDelete(doc.id)}
                disabled={loading}
              >
                <DeleteIcon />
              </IconButton>
            }
          >
            <ListItemButton
              selected={doc.id === selectedId}
              onClick={() => onSelect(doc)}
            >
              <ListItemText
                primary={doc.filename}
                secondary={doc.document_type}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default DocumentHistory; 