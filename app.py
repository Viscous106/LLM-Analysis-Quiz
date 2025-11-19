"""
Main FastAPI application for automated quiz solving system.
Receives quiz requests, validates secrets, and orchestrates quiz solving.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, HttpUrl, ValidationError
import uvicorn

from config import settings
from quiz_solver import QuizSolver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quiz_solver.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global quiz solver instance
quiz_solver: Optional[QuizSolver] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    global quiz_solver
    logger.info("Starting up quiz solver application...")
    quiz_solver = QuizSolver()
    await quiz_solver.initialize()
    yield
    logger.info("Shutting down quiz solver application...")
    await quiz_solver.cleanup()


app = FastAPI(
    title="LLM Quiz Solver API",
    description="Automated quiz solving system for data analysis tasks",
    version="1.0.0",
    lifespan=lifespan
)


class QuizRequest(BaseModel):
    """Request model for incoming quiz requests."""
    email: EmailStr
    secret: str
    url: HttpUrl

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "secret": "my-secret-key",
                "url": "https://example.com/quiz-834"
            }
        }


class QuizResponse(BaseModel):
    """Response model for quiz request acknowledgment."""
    status: str
    message: str
    received_at: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "LLM Quiz Solver",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "quiz_solver_ready": quiz_solver is not None,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/quiz")
async def receive_quiz(request: Request) -> JSONResponse:
    """
    Receive and process quiz requests.

    Validates the secret, then asynchronously solves the quiz.
    Returns 200 if valid, 400 for invalid JSON, 403 for invalid secret.
    """
    try:
        # Parse JSON payload
        try:
            payload = await request.json()
        except Exception as e:
            logger.warning(f"Invalid JSON received: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Validate payload structure
        try:
            quiz_request = QuizRequest(**payload)
        except ValidationError as e:
            logger.warning(f"Invalid request structure: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid request structure: {str(e)}")

        # Validate secret
        if quiz_request.secret != settings.SECRET:
            logger.warning(f"Invalid secret provided for email: {quiz_request.email}")
            raise HTTPException(status_code=403, detail="Invalid secret")

        logger.info(f"Valid quiz request received from {quiz_request.email} for URL: {quiz_request.url}")

        # Start quiz solving asynchronously (don't wait for completion)
        asyncio.create_task(
            quiz_solver.solve_quiz_chain(
                email=quiz_request.email,
                secret=quiz_request.secret,
                initial_url=str(quiz_request.url)
            )
        )

        # Return immediate acknowledgment
        response = QuizResponse(
            status="accepted",
            message="Quiz request accepted and processing started",
            received_at=datetime.utcnow().isoformat()
        )

        return JSONResponse(
            status_code=200,
            content=response.model_dump()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing quiz request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
        reload=settings.DEBUG
    )
