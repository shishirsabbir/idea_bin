# IMPORTING MODULES
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func


# SETUP POSTGRESQL AND ADD PASSWORD
# SQL_URL = "postgresql+psycopg2://postgres:<password>@localhost:5432/IdeaBinDB"
# engine = create_engine(SQL_URL)


# SETUP SQLITE
SQL_URL = "sqlite:///IdeaBinDB.db"
engine = create_engine(SQL_URL, connect_args={"check_same_thread": False})


# CREATING DATABASE SESSION AND BASE
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# CREATING CLASSES FOR TABLES
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum('admin', 'developer', 'user', name="user_role"), nullable=False)
    created_on = Column(DateTime, server_default=func.now())


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category = Column(Enum("General", "Technology", "Marketing", "Business", "Application", "Tools", name="idea_category"), nullable=False)
    owner = Column(Integer, ForeignKey("accounts.id"))


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    owner = Column(Integer, ForeignKey("accounts.id"))
