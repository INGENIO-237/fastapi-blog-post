from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

server = FastAPI()

# DB connection
while True:
    try:
        conn = psycopg2.connect(
            database="fastapi_blog",
            user="postgres",
            password="postgres",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Connected to DB")
        break
    except ConnectionError as e:
        time.sleep(2)
        print(e.strerror)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# posts = [
#     {"title": "post 1", "content": "content 1", "id": 1},
#     {"title": "post 2", "content": "content 2", "id": 2},
#     {"title": "post 3", "content": "content 3", "id": 3},
# ]


# def findPost(postId: int):
#     for post in posts:
#         if post["id"] == postId:
#             return post
#     return None


# def findPostIndex(postId: int):
#     for i, p in enumerate(posts):
#         if p["id"] == postId:
#             return i
#     return None


@server.get("/")
def healthCheck():
    return {"message": "Hello world"}


@server.get("/posts", tags=["Posts"])
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data": posts}


@server.post("/posts", status_code=status.HTTP_201_CREATED, tags=["Posts"])
def create_post(post: Post):
    cursor.execute(
        """INSERT INTO posts(title, content, published) VALUES(%s, %s, %s)
        RETURNING * """,
        (post.title, post.content, post.published),
    )

    post = cursor.fetchone()

    conn.commit()

    return {"data": post}


@server.get("/posts/{id}", tags=["Posts"])
def get_post(id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", [str(id)])

    post = cursor.fetchone()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@server.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Posts"])
def delete_post(id: int):
    post = get_post(id)

    cursor.execute("DELETE FROM posts WHERE id=%s", [str(post["id"])])
    conn.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@server.put("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Posts"])
def update_post(id: int, post: Post):
    existingPost = get_post(id)

    cursor.execute(
        """UPDATE posts set title=%s, content=%s, published=%s WHERE id=%s""",
        [post.title, post.content, post.published, str(existingPost["id"])],
    )

    conn.commit()
