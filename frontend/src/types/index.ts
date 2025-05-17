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
    document_content: Record<string, string>;
    fields: Field[];
    image_url: string;
}

export interface DocumentResponse {
    id: number;
    document_type: string;
    document_content: Record<string, string>;
    filename: string;
    image_url: string;
} 