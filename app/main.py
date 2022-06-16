from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from fastapi.middleware.cors import CORSMiddleware

# 因為有了alembic package，因此不用此行code來去建立db schema
# models.Base.metadata.create_all(bind=engine)  # Create a table in Postgres, tell sqlalchemy to the SQL

app = FastAPI()

# Request Get method url: "/"
# someone can hit this endpoint via this decorator
# When users send a request to the server, the url will only traverse through all decorators once, finding the first match and stop (return).
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

origins = ["*"]

# CORS
app.add_middleware(
    CORSMiddleware,  # 在所有request進來之前，都會經過這個middleware，並執行一些operation
    allow_origins=origins,  # allowed的origin domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")  # fastAPI Instance.Method("Path")
def root():
    return {"message": "Hello World"}
