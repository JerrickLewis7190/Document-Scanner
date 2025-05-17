import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  test('renders document upload section', () => {
    render(<App />);
    const uploadElement = screen.getByText(/Upload Document/i);
    expect(uploadElement).toBeInTheDocument();
  });

  test('renders document history section', () => {
    render(<App />);
    const historyElement = screen.getByText(/Document History/i);
    expect(historyElement).toBeInTheDocument();
  });
});
