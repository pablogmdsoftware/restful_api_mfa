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