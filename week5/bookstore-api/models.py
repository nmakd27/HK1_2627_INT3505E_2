from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import mapped_column, relationship

db = SQLAlchemy()

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    book_id = mapped_column(Integer, ForeignKey('books.id'), primary_key=True)
    author_id = mapped_column(Integer, ForeignKey('authors.id'), primary_key=True)
    role = mapped_column(String(20), default="co")

    author = relationship("Author")

class Category(db.Model):
    __tablename__ = 'categories'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    slug = mapped_column(String(100), unique=True, nullable=False)

class Book(db.Model):
    __tablename__ = 'books'
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(200), nullable=False)
    isbn = mapped_column(String(13), unique=True, nullable=True)
    price_amount = mapped_column(Integer, default=0)
    price_currency = mapped_column(String(3), default="VND")

    book_authors = relationship("BookAuthor", cascade="all, delete-orphan")

    def to_dict(self):
        authors_list = []
        for ba in self.book_authors:
            if ba.author:
                authors_list.append({
                    "id": ba.author.id,
                    "name": ba.author.name,
                    "role": ba.role if ba.role in ["lead", "co", "ed"] else "co"
                })

        if not authors_list:
            authors_list = [{"id": 1, "name": "Tác giả mặc định", "role": "lead"}]

        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "price": {
                "amount": self.price_amount,
                "currency": self.price_currency
            },
            "authors": authors_list
        }

class Author(db.Model):
    __tablename__ = 'authors'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    bio = mapped_column(Text, nullable=True)

class User(db.Model):
    __tablename__ = 'users'
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(120), unique=True, nullable=False)
    display_name = mapped_column(String(100))

class Review(db.Model):
    __tablename__ = 'reviews'
    id = mapped_column(Integer, primary_key=True)
    rating = mapped_column(Integer, nullable=False)
    comment = mapped_column(Text)
    
    book_id = mapped_column(Integer, ForeignKey('books.id'), nullable=False)
    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    
    book = relationship("Book", backref="reviews")
    user = relationship("User", backref="reviews")