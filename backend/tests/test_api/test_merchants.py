"""
Test merchant API endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_merchant(client: AsyncClient, sample_merchant_data):
    """Test merchant registration"""
    response = await client.post("/api/v1/auth/register", json=sample_merchant_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == sample_merchant_data["email"]
    assert "merchant_id" in data


@pytest.mark.asyncio
async def test_login(client: AsyncClient, sample_merchant_data):
    """Test merchant login"""
    # Register first
    await client.post("/api/v1/auth/register", json=sample_merchant_data)
    
    # Login
    login_data = {
        "email": sample_merchant_data["email"],
        "password": sample_merchant_data["password"]
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
