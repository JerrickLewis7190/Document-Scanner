import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import HistorySidebar from '../components/HistorySidebar';
import { Document } from '../types';

// Mock data
const mockDocuments: Document[] = [
  {
    id: 1,
    file_name: 'passport.jpg',
    file_path: '/uploads/passport.jpg',
    document_type: 'passport',
    created_at: '2023-01-15T12:00:00',
    document_content: { 
      passport_number: 'ABC123',
      license_number: '',
      first_name: '',
      last_name: '',
      date_of_birth: '', 
      expiration_date: '',
      issue_date: ''
    },
    image_url: '/uploads/passport.jpg'
  },
  {
    id: 2,
    file_name: 'drivers_license.jpg',
    file_path: '/uploads/drivers_license.jpg',
    document_type: 'drivers_license',
    created_at: '2023-01-20T14:30:00',
    document_content: { 
      license_number: 'XYZ789',
      passport_number: '',
      first_name: '',
      last_name: '',
      date_of_birth: '',
      expiration_date: '',
      issue_date: ''
    },
    image_url: '/uploads/drivers_license.jpg'
  }
];

describe('HistorySidebar', () => {
  const mockSelectDocument = jest.fn();
  const mockDeleteDocument = jest.fn();
  
  beforeEach(() => {
    mockSelectDocument.mockClear();
    mockDeleteDocument.mockClear();
  });
  
  test('renders document list correctly', () => {
    render(
      <HistorySidebar 
        documents={mockDocuments} 
        selectedDocumentId={undefined}
        onDocumentSelect={mockSelectDocument}
        onDocumentDelete={mockDeleteDocument}
      />
    );
    
    // Check title is displayed
    expect(screen.getByText(/recent extractions/i)).toBeInTheDocument();
    
    // Check both documents are listed
    expect(screen.getByText('passport.jpg')).toBeInTheDocument();
    expect(screen.getByText('drivers_license.jpg')).toBeInTheDocument();
    
    // Check document types are formatted
    expect(screen.getByText('Passport')).toBeInTheDocument();
    expect(screen.getByText('Drivers License')).toBeInTheDocument();
  });
  
  test('selecting a document triggers callback', async () => {
    render(
      <HistorySidebar 
        documents={mockDocuments} 
        selectedDocumentId={undefined}
        onDocumentSelect={mockSelectDocument}
        onDocumentDelete={mockDeleteDocument}
      />
    );
    
    // Click on the first document
    const firstDocument = screen.getByText('passport.jpg');
    userEvent.click(firstDocument);
    
    // Check callback was called with correct document
    await waitFor(() => {
      expect(mockSelectDocument).toHaveBeenCalledWith(mockDocuments[0]);
    });
  });
  
  test('deleting a document triggers callback', async () => {
    render(
      <HistorySidebar 
        documents={mockDocuments} 
        selectedDocumentId={undefined}
        onDocumentSelect={mockSelectDocument}
        onDocumentDelete={mockDeleteDocument}
      />
    );
    
    // Find and click the delete button for the second document
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    userEvent.click(deleteButtons[1]); // Second delete button
    
    // Check callback was called with correct ID
    await waitFor(() => {
      expect(mockDeleteDocument).toHaveBeenCalledWith(2);
    });
  });
  
  test('shows selected document as active', () => {
    const { container } = render(
      <HistorySidebar 
        documents={mockDocuments} 
        selectedDocumentId={2}
        onDocumentSelect={mockSelectDocument}
        onDocumentDelete={mockDeleteDocument}
      />
    );
    
    // Find all document items - use role='button' since ListItemButton has this role
    const listButtons = screen.getAllByRole('button').filter(button => !button.getAttribute('aria-label'));
    
    // Check that the second item has the Mui-selected class (MUI adds this class to selected ListItemButton)
    expect(listButtons[1]).toHaveClass('Mui-selected');
    expect(listButtons[0]).not.toHaveClass('Mui-selected');
    
    // Check if the text is bold - MUI uses font-weight: 700 for bold 
    const secondItemText = screen.getByText('drivers_license.jpg');
    const fontWeight = window.getComputedStyle(secondItemText).getPropertyValue('font-weight');
    expect(['bold', '700']).toContain(fontWeight);
  });
  
  test('displays empty state when no documents exist', () => {
    render(
      <HistorySidebar 
        documents={[]} 
        selectedDocumentId={undefined}
        onDocumentSelect={mockSelectDocument}
        onDocumentDelete={mockDeleteDocument}
      />
    );
    
    // Check empty state message is displayed
    expect(screen.getByText(/no documents processed yet/i)).toBeInTheDocument();
  });
}); 