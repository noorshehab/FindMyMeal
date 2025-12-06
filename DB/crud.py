import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from sqlmodel import SQLModel, Session,select
import uuid
from DB.models import*



def get_user(user_name:str,session:Session)-> User:
    statement= select(User).where(User.username==user_name)
    result=session.exec(statement)
    user=result.first()
    return user

def add_user(user_name:str,password,session:Session)-> User :
    uid=str(uuid.uuid4())[:8]
    user=User(id=uid,username=user_name,hashed_password=password)
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

def add_favorite(user_id:str,restaurant_id:str,session:Session):
    favorite=UserFavorite(userid=user_id,restaurantid=restaurant_id)

    session.add(favorite)
    session.commit()
    session.refresh(favorite)
    return favorite

def get_favorites(userid:str,session:Session):
    statement=select(Restaurant).join(UserFavorite,Restaurant.id==UserFavorite.restaurantid).where(User.id==userid)
    results=session.exec(statement)
    favorites=results.all()
    return favorites

def add_restaurant(name:str,address:str,cuisine:str,place_id:str,session:Session)-> Restaurant:
    rid=str(uuid.uuid4())[:8]
    restaurant=Restaurant(id=rid,name=name,address=address,cuisine=cuisine,place_id=place_id)
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)

    return restaurant


def update_restaurant(name:str,status:bool,session:Session):
    statement= select(Restaurant).where(Restaurant.name==name)
    result=session.exec(statement)
    restaurant=result.first()
    if restaurant:
        restaurant.active=status
        session.add(restaurant)
        session.commit()
        session.refresh(restaurant)
        return restaurant
    else:
        return None
    


def get_restaurant_by_cuisine(cuisine:str,session:Session)-> list[Restaurant]:
    statement= select(Restaurant).where(Restaurant.cuisine==cuisine,Restaurant.active==True)
    result=session.exec(statement)
    restaurants=result.all()
    return restaurants

