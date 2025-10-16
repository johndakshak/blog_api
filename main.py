from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI(title="My FastAPI")

db = {}
id = 0
 
class Blog(BaseModel):
    title: str
    content: str
    author: str
    updated_time: datetime

class UpdateBlog(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None


#Home
@app.get("/")
def index():
    return {
        "message": "Welcome to our FastAPI"
    }

#Create Blog
@app.post("/blog", status_code=status.HTTP_201_CREATED)
def create_blogs(blogg: Blog):
    if not blogg.title or not blogg.content or not blogg.author:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="At least one field is empty"
        )
    
    global id
    id += 1
    new_blog = {
        "title": blogg.title,
        "content": blogg.content,
        "author": blogg.author,
        "updated_time": datetime.utcnow()
    }

    db[id] = new_blog
    return {
        "message": "Blog created successfully",
        "data": new_blog
    }

#Read a singular Post
@app.get("/blog{id}", status_code=status.HTTP_200_OK)
def get_blog_post(id: int):
    for post in db:
        if post == id:
            return {
                "message": "Singular Post",
                "title": db[id]["title"],
                "content": db[id]["content"],
                "author": db[id]["author"]
            }
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No post for the selected Id"
    )

#Update Blog
@app.patch("/blog{id}", status_code=status.HTTP_200_OK)
def update_blog(id: int, update_blog: UpdateBlog):
    for blog in db:
        if blog == id:
            if update_blog.title != None:
                db[blog]["title"] = update_blog.title

            if update_blog.content != None:
                db[blog]["content"] = update_blog.content

            if update_blog.author != None:
                db[blog]["author"] = update_blog.author
    
            return {
                "message": "Blog updated successfully",
                "data": db
            }
    
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            details= "Id does not exist!"
        )
    
#Delete a Post
@app.delete("/blog/{id}")
def delete_post(id: int):
    for post in db:
        if db[post] == id:
            del db[id]

        return {
            "message": f"Post ID: {id} Deleted Successfully!"
        }
    
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Post Deleted"
    )
