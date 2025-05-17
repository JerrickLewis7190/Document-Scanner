import React from 'react';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  IconButton,
  Box,
  Divider
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { Document } from '../types';
import { logger } from '../utils/logger';

interface DocumentHistoryProps {
  documents: Document[];
  selectedDocument: Document | null;
  onSelectDocument: (document: Document) => void;
  onDeleteDocument: (documentId: number) => void;
  onDeleteAllDocuments: () => void;
}

const DocumentHistory: React.FC<DocumentHistoryProps> = ({
  documents,
  selectedDocument,
  onSelectDocument,
  onDeleteDocument,
  onDeleteAllDocuments,
}) => {
  const handleDelete = (document: Document, event: React.MouseEvent) => {
    event.stopPropagation();
    logger.info(`Deleting document: ${document.id}`);
    onDeleteDocument(document.id);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <List sx={{ flexGrow: 1, overflow: 'auto' }}>
        {documents.map((doc, index) => (
          <React.Fragment key={doc.id}>
            <ListItem
              disablePadding
              secondaryAction={
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={(e) => handleDelete(doc, e)}
                  size="small"
                >
                  <DeleteIcon />
                </IconButton>
              }
            >
              <ListItemButton
                selected={selectedDocument?.id === doc.id}
                onClick={() => onSelectDocument(doc)}
                sx={{ 
                  borderRadius: 1,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25, 118, 210, 0.08)',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.12)',
                    },
                  },
                }}
              >
                <ListItemText
                  primary={`Document ${index + 1}`}
                  primaryTypographyProps={{
                    variant: 'body1',
                    sx: { fontWeight: 'medium' }
                  }}
                />
              </ListItemButton>
            </ListItem>
            {index < documents.length - 1 && <Divider />}
          </React.Fragment>
        ))}
        
        {documents.length === 0 && (
          <ListItem>
            <ListItemText
              primary={
                <Typography color="textSecondary" align="center">
                  No documents processed yet
                </Typography>
              }
            />
          </ListItem>
        )}
      </List>
    </Box>
  );
};

export default DocumentHistory; 