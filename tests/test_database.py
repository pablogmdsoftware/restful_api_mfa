def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200

def test_get_users(client):
    response = client.get("/users")
    assert response.status_code == 200

def test_create_user(client):
    response = client.post(
        "/users",
        json = {
            "mail": "example@gmail.com",
            "name": "name",
            "password": "password"
        }
    )
    assert response.status_code == 200

def test_get_user(client):
    response = client.get("/users/1")
    assert response.status_code == 200

def test_login(client):
    response = client.post(
        "/token",
        data={
            "username": "example@gmail.com",
            "password": "password",
        }
    )
    data = response.json()
    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_user_me(client, access_token):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        )
    assert response.status_code == 200

def test_update_user(client, access_token):
    response = client.patch(
        "/users/1",
        headers={"Authorization": f"Bearer {access_token}"},
        json = {
            "mail": "example@gmail.com",
            "name": "update"
        }
    )
    assert response.status_code == 200

def test_activate_mfa(client, access_token):
    response = client.patch(
        "/users/me/mfa/activate",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

def test_deactivate_mfa(client, access_token):
    response = client.patch(
        "/users/me/mfa/deactivate",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

def test_create_topt(client, access_token):
    response = client.patch(
        "/users/me/topt",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

def test_get_qr(client, access_token):
    response = client.get(
        "/users/me/topt",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

def test_delete_user(client, access_token):
    response = client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200