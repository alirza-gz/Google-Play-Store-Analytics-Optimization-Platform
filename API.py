from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, Date, DateTime, Numeric
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import datetime

# ------------------------------------------------------------------------------
# Database configuration
# ------------------------------------------------------------------------------
# Update the connection URL as needed for your PostgreSQL setup.
DATABASE_URL = "postgresql+psycopg2://postgres:Alireza1679@127.0.0.1/GooglePlayData"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models.
Base = declarative_base()


# ------------------------------------------------------------------------------
# ORM Models
# ------------------------------------------------------------------------------

class Category(Base):
    """
    ORM model for the 'categories' table.
    This table contains a single column 'category' which is used as the primary key.
    """
    __tablename__ = "categories"
    category = Column(String, primary_key=True, index=True)


class Developer(Base):
    """
    ORM model for the 'developers' table.
    """
    __tablename__ = "developers"
    developer_id = Column(String, primary_key=True, index=True)
    developer_website = Column(String, nullable=True)
    developer_email = Column(String, nullable=True)


class Application(Base):
    """
    ORM model for the 'applications' table.
    Note: The attribute "privacy_policy_url" is mapped to the actual column "privacy_policy" in the database.
    """
    __tablename__ = "applications"

    app_id = Column(String, primary_key=True, index=True)
    app_name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # References Category table
    rating = Column(Float, nullable=True)
    rating_count = Column(Integer, nullable=True)
    installs = Column(Integer, nullable=True)
    free = Column(Boolean, default=True)
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String, nullable=True)
    size = Column(Float, nullable=True)
    minimum_installs = Column(Integer, nullable=True)
    maximum_installs = Column(Integer, nullable=True)
    minimum_android = Column(String, nullable=True)
    developer_id = Column(String, nullable=False)  # References Developer table
    released = Column(Date, nullable=True)
    last_updated = Column(Date, nullable=True)
    content_rating = Column(String, nullable=True)
    # Map the model attribute "privacy_policy_url" to the actual database column "privacy_policy"
    privacy_policy_url = Column("privacy_policy", String, nullable=True)
    ad_supported = Column(Boolean, default=False)
    in_app_purchases = Column(Boolean, default=False)
    editors_choice = Column(Boolean, default=False)
    scraped_time = Column(DateTime, nullable=True)


# Create tables if they do not already exist
Base.metadata.create_all(bind=engine)


# ------------------------------------------------------------------------------
# Pydantic Schemas for Data Validation and Serialization
# ------------------------------------------------------------------------------

# Schemas for Categories
class CategoryBase(BaseModel):
    category: str


class CategoryCreate(CategoryBase):
    """
    Schema for creating a new category.
    """
    pass


class CategoryUpdate(BaseModel):
    """
    Schema for updating a category.
    Since the primary key is the only field, caution is needed when updating.
    """
    category: Optional[str] = None


class CategoryOut(CategoryBase):
    """
    Schema for returning category data.
    """

    class Config:
        orm_mode = True


# Schemas for Developers
class DeveloperBase(BaseModel):
    developer_website: Optional[str] = None
    developer_email: Optional[str] = None


class DeveloperCreate(DeveloperBase):
    developer_id: str


class DeveloperUpdate(BaseModel):
    """
    Schema for updating a developer record.
    All fields are optional for partial updates.
    """
    developer_website: Optional[str] = None
    developer_email: Optional[str] = None


class DeveloperOut(DeveloperBase):
    developer_id: str

    class Config:
        orm_mode = True


# Schemas for Applications
class ApplicationBase(BaseModel):
    app_name: str
    category: str
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    installs: Optional[int] = None
    free: bool = True
    price: Optional[float] = None
    currency: Optional[str] = None
    size: Optional[float] = None
    minimum_installs: Optional[int] = None
    maximum_installs: Optional[int] = None
    minimum_android: Optional[str] = None
    developer_id: str
    released: Optional[datetime.date] = None
    last_updated: Optional[datetime.date] = None
    content_rating: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    ad_supported: bool = False
    in_app_purchases: bool = False
    editors_choice: bool = False
    scraped_time: Optional[datetime.datetime] = None


