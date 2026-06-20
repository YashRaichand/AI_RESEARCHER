import pytest

@pytest.mark.anyio
async def test_register(client):
    res = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

@pytest.mark.anyio
async def test_login(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "testpassword123",
        "name": "Login User"
    })
    res = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "testpassword123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()

@pytest.mark.anyio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "password": "correct123",
        "name": "Wrong User"
    })
    res = await client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401

@pytest.mark.anyio
async def test_get_me(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "me@example.com",
        "password": "testpassword123",
        "name": "Me User"
    })
    token = reg.json()["access_token"]
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"

@pytest.mark.anyio
async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert "status" in res.json()
