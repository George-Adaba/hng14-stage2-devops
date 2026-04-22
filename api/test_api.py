import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app


@pytest.fixture
def client():
    """Fixture to create TestClient - instantiated during test execution"""
    return TestClient(app=app)


@pytest.fixture
def mock_redis():
    """Fixture to mock Redis connection"""
    with patch('main.r') as mock:
        yield mock


def test_health(client, mock_redis):
    """Test health endpoint returns 200 with status healthy"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_job(client, mock_redis):
    """Test job creation returns job_id and calls Redis operations"""
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1
    
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) > 0
    
    # Verify Redis operations were called
    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called()


def test_get_job_not_found(client, mock_redis):
    """Test getting non-existent job returns 404"""
    mock_redis.hget.return_value = None
    
    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 404
    assert "error" in response.json()
    assert "not found" in response.json()["error"].lower()


def test_get_job_found(client, mock_redis):
    """Test getting existing job returns status"""
    job_id = "test-job-123"
    mock_redis.hget.return_value = "completed"
    
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "completed"


def test_redis_error_on_job_creation(client, mock_redis):
    """Test Redis error during job creation returns 503"""
    import redis
    mock_redis.lpush.side_effect = redis.RedisError("Connection refused")
    
    response = client.post("/jobs")
    assert response.status_code == 503
    assert "error" in response.json()
    assert "unavailable" in response.json()["error"].lower()


def test_redis_error_on_get_job(client, mock_redis):
    """Test Redis error when retrieving job returns 503"""
    import redis
    mock_redis.hget.side_effect = redis.RedisError("Redis timeout")
    
    response = client.get("/jobs/some-id")
    assert response.status_code == 503
    assert "error" in response.json()
