# 🖥️ Document Scanner Frontend

A React + TypeScript application for scanning, viewing, and editing extracted information from immigration documents.

## 🚀 Features

- **Document Upload**: Intuitive interface for uploading document images
- **Document Viewing**: View scanned documents with extracted information
- **Field Editing**: Edit and correct extracted information
- **Document History**: Browse previously processed documents
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Tech Stack

- **React 18**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Material UI**: Component library for clean, modern UI
- **Axios**: HTTP client for API communication
- **React Dropzone**: File upload functionality

## 📂 Project Structure

```
frontend/
├── public/                # Static assets
├── src/
│   ├── components/        # React components
│   │   ├── DocumentCard/  # Document history card
│   │   ├── DocumentList/  # Document history list
│   │   ├── DocumentView/  # Document viewer component
│   │   ├── FieldEditor/   # Field editing interface
│   │   ├── Header/        # Application header
│   │   └── UploadForm/    # Document upload form
│   ├── services/          # API services
│   │   └── api.ts         # API client
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts       # Shared type definitions
│   ├── utils/             # Utility functions
│   │   └── logger.ts      # Logging utility
│   ├── App.tsx            # Main application component
│   └── index.tsx          # Application entry point
├── package.json           # Project dependencies
└── tsconfig.json          # TypeScript configuration
```

## 🛠️ Setup & Installation

### System Requirements

Before setting up the frontend, ensure you have the following installed:

- **Node.js**: Version 16.x or higher
  - [Download Node.js](https://nodejs.org/)
  - Verify installation: `node --version`
  - npm (comes bundled with Node.js) or yarn: `npm --version` / `yarn --version`

- **Git**: Required for version control
  - [Download Git](https://git-scm.com/downloads)
  - Verify installation: `git --version`

- **Modern Web Browser**:
  - Chrome, Firefox, Edge, or Safari (latest versions recommended)
  - For development, Chrome DevTools or Firefox Developer Edition are recommended

### Installation Steps

1. Install dependencies:
   ```sh
   npm install
   ```

2. Configure environment:
   Create a `.env` file in the root directory with:
   ```
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```

3. Start the development server:
   ```sh
   npm start
   ```

4. Access the application at http://localhost:3000

## 📊 Application Flow

1. **Document Upload**:
   - User uploads a document image via the upload form
   - Frontend sends the image to the backend API
   - Backend processes the image and returns extracted information
   - Frontend displays the document with extracted fields

2. **Document Viewing**:
   - User can view the original document image
   - Extracted fields are displayed alongside the image
   - Fields are highlighted based on confidence level

3. **Field Editing**:
   - User can edit any extracted field
   - Changes are validated in real-time
   - Updated fields are saved to the backend

4. **Document History**:
   - User can browse previously processed documents
   - Click on a document to view its details and make changes

## 🧩 Key Components

### UploadForm
Handles document upload and initial processing. Uses React Dropzone for drag-and-drop functionality.

### DocumentView
Displays the document image alongside extracted information. Includes zoom and pan functionality.

### FieldEditor
Provides interface for editing extracted fields with validation.

### DocumentList
Displays a history of processed documents with search and filter capabilities.

## 🔌 API Integration

The frontend communicates with the backend via the API service defined in `src/services/api.ts`. Key endpoints:

- `POST /api/documents` - Upload and process documents
- `GET /api/documents` - Fetch document history
- `PATCH /api/documents/{id}` - Update extracted fields

## 🧪 Testing

Run the test suite:
```sh
npm test
```

Run tests with coverage:
```sh
npm test -- --coverage
```

## 🏗️ Building for Production

Build the application for production:
```sh
npm run build
```

The build artifacts will be stored in the `build/` directory.

## 🔍 Debugging

The application includes a logging utility in `src/utils/logger.ts` that can be used for debugging:

```typescript
import { logger } from '../utils/logger';

// Log at different levels
logger.info('Information message');
logger.warn('Warning message');
logger.error('Error message', error);
```

## 🎨 Customization

### Theme Customization
The Material UI theme can be customized in `src/theme.ts`.

### Adding New Field Types
To add support for new field types:

1. Update the `Field` type in `src/types/index.ts`
2. Add validation rules in `src/utils/validation.ts`
3. Update the field display component in `src/components/FieldEditor`