class ApplicationCreate(ApplicationBase):
    app_id: str


class ApplicationUpdate(BaseModel):
    app_name: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    installs: Optional[int] = None
    free: Optional[bool] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    size: Optional[float] = None
    minimum_installs: Optional[int] = None
    maximum_installs: Optional[int] = None
    minimum_android: Optional[str] = None
    developer_id: Optional[str] = None
    released: Optional[datetime.date] = None
    last_updated: Optional[datetime.date] = None
    content_rating: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    ad_supported: Optional[bool] = None
    in_app_purchases: Optional[bool] = None
    editors_choice: Optional[bool] = None
    scraped_time: Optional[datetime.datetime] = None


class ApplicationOut(ApplicationBase):
    app_id: str

    class Config:
        orm_mode = True


# ------------------------------------------------------------------------------
# FastAPI Application Instance
# ------------------------------------------------------------------------------
app = FastAPI(title="Google Play Applications API")


# ------------------------------------------------------------------------------
# Dependency: Get a Database Session per Request
# ------------------------------------------------------------------------------
def get_db():
    """
    Creates a new database session for each request and closes it after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------------------------
# Root Endpoint
# ------------------------------------------------------------------------------
@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message and directs users to the API docs.
    """
    return {"message": "Welcome to the Google Play Applications API. Visit /docs for API documentation."}


# ------------------------------------------------------------------------------
# CRUD Endpoints for Categories
# ------------------------------------------------------------------------------

@app.post("/categories/", response_model=CategoryOut)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Create a new category.

    - **category**: Category data provided in the request body.
    - **db**: Database session dependency.
    """
    db_cat = db.query(Category).filter(Category.category == category.category).first()
    if db_cat:
        raise HTTPException(status_code=400, detail="Category already exists")
    new_cat = Category(**category.dict())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


@app.get("/categories/", response_model=List[CategoryOut])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of categories with pagination.

    - **skip**: Number of records to skip.
    - **limit**: Maximum number of records to return.
    - **db**: Database session dependency.
    """
    cats = db.query(Category).offset(skip).limit(limit).all()
    return cats


@app.get("/categories/{category_id}", response_model=CategoryOut)
def read_category(category_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific category by its identifier.

    - **category_id**: The unique category identifier (category name).
    - **db**: Database session dependency.
    """
    db_cat = db.query(Category).filter(Category.category == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_cat


@app.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: str, category_update: CategoryUpdate, db: Session = Depends(get_db)):
    """
    Update an existing category.

    - **category_id**: The unique identifier of the category to update.
    - **category_update**: Data for updating the category.
    - **db**: Database session dependency.

    Note: Since the primary key is the category name, updating it may affect related foreign key constraints.
    """
    db_cat = db.query(Category).filter(Category.category == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_update.dict(exclude_unset=True)
    if "category" in update_data and update_data["category"]:
        db_cat.category = update_data["category"]
    db.commit()
    db.refresh(db_cat)
    return db_cat


@app.delete("/categories/{category_id}")
def delete_category(category_id: str, db: Session = Depends(get_db)):
    """
    Delete a category from the database.

    - **category_id**: The unique identifier of the category to delete.
    - **db**: Database session dependency.

    Note: Deleting a category that is referenced by applications may result in a foreign key violation.
    """
    db_cat = db.query(Category).filter(Category.category == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_cat)
    db.commit()
    return {"detail": "Category deleted successfully"}


# ------------------------------------------------------------------------------
# CRUD Endpoints for Developers
# ------------------------------------------------------------------------------

@app.post("/developers/", response_model=DeveloperOut)
def create_developer(developer: DeveloperCreate, db: Session = Depends(get_db)):
    """
    Create a new developer record.
    """
    db_dev = db.query(Developer).filter(Developer.developer_id == developer.developer_id).first()
    if db_dev:
        raise HTTPException(status_code=400, detail="Developer already exists")
    new_dev = Developer(**developer.dict())
    db.add(new_dev)
    db.commit()
    db.refresh(new_dev)
    return new_dev


@app.get("/developers/{developer_id}", response_model=DeveloperOut)
def read_developer(developer_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a developer by developer_id.
    """
    db_dev = db.query(Developer).filter(Developer.developer_id == developer_id).first()
    if not db_dev:
        raise HTTPException(status_code=404, detail="Developer not found")
    return db_dev


@app.put("/developers/{developer_id}", response_model=DeveloperOut)
def update_developer(developer_id: str, developer_update: DeveloperUpdate, db: Session = Depends(get_db)):
    """
    Update an existing developer record.

    - **developer_id**: The unique identifier of the developer to update.
    - **developer_update**: Data for updating the developer.
    - **db**: Database session dependency.
    """
    db_dev = db.query(Developer).filter(Developer.developer_id == developer_id).first()
    if not db_dev:
        raise HTTPException(status_code=404, detail="Developer not found")
    update_data = developer_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_dev, key, value)
    db.commit()
    db.refresh(db_dev)
    return db_dev


