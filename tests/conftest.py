# specific file that pytest will user it
# allow us to define the fixture in here
# will automatically accessible in this package: /tests
# You don't need to import anything in your test_*.py file
# 最上層的conftest可以inherit to the next package, e.g. /tests/api，
# 但是/tests/api/conftest.py 就無法讓/tests/裏面的test_*.py做使用

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app
from app import schemas, models
from app.config import settings
from app.database import get_db
from app.database import Base
from app.oath2 import create_access_token

# 需要先確認在.env裡面:
# DATABASE_HOSTNAME = localhost -> 本機運行 (原本是=postgres)
# DATABASE_PORT = 8080  -> docker build (原本是=5432 docker)
# pytest -x 可以在FAIL的時候就直接停下來，不會所有program都需要跑一次


# 我們希望創建出一個for testing database，而不要去連線到development的database
# To connect PostgreSQL for testing
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:admin@localhost:8080/fastapi_test'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

# Engine：用來把sqlalchemy和postgresql做連接
engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def override_get_db():
#     # 當我們在跑testing的時候, 這個function會直接override掉原本在routing裏面Depend(get_db)的function。
#     # Create a session to our database for every request on endpoint
#     db = TestSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# 把所有原先是get_db的Depend，換成用上面override_get_db的function使用作為testing
# app.dependency_overrides[get_db] = override_get_db

# -----------------

# 把client當作requests的使用，直接去做測試
# client = TestClient(app)
# --> 這邊可以利用@pytest.fixture來做替代，因為用這樣的方式變成function，可以多增加logic來對database做一些處理
# --> 因為每次testing都會遇到replicated data已經在database當中，而出現FAILED，因此利用yield來在run test前才創建database，run test完以後馬上drop掉all tables
# @pytest.fixture
# def client():
#     Base.metadata.drop_all(bind=engine)
#     # 利用yield好處(此處為解決上述之事項，testing duplicate data error):
#     # ---run our code before we run our test---
#     # replicate database from origin version directly，也可以利用alembic做migration
#     Base.metadata.create_all(bind=engine)
#     yield TestClient(app)
#     # ---run our code after our test finishes---
#     # -----------------------------------------
#     # ---利用alembic方式來recreate table in database---
#     # command.upgrade("head")
#     # yield TestClient(app)
#     # command.downgrade("base")

# 如果今天想對db直接在testing時也做操作，那麼我們可以利用pytest fixture的inherit來做到此方式
# 但這樣我們的session就會先被建立 (for database operation)，再來才會建立client (for client operation)
# 我們可以在test function的parameters裡面寫上像是：def test_root(client, session): 然後直接在下面使用session.query()...對db做直接操作
# default scope == function ，每一個function就跑一次fixture
@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

# 因為我們我設置原本database裡面的client會因為fixture的scope而無法事先在db裡面有data
# 所以再次寫一個fixture，讓一開始就可以直接設立一個fixture


@pytest.fixture
def test_user(client):
    user_data = {"email": "testmail@gmail.com", "password": "testpassword"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    # {'id': 1, 'email': 'testmail@gmail.com', 'created_at': '2022-07-02T08:01:55.065865+00:00'} -> 沒有password，所以要加上
    print(res.json())
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "testmail2@gmail.com", "password": "testpassword2"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    # {'id': 1, 'email': 'testmail@gmail.com', 'created_at': '2022-07-02T08:01:55.065865+00:00'} -> 沒有password，所以要加上
    print(res.json())
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(test_user):
    # login之後會對create post...等operation有token的限制
    # 但與其use every API through it，不如直接創造一個假的token，可以減少整個testing的時間，也不用go throught all APIs
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    # 利用這個fixture，之後已經被驗證過的client，會自帶bearer token在身上，
    # 我們可以直接call這個function，就可以直接利用client["Authorization"]就可以拿到token
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def test_posts(test_user, session, test_user2):
    # 利用這個fixture可以預先建立好posts做使用
    posts_data = [{
        "title": "1st title",
        "content": "1st content",
        "owner_id": test_user["id"]
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user["id"]
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user["id"]
    },
        {
        "title": "4th title",
        "content": "4th content",
        "owner_id": test_user2["id"]
    }]

    def create_post_model(post):
        return models.Post(**post)

    # map(func, )可以iterate到前面的func
    post_map = map(create_post_model, posts_data)
    posts = list(post_map)

    session.add_all(posts)
    # hardcode的方式(Not Recommend)
    # session.add_all([models.Post(title="first title", content="first content", owner_id=test_user['id'])])

    session.commit()

    posts = session.query(models.Post).all()
    return posts
