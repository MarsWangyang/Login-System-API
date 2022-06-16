# Every Model represent for the table in Database
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)  # ondelete="CASCADE" 表示當owner_id刪除的時候，也會將user.id符合此owner_id的數值給一併刪除

    # 當假設frontend需要呈現給使用者看user_id背後到底是什麼的時後，就會需要再去找User這張表的內容，而不是只有呈現user_id
    # referening the sqlalchemy class (User) instead of the tablename (users)
    # relationship is actually a foreign key but not show in the table (a property)
    # it will fetch the data for us automatically, and developers don't need to fetch by ourselves
    # 在shcema.py裏面，會需要去更改pydantic的Post model，將owner成為UserOut
    owner = relationship("User")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    # Email need to be a unique string
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))


class Votes(Base):
    __tablename__ = "votes"

    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
