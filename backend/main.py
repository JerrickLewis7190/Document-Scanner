from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
import sys
from datetime import datetime

from app.database import engine
from app.models.db_models import Base
from app.api.endpoints import router as api_router

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(logs_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log'))
    ]
)
logger = logging.getLogger(__name__)

# Create database tables
logger.info("Initializing database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

app = FastAPI(
    title="Document Scanner API",
    description="API for scanning and extracting information from immigration documents",
    version="1.0.0"
)

# Configure CORS
logger.info("Configuring CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured successfully")

# Initialize upload directory and mount it for static file serving
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
logger.info(f"Creating upload directory at: {UPLOAD_DIR}")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
logger.info("Upload directory mounted successfully")

# Include API routes
logger.info("Including API routes...")
app.include_router(api_router, prefix="/api")
logger.info("API routes included successfully")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Document Scanner API server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    ) 