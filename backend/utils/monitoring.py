"""Comprehensive logging and monitoring configuration for Fynace application."""
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel
import json

class LogConfig:
    """Configuration for logging."""
    
    # Log levels
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # File logging
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() == "true"
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/app.log")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

def setup_logging():
    """Set up comprehensive logging configuration."""
    from logging.handlers import RotatingFileHandler
    
    # Create logs directory if it doesn't exist
    if LogConfig.LOG_TO_FILE:
        os.makedirs(os.path.dirname(LogConfig.LOG_FILE_PATH), exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(LogConfig.LOG_FORMAT)
    
    # Create handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LogConfig.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler (if enabled)
    if LogConfig.LOG_TO_FILE:
        file_handler = RotatingFileHandler(
            LogConfig.LOG_FILE_PATH,
            maxBytes=LogConfig.LOG_MAX_BYTES,
            backupCount=LogConfig.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(getattr(logging, LogConfig.LOG_LEVEL))
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LogConfig.LOG_LEVEL))
    root_logger.handlers = []  # Clear existing handlers
    
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Set specific loggers to WARNING to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)

class MonitoringEvent(BaseModel):
    """Model for monitoring events."""
    timestamp: datetime
    event_type: str
    user_id: str = None
    action: str
    details: Dict[str, Any] = {}
    success: bool = True

class MonitoringService:
    """Service for application monitoring and metrics."""
    
    def __init__(self):
        self.logger = get_logger("monitoring")
    
    def log_event(self, event: MonitoringEvent):
        """Log a monitoring event."""
        log_data = {
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "user_id": event.user_id,
            "action": event.action,
            "details": event.details,
            "success": event.success
        }
        
        if event.success:
            self.logger.info(f"MONITORING_EVENT: {json.dumps(log_data)}")
        else:
            self.logger.warning(f"MONITORING_EVENT: {json.dumps(log_data)}")
    
    def log_api_call(self, user_id: str, endpoint: str, method: str, success: bool, details: Dict[str, Any] = None):
        """Log an API call event."""
        event = MonitoringEvent(
            timestamp=datetime.now(),
            event_type="api_call",
            user_id=user_id,
            action=f"{method} {endpoint}",
            details=details or {},
            success=success
        )
        self.log_event(event)
    
    def log_transaction_operation(self, user_id: str, operation: str, success: bool, details: Dict[str, Any] = None):
        """Log a transaction operation event."""
        event = MonitoringEvent(
            timestamp=datetime.now(),
            event_type="transaction_operation",
            user_id=user_id,
            action=operation,
            details=details or {},
            success=success
        )
        self.log_event(event)
    
    def log_auth_event(self, user_id: str, event_type: str, success: bool, details: Dict[str, Any] = None):
        """Log an authentication event."""
        event = MonitoringEvent(
            timestamp=datetime.now(),
            event_type="auth_event",
            user_id=user_id,
            action=event_type,
            details=details or {},
            success=success
        )
        self.log_event(event)

# Global monitoring service instance
monitoring_service = MonitoringService()