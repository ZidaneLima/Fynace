from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from backend.utils.logging import setup_logging
from backend.utils.monitoring import monitoring_service
from backend.config_modules.security_config import setup_security_headers, setup_rate_limiting, get_security_config
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()
# Setup logging before creating the app
setup_logging()

from backend.routes import transacoes, resumo, pagamentos
from backend.auth_utils import get_current_user

logger = logging.getLogger(__name__)

# Create FastAPI app with security considerations
app = FastAPI(
    title=os.getenv("APP_NAME", "Fynace"),
    description="Fynace - Sistema de Finanças Pessoais com integração Google Sheets",
    version="1.0.0",
    # Don't expose sensitive information in docs in production
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Setup security configurations
setup_security_headers(app)
# setup_rate_limiting(app)  # Uncomment when slowapi is installed

# Add middleware for request logging and monitoring
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Get user ID if available (from JWT token)
    user_id = "unknown"
    try:
        # Try to extract user ID from the authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, you would decode the JWT to get the user ID
            # For now, we'll just log that there's an auth header
            user_id = "authenticated_user"
    except:
        pass

    # Log the incoming request
    monitoring_service.log_api_call(
        user_id=user_id,
        endpoint=request.url.path,
        method=request.method,
        success=True,
        details={
            "client_host": request.client.host,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "content_type": request.headers.get("content-type", "unknown")
        }
    )

    response = await call_next(request)

    process_time = time.time() - start_time

    # Add process time to response headers
    response.headers["X-Process-Time"] = str(process_time)

    # Apply security headers to response
    from backend.utils.security import SecurityMiddleware
    response = SecurityMiddleware.add_security_headers(response)

    # Log the response
    from backend.utils.monitoring import MonitoringEvent
    from datetime import datetime
    monitoring_service.log_event(
        MonitoringEvent(
            timestamp=datetime.now(),
            event_type="api_response",
            user_id=user_id,
            action=f"{request.method} {request.url.path}",
            details={
                "status_code": response.status_code,
                "process_time": process_time
            },
            success=response.status_code < 400
        )
    )

    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for logging errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    # Log the error in monitoring
    from backend.utils.monitoring import MonitoringEvent
    from datetime import datetime
    monitoring_service.log_event(
        MonitoringEvent(
            timestamp=datetime.now(),
            event_type="error",
            user_id="unknown",
            action=f"{request.method} {request.url.path}",
            details={
                "error": str(exc),
                "error_type": type(exc).__name__
            },
            success=False
        )
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

app.include_router(transacoes.router, prefix="/transacoes", tags=["Transações"])
app.include_router(resumo.router, prefix="/resumo", tags=["Resumo"])
app.include_router(pagamentos.router)

@app.get("/saudez")
def health():
    return {"status": "ok"}

@app.get("/me")
def me(user=Depends(get_current_user)):
    return user
