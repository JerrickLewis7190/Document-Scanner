// Basic interfaces
export interface Field {
  field_name: string;
  field_value: string;
  corrected: boolean;
}

export interface DocumentContent {
  [key: string]: string;
}

export interface Document {
  id: number;
  file_name: string;
  file_path: string;
  document_type: string;
  document_content: DocumentContent;
  created_at: string;
  confidence_score?: number;
  fields?: Field[];
  requires_review?: boolean;
  image_url?: string;
}

export interface DocumentResponse {
  id: number;
  file_name: string;
  file_path: string;
  document_type: string;
  document_content: DocumentContent;
  created_at: string;
  confidence_score?: number;
  requires_review?: boolean;
}

// Define required fields by document type
export const REQUIRED_FIELDS = {
  passport: [
    'full_name', 'date_of_birth', 'country', 'issue_date', 
    'expiration_date'
  ],
  drivers_license: [
    'license_number', 'date_of_birth', 'issue_date', 
    'expiration_date', 'first_name', 'last_name'
  ],
  ead_card: [
    'card_number', 'category', 'first_name', 'last_name', 
    'card_expires_date'
  ]
};

// Helper function to check if a field is required for a document type
export const isRequiredField = (fieldName: string, documentType: string): boolean => {
  const normalizedType = documentType.toLowerCase().replace(' ', '_');
  const requiredFields = REQUIRED_FIELDS[normalizedType as keyof typeof REQUIRED_FIELDS];
  return requiredFields?.includes(fieldName) || false;
}; 