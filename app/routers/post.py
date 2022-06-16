from sqlalchemy import func
from .. import models, schemas, oath2
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


# 這邊需要變成List，才可以把所有的posts給呈現出來
# @router.get("/", response_model=List[schemas.Post])
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    '''
    limit: 限制只有多少數量 -> limit()
    skip: 要跳過多少數量 -> offet()
    search: Optional, 查詢是否有任何specific string contain in the title of all the posts -> filter()
    '''
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()
    # print(posts)

    # posts = db.query(models.Post).filter(models.Post.title.contains(
    #     search)).limit(limit).offset(offset=skip).all()

    # posts = db.query(models.Post).filter(
    #     models.Post.owner_id == current_user.id).all()

    # join operation (LEFT OUTER JOIN) -> But the default of the sqlalchemy is INNER JOIN
    # SQL: SELECT *, COUNT(votes.post_id) AS votes FROM posts LEFT (OUTER) JOIN votes ON posts.id=votes.post_id GROUP BY posts.id
    posts = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(
        models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(
            search)).limit(limit).offset(offset=skip).all()

    return posts


# when you create something, you must return 201
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
# It will extract the data in Body and transfer to Python dictionary, and throw into "payLoad"
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    # Bad Way:
    # cursor.execute(f"""INSERT INTO posts (title, content, published) VALUES ({post.title}, {post.content}, {post.published})""")
    # 以上的做法有可能會造成SQL Injection: 也就是說如果今天使用者輸入的資料是一個SQL語法，那麼就很有可能可以直接對我們的資料庫進行操控刪除，
    # 因此不建議用直接把資料丟進去我們的code當中，一定要經由variable的方式去進行

    # 但以下這種做法可以讓psycopg2經過verify說沒有SQL Injection以後，才進行動作. (Automatically eliminate the risk)
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",  # %s: represent for a variable
    #     (post.title, post.content, post.published))  # real data
    # new_post = cursor.fetchone()

    # push all change to the database (IMPORTANT!!!)
    # conn.commit()
    # Turn into dictionary format and pack into a dict to match automatically
    # same as title=post.title, content=post.content, etc.

    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
# Directly change parameters into integer (validate the input parameters must be a integer)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    # print(f"Type of id: {type(id)}") # From request, the "id" here is a <class 'str'>
    # print(id)
    # cursor.execute("""SELECT * FROM posts WHERE id=%s """ %
    #                (str(id)))  # need "id" to be string as well
    # print("==========")
    # post = cursor.fetchone()

    # 這邊因為我們知道"id" is unqiue, so there is no need to run .all() to waste the time to search for other questions.
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(
        models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id: {id} was not found."}
        # ===== use HTTPException to replace with =====
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

     # if the user now get a post is not the actual post owner, and then raise Exception
    if post.Post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING *""" % (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()  # cuz we delete (change) the data in database
    # deleting post
    # find the index in the array that has required ID
    # my_posts.pop(index)
    # index = find_index_post(id)

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist.")

    # if the user now delete the post is not the actual post owner, and then raise Exception
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

    # when you delete something, we don't want you to send anything back except for HTTP status code
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
    #                (post.title, post.content, post.published, str(id)))

    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    # if the user now update the post is not the actual post owner, and then raise Exception
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
