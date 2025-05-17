import { Field } from '../services/api';

export interface Document {
    id: number;
    filename: string;
    document_type: string;
    created_at: string;
    updated_at?: string;
    fields: Field[];
    extracted_fields?: Record<string, string>;
}

export interface DocumentResponse {
    id: number;
    document_type: string;
    document_content: Record<string, string>;
    filename: string;
} 