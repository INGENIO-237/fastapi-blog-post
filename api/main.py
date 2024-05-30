from typing import Optional
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from random import randrange

server = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


posts = [
    {"title": "post 1", "content": "content 1", "id": 1},
    {"title": "post 2", "content": "content 2", "id": 2},
    {"title": "post 3", "content": "content 3", "id": 3},
]


def findPost(postId: int):
    for post in posts:
        if post["id"] == postId:
            return post
    return None


def findPostIndex(postId: int):
    for i, p in enumerate(posts):
        if p["id"] == postId:
            return i
    return None


@server.get("/")
def healthCheck():
    return {"message": "Hello world"}


@server.get("/posts", tags=["Posts"])
def get_posts():
    return {"data": posts}


@server.post("/posts", status_code=status.HTTP_201_CREATED, tags=["Posts"])
def create_post(post: Post):
    post = post.model_dump()
    post["id"] = randrange(0, 1e6)
    posts.append(post)
    return {"data": post}


@server.get("/posts/{id}", tags=["Posts"])
def get_post(id: int):
    post = findPost(id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@server.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT,
               tags=["Posts"])
def delete_post(id: int):
    index = findPostIndex(id)

    print(index)

    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@server.put("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT,
            tags=["Posts"])
def update_post(id: int, post: Post):
    index = findPostIndex(id)

    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist",
        )

    posts[index] = post.model_dump()
