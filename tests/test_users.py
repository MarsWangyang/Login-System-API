from cgi import test
from jose import jwt
import pytest
from app import schemas
from app.config import settings


def test_root(client):
    res = client.get("/")
    # 如果只有res的話，就只會有Response的HTTP status code，若要有詳細的payload, 就加上.json()
    print(res.json())
    print(res.json().get("message"))
    assert res.json().get("message") == 'Hello World!!!'
    assert res.status_code == 200


def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "testmail@gmail.com", "password": "testpassword"})
    # 特別注意這邊所post的prefix是"/users/"，而不是"/users"
    # 當run code會發現，post '/users' 會出現Temp Redirect 307, 然後才變成/users/ 201 Created
    # 當我們不是用API_prefix的方式建立我們的api的時候，可以以不用理會/xxx/的testing issues

    # print(res.json())
    # 要unpack the dictionary, 變成right format for UserOut model, 這邊直接利用pydantic來去做是否有UserOut裏面數值的初步檢查
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "testmail@gmail.com"
    # assert res.json().get("email") == "testmail@gmail.com"
    assert res.status_code == 201


def test_login_users(client, test_user):
    res = client.post("/login", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })

    login_res = schemas.Token(**res.json())  # validate the token
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])
    id: str = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", "testpassword", 403),
    ("testemail@gmail.com", "wrongpassword", 403),
    ("wrongemail@gmail.com", "wrongpassword", 403),
    (None, "password", 422),
    ("testemail@gmail.com", None, 422)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", data={
        "username": email,
        "password": password
    })

    assert res.status_code == status_code
    # assert res.json().get("detail") == "Invalid Credentials"
