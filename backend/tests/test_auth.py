"""Auth endpoint tests."""
import pytest


class TestAuth:
    def test_register(self, client):
        res = client.post("/api/v1/auth/register", json={"email": "new@test.com", "name": "New User", "password": "password123"})
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "new@test.com"

    def test_register_duplicate_email(self, client, admin_user):
        res = client.post("/api/v1/auth/register", json={"email": "admin@test.com", "name": "Dup", "password": "password123"})
        assert res.status_code == 400

    def test_register_short_password(self, client):
        res = client.post("/api/v1/auth/register", json={"email": "x@test.com", "name": "X", "password": "short"})
        assert res.status_code == 400

    def test_login(self, client, admin_user):
        res = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "admin123"})
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_login_wrong_password(self, client, admin_user):
        res = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "wrong"})
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "password123"})
        assert res.status_code == 401

    def test_me(self, client, admin_headers, admin_user):
        res = client.get("/api/v1/auth/me", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["email"] == "admin@test.com"

    def test_me_no_token(self, client):
        res = client.get("/api/v1/auth/me")
        assert res.status_code in (401, 403)

    def test_refresh(self, client, admin_user):
        login = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "admin123"})
        rt = login.json()["refresh_token"]
        res = client.post("/api/v1/auth/refresh", json={"refresh_token": rt})
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_list_users_admin(self, client, admin_headers):
        res = client.get("/api/v1/auth/users", headers=admin_headers)
        assert res.status_code == 200
        assert "users" in res.json()

    def test_list_users_viewer_denied(self, client, viewer_headers):
        res = client.get("/api/v1/auth/users", headers=viewer_headers)
        assert res.status_code == 403

    def test_update_profile(self, client, analyst_headers):
        res = client.put("/api/v1/auth/profile", headers=analyst_headers, json={"name": "Updated"})
        assert res.status_code == 200
        assert res.json()["name"] == "Updated"

    def test_change_password(self, client, analyst_headers):
        res = client.post("/api/v1/auth/change-password", headers=analyst_headers, json={"current_password": "analyst123", "new_password": "newpass123"})
        assert res.status_code == 200

    def test_change_password_wrong_current(self, client, analyst_headers):
        res = client.post("/api/v1/auth/change-password", headers=analyst_headers, json={"current_password": "wrong", "new_password": "newpass123"})
        assert res.status_code == 401
