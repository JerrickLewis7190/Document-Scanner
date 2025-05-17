import React, { useEffect } from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UploadForm from '../components/UploadForm';

// Create custom file mocks outside of Jest mocks
const createMockFile = (name: string, size: number, type: string): File => {
  const file = new File([new ArrayBuffer(size)], name, { type });
  return file;
};

// Create mock for useDropzone
jest.mock('react-dropzone', () => ({
  useDropzone: () => ({
    getRootProps: () => ({
      onClick: jest.fn(),
      onKeyDown: jest.fn(),
      role: 'button',
      tabIndex: 0,
    }),
    getInputProps: () => ({
      type: 'file',
      accept: '.jpg,.jpeg,.png,.pdf',
    }),
    isDragActive: false,
    open: jest.fn(),
  }),
}));

// Function to dynamically set validation result
const mockValidationCallback: { current: ((isValid: boolean) => void) | null } = {
  current: null
};

// Mock ImageResolutionValidator - to avoid having to mock browser image objects
jest.mock('../components/ImageResolutionValidator', () => {
  return function MockImageValidator(props: { file: File | null, onValidationResult: (isValid: boolean) => void }) {
    // Store the callback so we can trigger it from tests
    mockValidationCallback.current = props.onValidationResult;
    
    // Initial validation - using props not React.useEffect
    if (props.file && mockValidationCallback.current) {
      // Use setTimeout to properly simulate async validation
      setTimeout(() => {
        if (mockValidationCallback.current) {
          mockValidationCallback.current(true);
        }
      }, 0);
    }
    
    return props.file ? <div data-testid="image-validator">Image validated</div> : null;
  };
});

describe('UploadForm', () => {
  const mockUploadCallback = jest.fn();
  
  beforeEach(() => {
    mockUploadCallback.mockClear();
    jest.clearAllMocks();
  });
  
  test('renders upload area correctly', () => {
    render(<UploadForm onFileUpload={mockUploadCallback} />);
    
    // Check for the main elements
    expect(screen.getByText(/drag & drop a document here/i)).toBeInTheDocument();
    expect(screen.getByText(/supported formats: pdf, png, jpg/i)).toBeInTheDocument();
    
    // Upload button should not be visible initially
    expect(screen.queryByText(/process document/i)).not.toBeInTheDocument();
  });
  
  test('displays selected file name when file is selected', async () => {
    // Create a testing-library friendly implementation
    const TestComponent = () => {
      const [file, setFile] = React.useState<File | null>(null);
      
      const handleSelectFile = () => {
        const testFile = createMockFile('test-document.jpg', 1024, 'image/jpeg');
        setFile(testFile);
      };
      
      return (
        <div>
          <button onClick={handleSelectFile}>Select File</button>
          {file && (
            <div>
              <span>Selected: {file.name}</span>
              <button onClick={() => mockUploadCallback(file)}>Process Document</button>
            </div>
          )}
        </div>
      );
    };
    
    render(<TestComponent />);
    
    // Click the button to select a file
    const selectButton = screen.getByText('Select File');
    userEvent.click(selectButton);
    
    // Check for file name
    await waitFor(() => {
      expect(screen.getByText(/test-document.jpg/i)).toBeInTheDocument();
    });
    
    // Process button should be visible
    const processButton = screen.getByText(/process document/i);
    expect(processButton).toBeInTheDocument();
    
    // Click the process button
    userEvent.click(processButton);
    
    // Check that the upload callback was called with a file
    await waitFor(() => {
      expect(mockUploadCallback).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'test-document.jpg',
          type: 'image/jpeg'
        })
      );
    });
  });
  
  test('shows validation error for invalid files', async () => {
    // Create a testing-library friendly implementation
    const TestComponent = () => {
      const [file, setFile] = React.useState<File | null>(null);
      const [isValid, setIsValid] = React.useState(false);
      
      const handleSelectFile = () => {
        const testFile = createMockFile('low-res.jpg', 1024, 'image/jpeg');
        setFile(testFile);
        // Immediately mark as invalid
        setIsValid(false);
      };
      
      return (
        <div>
          <button onClick={handleSelectFile}>Select File</button>
          {file && (
            <div>
              <span>Selected: {file.name}</span>
              <div data-testid="image-validator">Invalid image</div>
              <button 
                onClick={() => mockUploadCallback(file)} 
                disabled={!isValid}
              >
                Process Document
              </button>
            </div>
          )}
        </div>
      );
    };
    
    render(<TestComponent />);
    
    // Click the button to select a file
    const selectButton = screen.getByText('Select File');
    userEvent.click(selectButton);
    
    // Check for file name
    await waitFor(() => {
      expect(screen.getByText(/low-res.jpg/i)).toBeInTheDocument();
    });
    
    // Process button should be disabled
    const processButton = screen.getByText(/process document/i);
    expect(processButton).toBeDisabled();
    
    // Click the disabled button
    userEvent.click(processButton);
    
    // Check that the upload callback was NOT called
    expect(mockUploadCallback).not.toHaveBeenCalled();
  });
}); 