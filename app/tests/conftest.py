import os
import pytest
from fastapi.testclient import TestClient

import sys
sys.path.append(os.sep.join(sys.path[0].split(os.sep)[:-1]))

# Force LLM_PROVIDER to be caila.io for tests
os.environ["LLM_PROVIDER"] = "caila.io"

from main import app
from config import llm_providers
from test_utils import OpenAiMessageMock, OpenAiChoiceMock, OpenAiRespMock, success_content, violation_content


# Remove logging middleware for tests
app.user_middleware = []
app.middleware = []


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_llm_response():
    async def async_mock():
        return OpenAiRespMock(choices=[
            OpenAiChoiceMock(
                message=OpenAiMessageMock(
                    content=success_content
                )
                )
        ])
    
    return async_mock()

@pytest.fixture
def mock_llm_violation_response():
    async def async_mock():
        return OpenAiRespMock(choices=[
            OpenAiChoiceMock(
                message=OpenAiMessageMock(
                    content=violation_content
                )
                )
        ])
    
    return async_mock()
