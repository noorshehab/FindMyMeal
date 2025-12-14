from typing import Optional, List
from sqlmodel import Field,  SQLModel,  Relationship


class UserFavorite(SQLModel,table=True):
    userid: Optional[str] = Field(default=None, foreign_key="user.id",primary_key=True)
    restaurantid: Optional[str] = Field(default=None, foreign_key="restaurant.id",primary_key=True)

class User(SQLModel,table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    username:str
    hashed_password:str
    favorites: List["Restaurant"] = Relationship(back_populates="favorited_by", link_model=UserFavorite)
    role: Optional[str]=Field(default='user')

class Restaurant(SQLModel,table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    place_id:Optional[str] = Field(default=None, unique=True,index=True)
    name:str
    address:str
    cuisine:str
    active: Optional[bool] = Field(default=True)
    favorited_by: List["User"] = Relationship(back_populates="favorites", link_model=UserFavorite)

