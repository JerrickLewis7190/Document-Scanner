import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import ImageResolutionValidator from '../components/ImageResolutionValidator';

// Mock Image implementation for testing
class MockImage {
  width: number;
  height: number;
  onload: Function = () => {};
  onerror: Function = () => {};
  src: string = '';

  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
  }
}

// Setup global Image mock
const originalImage = global.Image;

describe('ImageResolutionValidator', () => {
  const mockValidationCallback = jest.fn();
  
  beforeEach(() => {
    mockValidationCallback.mockClear();
  });

  afterAll(() => {
    // Restore original Image
    global.Image = originalImage;
  });

  test('validates image with sufficient resolution', async () => {
    // Mock high resolution image
    const mockImg = new MockImage(800, 600);
    global.Image = jest.fn(() => mockImg) as any;
    URL.createObjectURL = jest.fn(() => 'test-url');
    URL.revokeObjectURL = jest.fn();

    // Create test file
    const testFile = new File(['dummy content'], 'test.png', { type: 'image/png' });
    
    // Render component
    render(
      <ImageResolutionValidator 
        file={testFile} 
        minWidth={500} 
        minHeight={300}
        onValidationResult={mockValidationCallback}
      />
    );

    // Simulate image load
    setTimeout(() => {
      mockImg.onload();
    }, 0);

    // Check that validation callback was called with true
    await waitFor(() => {
      expect(mockValidationCallback).toHaveBeenCalledWith(true);
    });

    // No error message should be displayed
    expect(screen.queryByText(/resolution too low/i)).not.toBeInTheDocument();
  });

  test('shows error for low resolution image', async () => {
    // Mock low resolution image
    const mockImg = new MockImage(400, 200);
    global.Image = jest.fn(() => mockImg) as any;
    URL.createObjectURL = jest.fn(() => 'test-url');
    URL.revokeObjectURL = jest.fn();

    // Create test file
    const testFile = new File(['dummy content'], 'test.png', { type: 'image/png' });
    
    // Render component
    render(
      <ImageResolutionValidator 
        file={testFile} 
        minWidth={500} 
        minHeight={300}
        onValidationResult={mockValidationCallback}
      />
    );

    // Simulate image load
    setTimeout(() => {
      mockImg.onload();
    }, 0);

    // Check that validation callback was called with false
    await waitFor(() => {
      expect(mockValidationCallback).toHaveBeenCalledWith(false);
    });

    // Error message should be displayed
    await waitFor(() => {
      expect(screen.getByText(/resolution too low \(400x200\)/i)).toBeInTheDocument();
    });
  });

  test('passes PDF files without validation', async () => {
    // Create PDF test file
    const pdfFile = new File(['dummy pdf'], 'test.pdf', { type: 'application/pdf' });
    
    render(
      <ImageResolutionValidator 
        file={pdfFile} 
        minWidth={500} 
        minHeight={300}
        onValidationResult={mockValidationCallback}
      />
    );

    // Check that validation callback was called with true
    await waitFor(() => {
      expect(mockValidationCallback).toHaveBeenCalledWith(true);
    });

    // No error message
    expect(screen.queryByText(/resolution too low/i)).not.toBeInTheDocument();
  });
}); 