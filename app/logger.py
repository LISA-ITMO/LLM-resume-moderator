import json
import logging
import time

from config import ELASTIC_PASSWORD
from elasticsearch import Elasticsearch
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", ELASTIC_PASSWORD),
    verify_certs=False,
)


class ElasticsearchHandler(logging.Handler):
    def emit(self, record):
        try:
            timestamp = time.strftime(
                "%Y-%m-%dT%H:%M:%S", time.localtime(record.created)
            )

            log_entry = {
                "@timestamp": timestamp,
                "level": record.levelname,
                "service": "moderator-service",
                "method": getattr(record, "method", ""),
                "path": getattr(record, "path", ""),
                "status": getattr(record, "status", 0),
                "duration": getattr(record, "duration", 0),
                "request_headers": json.dumps(getattr(record, "request_headers", {})),
                "request_body": getattr(record, "request_body", ""),
                "response_headers": json.dumps(getattr(record, "response_headers", {})),
                "response_body": getattr(record, "response_body", ""),
            }
            es.index(index="app-logs", document=log_entry)
        except Exception as e:
            print(f"Error sending log to Elasticsearch: {e}")


logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

es_handler = ElasticsearchHandler()
es_handler.setFormatter(formatter)
logger.addHandler(es_handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "request_headers": dict(request.headers),
            "request_body": "",
            "status": 0,
            "duration": 0,
            "response_headers": {},
            "response_body": "",
        }

        try:
            body = await request.body()
            log_data["request_body"] = body.decode(errors="replace") if body else ""
            request._body = body
        except Exception as e:
            log_data["request_body"] = f"Error reading body: {str(e)}"

        try:
            response = await call_next(request)
        except Exception as e:
            log_data.update(
                {
                    "status": 500,
                    "response_body": str(e),
                    "duration": time.time() - start_time,
                }
            )
            logger.error("Request error", extra=log_data)
            raise

        try:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            log_data["response_body"] = response_body.decode(errors="replace")
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        except Exception as e:
            log_data["response_body"] = f"Error reading response: {str(e)}"

        log_data.update(
            {
                "status": response.status_code,
                "response_headers": dict(response.headers),
                "duration": round(time.time() - start_time, 3),
            }
        )

        log_level = logging.INFO
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING

        logger.log(
            log_level,
            "Request processed",
            extra={
                "method": log_data["method"],
                "path": log_data["path"],
                "status": log_data["status"],
                "duration": log_data["duration"],
                "request_headers": log_data["request_headers"],
                "request_body": log_data["request_body"],
                "response_headers": log_data["response_headers"],
                "response_body": log_data["response_body"],
            },
        )

        return response
