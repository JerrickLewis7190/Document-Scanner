import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Paper,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { Document, Field } from '../types';
import FieldEditor from './FieldEditor';
import { logger } from '../utils/logger';

interface DocumentFieldsProps {
  document: Document;
  onFieldsUpdate: (documentId: number, fields: Field[]) => Promise<void>;
}

const DocumentFields: React.FC<DocumentFieldsProps> = ({ document, onFieldsUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);

  // Convert document_content to fields array
  const fields: Field[] = Object.entries(document.document_content)
    .filter(([key]) => key !== 'document_type') // Exclude document_type from editable fields
    .map(([field_name, field_value]) => ({
      field_name,
      field_value: field_value || '',
      corrected: false  // Always set to false initially
    }));

  const handleSave = async (editedFields: Field[]) => {
    try {
      setLoading(true);
      await onFieldsUpdate(document.id, editedFields);
      setIsEditing(false);
      logger.info('Fields updated successfully');
    } catch (error) {
      logger.error('Failed to update fields:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Document Fields</Typography>
        <IconButton 
          onClick={() => setIsEditing(true)}
          color="primary"
          size="small"
        >
          <EditIcon />
        </IconButton>
      </Box>

      <Grid container spacing={2}>
        {/* Always show document type (non-editable) */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Typography sx={{ fontWeight: 'medium', minWidth: '120px' }}>
              Document Type
            </Typography>
            <Typography>
              {document.document_content.document_type || 'Unknown'}
            </Typography>
          </Box>
        </Grid>

        {/* Show other fields */}
        {Object.entries(document.document_content)
          .filter(([key]) => key !== 'document_type')
          .map(([key, value]) => (
            <Grid item xs={12} key={key}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Typography sx={{ fontWeight: 'medium', minWidth: '120px' }}>
                  {key.split('_').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                  ).join(' ')}
                </Typography>
                <Typography>{value || 'N/A'}</Typography>
              </Box>
            </Grid>
          ))
        }
      </Grid>

      <Dialog 
        open={isEditing} 
        onClose={() => setIsEditing(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Fields</DialogTitle>
        <DialogContent>
          <FieldEditor
            fields={fields}
            onSave={handleSave}
            loading={loading}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEditing(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default DocumentFields; 