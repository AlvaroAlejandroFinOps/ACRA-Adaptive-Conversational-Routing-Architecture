"""
ACRA Structured Logger: Emits standardized JSON log events with correlation IDs,
timing benchmarks, component namespaces, and automated secret redaction.
"""

import json
import logging
import time
import sys
import uuid
from typing import Dict, Any, Optional

from .payload_policy import PayloadPolicyGate


class ACRAJsonFormatter(logging.Formatter):
    """Formateador de logs en formato JSON estructurado listo para observabilidad en la nube."""

    def format(self, record: logging.LogRecord) -> str:
        log_event = {
            "timestamp": self.formatTime(record, self.datefmt),
            "timestamp_epoch": time.time(),
            "level": record.levelname,
            "component": getattr(record, "component", "acra_kernel"),
            "session_id": getattr(record, "session_id", None),
            "correlation_id": getattr(record, "correlation_id", None),
            "message": record.getMessage(),
            "caller": f"{record.filename}:{record.lineno}",
        }
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_event.update(record.extra_data)
        return json.dumps(log_event, ensure_ascii=False)


class ACRALogger:
    """Instancia de logger estructurado para ACRA."""

    def __init__(self, name: str = "acra", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(ACRAJsonFormatter())
            self.logger.addHandler(handler)

        self._sanitizer = PayloadPolicyGate()

    def log(
        self,
        level: int,
        message: str,
        component: str = "core",
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # Sanitizar mensaje para evitar fuga accidental de secretos en logs
        clean_msg = self._sanitizer.sanitize(message)
        cid = correlation_id or str(uuid.uuid4())[:8]

        extra = {
            "component": component,
            "session_id": session_id,
            "correlation_id": cid,
            "extra_data": kwargs,
        }
        self.logger.log(level, clean_msg, extra=extra)

    def info(self, message: str, **kwargs: Any) -> None:
        self.log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self.log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self.log(logging.ERROR, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self.log(logging.DEBUG, message, **kwargs)
