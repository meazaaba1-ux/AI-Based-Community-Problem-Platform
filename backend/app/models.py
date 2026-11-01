
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(String(255), nullable=False)

    role = Column(String(20), default="citizen")

    # Officer's assigned category
    category = Column(String(100), nullable=True)


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    description = Column(String(1000), nullable=False)

    location = Column(String(255), nullable=False)

    category = Column(String(100), nullable=True)

    image_url = Column(String(255), nullable=True)

    latitude = Column(Float, nullable=True)

    longitude = Column(Float, nullable=True)

    status = Column(String(30), default="pending")

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Officer assigned to this report
    assigned_officer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
