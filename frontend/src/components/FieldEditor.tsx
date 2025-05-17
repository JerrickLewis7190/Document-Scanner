import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Grid
} from '@mui/material';
import { Field } from '../types';
import { logger } from '../utils/logger';

interface FieldEditorProps {
  fields: Field[];
  onSave: (fields: Field[]) => void;
  loading?: boolean;
}

const FieldEditor: React.FC<FieldEditorProps> = ({
  fields = [],
  onSave,
  loading = false
}) => {
  const [editedFields, setEditedFields] = useState<Field[]>([]);

  useEffect(() => {
    if (fields && fields.length > 0) {
      setEditedFields(fields);
    }
  }, [fields]);

  const handleFieldChange = (fieldName: string, value: string) => {
    logger.debug(`Editing field: ${fieldName} with value: ${value}`);
    setEditedFields(prev =>
      prev.map(field =>
        field.field_name === fieldName
          ? { ...field, field_value: value, corrected: true }
          : field
      )
    );
  };

  const handleSave = () => {
    logger.info('Saving edited fields');
    onSave(editedFields);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  if (!fields || fields.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography color="textSecondary">
          No fields available for editing
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Grid container spacing={2}>
        {editedFields.map((field) => (
          <Grid item xs={12} key={field.field_name}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography
                variant="body1"
                component="label"
                htmlFor={field.field_name}
                sx={{ minWidth: '120px', fontWeight: 'medium' }}
              >
                {field.field_name.split('_').map((word: string) =>
                  word.charAt(0).toUpperCase() + word.slice(1)
                ).join(' ')}
              </Typography>
              <TextField
                id={field.field_name}
                fullWidth
                variant="outlined"
                size="small"
                value={field.field_value || ''}
                onChange={(e) => handleFieldChange(field.field_name, e.target.value)}
                InputProps={{
                  endAdornment: field.corrected && (
                    <Typography
                      variant="caption"
                      color="primary"
                      sx={{ ml: 1 }}
                    >
                      Edited
                    </Typography>
                  ),
                }}
              />
            </Box>
          </Grid>
        ))}
      </Grid>

      <Box mt={3} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          disabled={loading || editedFields.length === 0}
        >
          Save Changes
        </Button>
      </Box>
    </Box>
  );
};

export default FieldEditor; 