import axios from 'axios';
import { logger } from '../utils/logger';

const API_BASE_URL = 'http://localhost:8000/api';

export interface Field {
  field_name: string;
  field_value: string;
  corrected: boolean;
}

export interface Document {
  id: number;
  filename: string;
  document_type: string;
  created_at: string;
  fields: Field[];
}

export interface DocumentClassification {
  document_type: string;
  confidence: number;
}

const api = {
  async uploadDocument(file: File): Promise<Document> {
    logger.debug(`Preparing to upload file: ${file.name}`);
    const formData = new FormData();
    formData.append('file', file);

    try {
      logger.info('Sending document upload request to API');
      const response = await axios.post<Document>(`${API_BASE_URL}/documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      logger.info(`Document uploaded successfully, received ID: ${response.data.id}`);
      return response.data;
    } catch (error) {
      logger.error('Failed to upload document', error);
      throw error;
    }
  },

  async classifyDocument(file: File): Promise<DocumentClassification> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post<DocumentClassification>(`${API_BASE_URL}/classify`, formData);
    return response.data;
  },

  async getDocuments(
    skip: number = 0,
    limit: number = 100
  ): Promise<Document[]> {
    logger.debug('Fetching all documents from API');
    try {
      const response = await axios.get<Document[]>(`${API_BASE_URL}/documents`, {
        params: { skip, limit },
      });
      logger.info(`Retrieved ${response.data.length} documents`);
      return response.data;
    } catch (error) {
      logger.error('Failed to fetch documents', error);
      throw error;
    }
  },

  async getDocument(id: number): Promise<Document> {
    logger.debug(`Fetching document with ID: ${id}`);
    try {
      const response = await axios.get<Document>(`${API_BASE_URL}/documents/${id}`);
      logger.info(`Retrieved document: ${response.data.filename}`);
      return response.data;
    } catch (error) {
      logger.error(`Failed to fetch document with ID: ${id}`, error);
      throw error;
    }
  },

  async deleteDocument(id: number): Promise<void> {
    logger.debug(`Deleting document with ID: ${id}`);
    try {
      await axios.delete(`${API_BASE_URL}/documents/${id}`);
      logger.info(`Document ${id} deleted successfully`);
    } catch (error) {
      logger.error(`Failed to delete document with ID: ${id}`, error);
      throw error;
    }
  },

  async deleteAllDocuments(): Promise<void> {
    logger.debug('Deleting all documents');
    try {
      await axios.delete(`${API_BASE_URL}/documents`);
      logger.info('All documents deleted successfully');
    } catch (error) {
      logger.error('Failed to delete all documents', error);
      throw error;
    }
  }
};

export default api; 