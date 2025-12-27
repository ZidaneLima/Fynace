"""Security configuration for Fynace application."""
import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

def setup_security_headers(app: FastAPI):
    """Setup security-related configurations for the FastAPI app."""
    
    # CORS middleware - restrict origins in production
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Don't expose sensitive headers
        expose_headers=["X-Process-Time"]
    )
    
    # Trusted host middleware to prevent HTTP Host Header attacks
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

def setup_rate_limiting(app: FastAPI):
    """Setup rate limiting for the application."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def get_security_config():
    """Get security configuration values."""
    return {
        # Security headers
        "SECURE_SSL_REDIRECT": os.getenv("SECURE_SSL_REDIRECT", "false").lower() == "true",
        "SECURE_HSTS_SECONDS": int(os.getenv("SECURE_HSTS_SECONDS", "31536000")),  # 1 year
        "SECURE_HSTS_INCLUDE_SUBDOMAINS": os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "true").lower() == "true",
        "SECURE_CONTENT_TYPE_NOSNIFF": os.getenv("SECURE_CONTENT_TYPE_NOSNIFF", "true").lower() == "true",
        "SECURE_BROWSER_XSS_FILTER": os.getenv("SECURE_BROWSER_XSS_FILTER", "true").lower() == "true",
        "SECURE_CROSS_ORIGIN_EMBEDDER_POLICY": os.getenv("SECURE_CROSS_ORIGIN_EMBEDDER_POLICY", "require-corp"),
        
        # Rate limiting
        "RATE_LIMIT_DEFAULT": os.getenv("RATE_LIMIT_DEFAULT", "100/hour"),
        "RATE_LIMIT_TRANSACTIONS": os.getenv("RATE_LIMIT_TRANSACTIONS", "10/minute"),
        "RATE_LIMIT_AUTH": os.getenv("RATE_LIMIT_AUTH", "5/minute"),
        
        # Input validation
        "MAX_REQUEST_SIZE": int(os.getenv("MAX_REQUEST_SIZE", "1048576")),  # 1MB
        "ALLOWED_FILE_EXTENSIONS": os.getenv("ALLOWED_FILE_EXTENSIONS", "csv,xlsx,pdf").split(","),
        
        # Sensitive data handling
        "ENCRYPT_SENSITIVE_DATA": os.getenv("ENCRYPT_SENSITIVE_DATA", "true").lower() == "true",
        "LOG_SENSITIVE_DATA": os.getenv("LOG_SENSITIVE_DATA", "false").lower() == "true",
    }

# Example of how to apply rate limiting to specific routes
# This would be used in route definitions:
# 
# @limiter.limit("10/minute")
# @app.get("/api/transactions")
# def get_transactions(request: Request):
#     ...