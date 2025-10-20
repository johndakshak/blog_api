from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class BlogCategory(str, Enum):
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"

class BlogCreate(BaseModel):
    title: str
    content: str
    author: str
    category: BlogCategory

class Blog(BlogCreate):
    id: int
    created_at: datetime
    updated_at: datetime

class AuthorSummary(BaseModel):
    author: str
    blog_count: int

class CategorySummary(BaseModel):
    category: str
    blog_count: int

from typing import List, Optional

class Database:

    def __init__(self):
        self._blogs: List[Blog] = []
        self._current_id = 1

    def generate_id(self) -> int:
        next_id = self._current_id
        self._current_id += 1
        return next_id

    def add_blog(self, blog: BlogCreate) -> Blog:
        if not blog.title or not blog.content or not blog.author or not blog.category:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="Atleast one field is empty!"
            )
        
        new_blog = Blog(
            title=blog.title,
            content=blog.content,
            author=blog.author,
            category=blog.category,
            id=self._current_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self._blogs.append(new_blog)
        self.generate_id()

        return new_blog

    def get_all_blogs(self) -> List[Blog]:
        if not self._blogs:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="Data is Empty"
            )
        
        return self._blogs
    
    def get_blogs_by_filter(self,
        category: Optional[BlogCategory] = None,
        author: Optional[str] = None,
        keyword: Optional[str] = None
        ):
         
        filtered_blogs: List[Blog] = []

        for blog in self._blogs:
            if category is not None:
                if category in blog.category:
                    filtered_blogs.append(blog)
            
            if author is not None:
                if author in blog.author:
                    filtered_blogs.append(blog)

            if blog.title != None or blog.content != None:
                if keyword != None:
                    if keyword in blog.title or keyword in blog.content:
                        filtered_blogs.append(blog)

        if not filtered_blogs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching Blog found"
            )
        
        return filtered_blogs

    def get_blog_by_id(self, blog_id: int) -> Optional[Blog]:
        for blog in self._blogs:
            if blog.id == blog_id:
                return blog
            
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found!"
        )

    def update_blog(self, blog_id: int, updates: BlogCreate) -> Optional[Blog]:
        for index, blog in enumerate(self._blogs):
            if blog.id == blog_id:
                updated = Blog(
                    title=updates.title,
                    content=updates.content,
                    author=updates.author,
                    category=updates.category,
                    id=blog_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                self._blogs[index] = updated
                return updated
                
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog Id: {blog_id} not found!"
        )
            
    def delete_blog(self, blog_id: int) -> bool:
        for index, blog in enumerate(self._blogs):
            if blog.id == blog_id:
                del self._blogs[index]

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog Id: {blog_id} not found!"
        )

    def get_blogs_by_category(self, category: BlogCategory) -> List[Blog]:

        blog_category = []

        for blog in self._blogs:
            if blog.category == category:
                blog_category.append(blog)
        
        if not blog_category:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog Category: {blog.category} not Found!"
            )
    
        return blog_category
    
    def search_blogs(self, keyword: str) -> List[Blog]:
                
        blogs_list = []
        flag = False

        for blog in self._blogs:
            if keyword in blog.title or keyword in blog.content:
                blogs_list.append(blog)
                flag = True
        else:
            if flag == False:

                return {
                    "message": "No match with Search Param"
                }
        
        return blogs_list

    def get_author_summary(self) -> List[AuthorSummary]:
                
        author_dict = {}

        for blog in self._blogs:
            if blog.author in author_dict:
                author_dict[blog.author] += 1
            
            else:
                author_dict[blog.author] = 1

        author_list = []

        for key, value in author_dict.items():
            summary = AuthorSummary(
                author=key,
                blog_count=value
            )

            author_list.append(summary)

        return author_list

    def get_category_summary(self) -> List[CategorySummary]:
        
        category_dict = {}

        for blog in self._blogs:
            if blog.category in category_dict:
                category_dict[blog.category] += 1
            
            else:
                category_dict[blog.category] = 1

        category_list = []

        for key, value in category_dict.items():
            summary = CategorySummary(
                category=key,
                blog_count=value
            )

            category_list.append(summary)

        return category_list

from fastapi import FastAPI, HTTPException, status
from typing import List, Optional

app = FastAPI(title="Blog Management API")

db = Database()  

@app.post("/blogs", response_model=Blog)
def create_blog(blog: BlogCreate):
    return db.add_blog(blog)

@app.get("/all_blogs")
def get_all_blogs():
    return db.get_all_blogs()

@app.get("/blogs", response_model=List[Blog])
def list_blogs(
    category: Optional[BlogCategory] = None,
    author: Optional[str] = None,
    keyword: Optional[str] = None
    ):

    return db.get_blogs_by_filter(category, author, keyword)

@app.get("/blogs/{blog_id}", response_model=Blog)
def get_blog(blog_id: int):
    return db.get_blog_by_id(blog_id)

@app.put("/blogs/{blog_id}", response_model=Blog)
def update_blog(blog_id: int, updated_blog: BlogCreate):
    return db.update_blog(blog_id, updated_blog)

@app.delete("/blogs/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(blog_id: int):
    return db.delete_blog(blog_id)

@app.get("/blogs_category/category")
def blogs_category(category: BlogCategory):
    return db.get_blogs_by_category(category)

@app.get("/blogs_search/search")
def blogs_search_by_keyword(keyword: str):
    return db.search_blogs(keyword)

@app.get("/summary/authors", response_model=List[AuthorSummary])
def author_summary():
    return db.get_author_summary()

@app.get("/summary/categories", response_model=List[CategorySummary])
def category_summary():
    return db.get_category_summary()