@app.delete("/developers/{developer_id}")
def delete_developer(developer_id: str, db: Session = Depends(get_db)):
    """
    Delete a developer record.

    - **developer_id**: The unique identifier of the developer to delete.
    - **db**: Database session dependency.
    """
    db_dev = db.query(Developer).filter(Developer.developer_id == developer_id).first()
    if not db_dev:
        raise HTTPException(status_code=404, detail="Developer not found")
    db.delete(db_dev)
    db.commit()
    return {"detail": "Developer deleted successfully"}


# ------------------------------------------------------------------------------
# CRUD Endpoints for Applications
# ------------------------------------------------------------------------------

@app.post("/applications/", response_model=ApplicationOut)
def create_application(app_data: ApplicationCreate, db: Session = Depends(get_db)):
    """
    Create a new application record.
    Note: The referenced developer must already exist.
    """
    db_app = db.query(Application).filter(Application.app_id == app_data.app_id).first()
    if db_app:
        raise HTTPException(status_code=400, detail="Application already exists")

    # Ensure that the referenced developer exists.
    db_dev = db.query(Developer).filter(Developer.developer_id == app_data.developer_id).first()
    if not db_dev:
        raise HTTPException(status_code=400,
                            detail=f"Developer '{app_data.developer_id}' does not exist. Please create the developer record first.")

    new_app = Application(**app_data.dict())
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app


@app.get("/applications/", response_model=List[ApplicationOut])
def read_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of applications with pagination.

    - **skip**: Number of records to skip.
    - **limit**: Maximum number of records to return.
    - **db**: Database session dependency.
    """
    apps = db.query(Application).offset(skip).limit(limit).all()
    return apps


@app.get("/applications/{app_id}", response_model=ApplicationOut)
def read_application(app_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific application by its app_id.

    - **app_id**: Unique identifier of the application.
    - **db**: Database session dependency.
    """
    db_app = db.query(Application).filter(Application.app_id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_app


@app.put("/applications/{app_id}", response_model=ApplicationOut)
def update_application(app_id: str, app_update: ApplicationUpdate, db: Session = Depends(get_db)):
    """
    Update an existing application record.

    - **app_id**: Unique identifier of the application to update.
    - **app_update**: Data to update (partial updates allowed).
    - **db**: Database session dependency.
    """
    db_app = db.query(Application).filter(Application.app_id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = app_update.dict(exclude_unset=True)
    # If updating developer_id, ensure the new developer exists.
    if "developer_id" in update_data:
        db_dev = db.query(Developer).filter(Developer.developer_id == update_data["developer_id"]).first()
        if not db_dev:
            raise HTTPException(status_code=400, detail=f"Developer '{update_data['developer_id']}' does not exist.")

    for key, value in update_data.items():
        setattr(db_app, key, value)
    db.commit()
    db.refresh(db_app)
    return db_app


@app.delete("/applications/{app_id}")
def delete_application(app_id: str, db: Session = Depends(get_db)):
    """
    Delete an application record.

    - **app_id**: Unique identifier of the application to delete.
    - **db**: Database session dependency.
    """
    db_app = db.query(Application).filter(Application.app_id == app_id).first()
    if db_app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(db_app)
    db.commit()
    return {"detail": "Application deleted successfully"}


# ------------------------------------------------------------------------------
# Run the API using Uvicorn (for development purposes)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

