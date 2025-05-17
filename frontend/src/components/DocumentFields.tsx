import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Paper,
  Grid,
  Button,
  TextField
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { Document, Field } from '../types';
import { logger } from '../utils/logger';

interface DocumentFieldsProps {
  document: Document;
  onFieldsUpdate: (documentId: number, fields: Field[]) => Promise<void>;
}

const DocumentFields: React.FC<DocumentFieldsProps> = ({ document, onFieldsUpdate }) => {
  const [editingField, setEditingField] = useState<string | null>(null);
  const [fieldValue, setFieldValue] = useState('');
  const [loading, setLoading] = useState(false);

  // Convert document_content to fields array
  const fields: Field[] = Object.entries(document.document_content)
    .filter(([key]) => key !== 'document_type') // Exclude document_type from editable fields
    .map(([field_name, field_value]) => ({
      field_name,
      field_value: field_value || '',
      corrected: false  // Always set to false initially
    }));

  // Get document type (normalized)
  const documentType = document.document_content.document_type?.toLowerCase() || 'unknown';

  // Define the specific fields to show for each document type
  const getVisibleFields = (docType: string): string[] => {
    if (docType.includes('passport')) {
      // Show only the specified fields for passport
      return ['full_name', 'date_of_birth', 'country', 'issue_date', 'expiration_date'];
    } else if (docType.includes('driver') || docType.includes('license')) {
      // For driver's license, show these fields in this specific order
      return ['license_number', 'date_of_birth', 'issue_date', 'expiration_date', 'first_name', 'last_name'];
    } else if (docType.includes('ead') || docType.includes('card')) {
      return ['card_number', 'category', 'first_name', 'last_name', 'card_expires_date'];
    }
    // Default - show all fields
    return Object.keys(document.document_content).filter(k => k !== 'document_type');
  };
  
  const handleEditClick = (fieldName: string, value: string) => {
    setEditingField(fieldName);
    setFieldValue(value);
  };

  const handleSave = async (fieldName: string) => {
    setLoading(true);
    try {
      console.log('Saving field:', fieldName, 'New value:', fieldValue);
      
      // Special handling for document_type
      let updatedFields: Field[];
      if (fieldName === 'document_type') {
        console.log('Updating document_type to:', fieldValue);
        // Create a special field for document_type
        updatedFields = [
          ...fields,
          {
            field_name: 'document_type',
            field_value: fieldValue,
            corrected: true
          }
        ];
      } else {
        updatedFields = fields.map(f =>
          f.field_name === fieldName ? { ...f, field_value: fieldValue, corrected: true } : f
        );
      }
      
      console.log('Sending updated fields:', updatedFields);
      await onFieldsUpdate(document.id, updatedFields);
      console.log('Fields update API call completed');
      
      setEditingField(null);
      logger.info('Fields updated successfully');
    } catch (error) {
      console.error('Error updating fields:', error);
      logger.error('Failed to update fields:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditingField(null);
    setFieldValue('');
  };

  // Function to render a field
  const renderField = (key: string) => {
    const value = document.document_content[key];
    const isMissing = !value || value === 'NOT_FOUND';
    const fieldValue = value?.toString() || '';
    
    return (
      <Grid item xs={12} key={key}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 1, 
          width: '100%', 
          overflow: 'visible', 
          flexWrap: 'wrap',
          backgroundColor: isMissing ? 'rgba(255, 0, 0, 0.05)' : 'transparent',
          p: 1,
          borderRadius: 1
        }}>
          <Typography sx={{ fontWeight: 'medium', minWidth: 140, flexShrink: 0 }}>
            {key.split('_').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')}
          </Typography>
          {editingField === key ? (
            <>
              <TextField
                value={fieldValue}
                onChange={e => setFieldValue(e.target.value)}
                size="small"
                error={isMissing}
                helperText={isMissing ? "This field is required" : ""}
                sx={{ flexGrow: 1, minWidth: 250, maxWidth: 350 }}
              />
              <Button 
                onClick={() => handleSave(key)} 
                size="small" 
                variant="contained" 
                disabled={loading} 
                sx={{ ml: 1, whiteSpace: 'nowrap' }}
              >
                Save
              </Button>
              <Button 
                onClick={handleCancel} 
                size="small" 
                variant="outlined" 
                disabled={loading} 
                sx={{ ml: 1, whiteSpace: 'nowrap' }}
              >
                Cancel
              </Button>
            </>
          ) : (
            <>
              <Typography 
                sx={{ 
                  flex: 1, 
                  color: isMissing ? 'error.main' : 'text.primary',
                  fontWeight: isMissing ? 'bold' : 'normal'
                }}
              >
                {fieldValue ? fieldValue : 'NOT FOUND'}
              </Typography>
              <Button 
                onClick={() => handleEditClick(key, fieldValue)} 
                size="small" 
                variant="outlined" 
                color={isMissing ? "error" : "primary"}
              >
                EDIT
              </Button>
            </>
          )}
        </Box>
      </Grid>
    );
  };

  // Get the list of fields to display based on document type
  const visibleFields = getVisibleFields(documentType);

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Document Fields</Typography>
        <IconButton 
          onClick={() => setEditingField('document_type')}
          color="primary"
          size="small"
        >
          <EditIcon />
        </IconButton>
      </Box>

      <Grid container spacing={2}>
        {/* Always show document type */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 1, width: '100%', overflow: 'visible', flexWrap: 'wrap', alignItems: 'center' }}>
            <Typography sx={{ fontWeight: 'medium', minWidth: '120px', flexShrink: 0 }}>
              Document Type
            </Typography>
            {editingField === 'document_type' ? (
              <>
                <TextField
                  value={fieldValue}
                  onChange={e => setFieldValue(e.target.value)}
                  size="small"
                  sx={{ flexGrow: 1, minWidth: 250, maxWidth: 350 }}
                />
                <Button onClick={() => handleSave('document_type')} size="small" variant="contained" disabled={loading} sx={{ ml: 1, whiteSpace: 'nowrap' }}>Save</Button>
                <Button onClick={handleCancel} size="small" variant="outlined" disabled={loading} sx={{ ml: 1, whiteSpace: 'nowrap' }}>Cancel</Button>
              </>
            ) : (
              <>
                <Typography sx={{ flex: 1 }}>
                  {document.document_content.document_type || 'Unknown'}
                </Typography>
                <Button onClick={() => handleEditClick('document_type', document.document_content.document_type || '')} size="small" variant="outlined">EDIT</Button>
              </>
            )}
          </Box>
        </Grid>

        {/* Display only the specified fields for the current document type */}
        {visibleFields.map(key => renderField(key))}
      </Grid>
    </Paper>
  );
};

export default DocumentFields; 