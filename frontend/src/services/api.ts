import axios from 'axios';
import { Document, DocumentResponse, Field } from '../types';
import { logger } from '../utils/logger';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

function convertContentToFields(content: Record<string, string>): Field[] {
  return Object.entries(content)
    .filter(([key]) => key !== 'document_type')
    .map(([field_name, field_value]) => ({
      field_name,
      field_value: field_value || '',
      corrected: false
    }));
}

const api = {
  async getDocuments(): Promise<Document[]> {
    try {
      const response = await axios.get<DocumentResponse[]>(`${API_BASE_URL}/api/documents`);
      return response.data.map((doc) => ({
        ...doc,
        created_at: new Date().toISOString(),
        fields: convertContentToFields(doc.document_content)
      }));
    } catch (error) {
      logger.error('Failed to fetch documents:', error);
      throw error;
    }
  },

  async uploadDocument(file: File): Promise<Document> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post<DocumentResponse>(`${API_BASE_URL}/api/documents`, formData);
      return {
        ...response.data,
        created_at: new Date().toISOString(),
        fields: convertContentToFields(response.data.document_content)
      };
    } catch (error) {
      logger.error('Failed to upload document:', error);
      throw error;
    }
  },

  async updateDocumentFields(documentId: number, fields: Field[]): Promise<Document> {
    try {
      console.log('API: Updating document fields for ID:', documentId);
      console.log('API: Fields to update:', fields);
      
      // Map our Field type to match the expected ExtractedFieldBase schema
      const completeFields = fields.map(field => ({
        field_name: field.field_name,
        field_value: field.field_value,
        confidence_score: 1.0, // Default high confidence for user edits
        needs_correction: false, // User has already corrected it
        error_message: null // No error for user edits
      }));
      
      console.log('API: Sending complete fields:', completeFields);
      
      // Update the request structure to match backend expectations
      const response = await axios.patch<DocumentResponse>(
        `${API_BASE_URL}/api/documents/${documentId}`,
        { fields: completeFields }
      );
      
      console.log('API: Update response:', response.data);
      
      return {
        ...response.data,
        created_at: new Date().toISOString(),
        fields: convertContentToFields(response.data.document_content)
      };
    } catch (error) {
      console.error('API: Error updating document fields:', error);
      logger.error('Failed to update document fields:', error);
      throw error;
    }
  },

  async deleteDocument(documentId: number): Promise<void> {
    try {
      await axios.delete(`${API_BASE_URL}/api/documents/${documentId}`);
    } catch (error) {
      logger.error('Failed to delete document:', error);
      throw error;
    }
  },

  async deleteAllDocuments(): Promise<void> {
    try {
      await axios.delete(`${API_BASE_URL}/api/documents`);
    } catch (error) {
      logger.error('Failed to delete all documents:', error);
      throw error;
    }
  },

  async getDocument(documentId: number): Promise<Document> {
    try {
      console.log('API: Fetching document ID:', documentId);
      
      const response = await axios.get<DocumentResponse>(`${API_BASE_URL}/api/documents/${documentId}`);
      console.log('API: Fetched document:', response.data);
      
      return {
        ...response.data,
        created_at: new Date().toISOString(),
        fields: convertContentToFields(response.data.document_content)
      };
    } catch (error) {
      console.error('API: Error fetching document:', error);
      logger.error('Failed to fetch document:', error);
      throw error;
    }
  }
};

export default api;