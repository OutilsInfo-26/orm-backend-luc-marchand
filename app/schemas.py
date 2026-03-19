#Les schémas Pydantic sont utilisés pour définir la structure des données d'entrée et de sortie de l'API. 
# Ils permettent de valider les données reçues et de contrôler la forme des données renvoyées.

from datetime import date

from pydantic import BaseModel, Field


class AuthorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Author full name")

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Ada Lovelace"}
        }
    }


class AuthorUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)


class AuthorOut(AuthorCreate):
    id: int

    model_config = {
        "from_attributes": True,
    }


class BookCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, description="Book title")
    pages: int = Field(..., gt=0, le=2000, description="Number of pages")
    author_id: int = Field(..., gt=0, description="Existing author id")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Notes on the Analytical Engine",
                "pages": 120,
                "author_id": 1,
            }
        }
    }


class BookOut(BookCreate):
    id: int

    model_config = {
        "from_attributes": True,
    }


class BookSummary(BaseModel):
    id: int
    title: str


class BookWithAuthor(BaseModel):
    id: int
    title: str
    pages: int
    author_name: str

class BookFull(BaseModel):
    book_name: str
    author_name: str
    editor_name: str | None

    

# Contrairement à BookWithAuthor, ici author est un objet imbriqué
# accessible via la navigation ORM (book.author.id, book.author.name)
class BookWithAuthorObject(BaseModel):
    id: int
    title: str
    pages: int
    author: AuthorOut

    model_config = {"from_attributes": True}


class BookWithPublisher(BaseModel):
    id: int
    title: str
    pages: int
    publisher_name: str | None


class TagOut(BaseModel):
    name: str
    tagged_at: date

    model_config = {"from_attributes": True}


class BookWithTags(BaseModel):
    id: int
    title: str
    tags: list[TagOut]

    model_config = {"from_attributes": True}



class PersonCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50, description="First name of person")
    last_name: str = Field(..., min_length=2, max_length=50, description="Last name of person")

    model_config = {
        "json_schema_extra": {
            "example": {"first_name": "John", "last_name": "Doe"}
        }
    }

class PersonUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=2, max_length=50)
    last_name: str | None = Field(None, min_length=2, max_length=50)


class PersonOut(PersonCreate):
    id: int

class PersonWithBooks(BaseModel):
    first_name: str
    last_name: str
    title: str

class PersonWithBooksCount(BaseModel):
    first_name: str
    last_name: str
    numberOfBooks: int 

class StatsOut(BaseModel):
    total_books: int
    total_authors: int
    total_tags: int
    longest_book: str
    longest_book_pages: int
    mean_pages: float
