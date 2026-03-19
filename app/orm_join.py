from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.db import get_session
from app.models import Author, Book, Publisher, Person
from app.schemas import BookWithAuthor, BookWithAuthorObject, BookWithPublisher, PersonWithBooks, BookFull, PersonWithBooksCount

router = APIRouter(prefix="/orm", tags=["ORM jointure"])


@router.get("/books-with-authors", response_model=list[BookWithAuthor])
def list_books_with_authors(
    session: Session = Depends(get_session),
) -> list[BookWithAuthor]:
    stmt = (
        select(
            Book.id,
            Book.title,
            Book.pages,
            Author.name.label("author_name"),
        )
        .join(Author)
        .order_by(Book.id)
    )

    # On pourrait aussi utiliser mappings et ** pour éviter de répéter tous les champs de Book :
    # rows = session.execute(stmt).mappings().all()
    # return [BookWithAuthor(**row) for row in rows]

    rows = session.execute(stmt).all()
    return [
        BookWithAuthor(
            id=row.id,
            title=row.title,
            pages=row.pages,
            author_name=row.author_name,
        )
        for row in rows
    ]

# Person
@router.get("/persons-with-books", response_model=list[PersonWithBooks])
def list_persons_with_books(
    session: Session = Depends(get_session),
) -> list[PersonWithBooks]:
    stmt = (
        select(
            Person.first_name,
            Person.last_name,
            Book.title,
        )
        .join(Person.books)
    )

    rows = session.execute(stmt).all()
    return [
        PersonWithBooks(
            first_name=row.first_name,
            last_name=row.last_name,
            title=row.title,
        )
        for row in rows
    ]

# Retourne chaque personne avec le nombre de livres qu'elle possède
@router.get("/persons-with-book-count", response_model=list[PersonWithBooksCount])
def list_persons_with_books(
    session: Session = Depends(get_session),
) -> list[PersonWithBooksCount]:
    stmt = (
        select(
            Person.first_name,
            Person.last_name,
            func.count(Book.id).label("numberOfBooks")
        )
        .join(Person.books)
        .group_by(Person.first_name, Person.last_name)

    )

    rows = session.execute(stmt).all()
    return [
        PersonWithBooksCount(
            first_name=row.first_name,
            last_name=row.last_name,
            numberOfBooks=row.numberOfBooks,
        )
        for row in rows

    ]

# books-full
@router.get("/books-full", response_model=list[BookFull])
def list_books_full(
    session: Session = Depends(get_session),
) -> list[BookFull]:
    stmt = (
        select(
            Book.title,
            Author.name.label("author_name"),   #On mets un .label pour renommer le champ author_name dans le résultat de la requête. (Comme le "as" en SQL)
            Publisher.name.label("editor_name"),
        )
        .join(Author)
        .join(Publisher, Book.publisher_id == Publisher.id, isouter=True)
    )

    # On pourrait aussi utiliser mappings et ** pour éviter de répéter tous les champs de Book :
    # rows = session.execute(stmt).mappings().all()
    # return [BookWithAuthor(**row) for row in rows]

    rows = session.execute(stmt).all()
    return [
        BookFull(
            book_name=row.title,
            author_name=row.author_name,
            editor_name=row.editor_name,
        )
        for row in rows
    ]


@router.get("/books-with-author-object", response_model=list[BookWithAuthorObject])
def list_books_with_author_object(
    session: Session = Depends(get_session),
) -> list[BookWithAuthorObject]:
    # Contrairement à /books-with-authors qui extrait author_name comme simple string,
    # ici on charge des objets Book complets avec book.author navigable (objet Author).
    # joinedload → un seul SELECT avec JOIN, idéal pour une relation many-to-one.
    books = session.scalars(
        select(Book)
        .options(joinedload(Book.author))
        .order_by(Book.id)
    ).all()
    # book.author est un objet Author — on peut accéder à book.author.id, book.author.name
    return books


@router.get("/books-with-publisher", response_model=list[BookWithPublisher])
def list_books_with_publisher(
    session: Session = Depends(get_session),
) -> list[BookWithPublisher]:
    # Publisher n'est pas accessible via book.publisher (pas de relationship défini).
    # On doit donc construire la jointure manuellement avec join() et la condition explicite.
    stmt = (
        select(
            Book.id,
            Book.title,
            Book.pages,
            Publisher.name.label("publisher_name"),
        )
        .join(Publisher, Book.publisher_id == Publisher.id, isouter=True)
        .order_by(Book.id)
    )

    # Idem, on pourrait utiliser mappings et **
    rows = session.execute(stmt).all()
    return [
        BookWithPublisher(
            id=row.id,
            title=row.title,
            pages=row.pages,
            publisher_name=row.publisher_name,
        )
        for row in rows
    ]
