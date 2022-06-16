from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    ''' A Pydanic Model that can automatically validate the variable'''
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    '''Exactly same as PostBase. Will inherit the PostBase'''
    pass


class Post(PostBase):
    '''Response model => to filter out the data that we don't want to display to the users'''
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut  # 利用models當中所使用sqlalchemy.orm.relationship的方式，讓owner這個pydantic model可以傳入UserOut，並且把所有User相關的資訊print出來

    # 現在是Pydantic model，需要轉換成為sqlalchemy model才可以執行(using Config)
    class Config:
        '''orm_mode will tell the Pydanic model to read the data even if it is not a dict, but an ORM model or any other arbitrary object with attributes'''
        orm_mode = True


class PostOut(BaseModel):
    # You have to inherit BaseModel instead of PostBase,
    # because Pydantic was expecting all the members of the class PostBase to be present in the object returned by the API.
    Post: Post
    votes: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)  # 進來的數字需要大小比1小，不可以超過，但這樣negative也可以，因此用boolean來表示會最好
