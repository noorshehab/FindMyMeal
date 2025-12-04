

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import List

from DB.models import*
from DB.crud import*
from DB.db_setup import get_session
from utils import*
from auth import create_access_token,get_current_user,get_current_admin

app =FastAPI()

#user endpoints

@app.post("/auth/register",response_model=UserReturn)
def register(userin:UserSignup,session:Session=Depends(get_session)):
    if get_user(userin.username,session):
        raise HTTPException(status_code=400, detail="Username already taken")
    else:
        hashed=hash_password(userin.password)
        new_user=add_user(userin.username,hashed,session)
        return new_user

@app.post("/auth/login",response_model=UserReturn)
def login(form_data: OAuth2PasswordRequestForm = Depends(),session:Session=Depends(get_session)):
    user=get_user(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="User doesnt exist")
    if not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(status_code=400, detail="Passwords dont match")
    
    access_token=create_access_token(data={"sub":user.username})

    return {"access_token":access_token,"token_type":"bearer"}

@app.post("/favorites/add")
def add_favorite(
    restaurant_id: str, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):
    return add_favorite(restaurant_id,session,current_user.id)

@app.get("/favorites",response_model=List[RestaurantRead])
def get_favorites(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):
    restaurants=get_favorites(current_user.id,session)
    return restaurants

#restaurant endpoints
#add restaurant
@app.post("/add",response_model=RestaurantRead)
def add(restaurant:RestaurantCreate,
        session:Session=Depends(get_session),
        admin_user: User = Depends(get_current_admin)):
    return add_restaurant(restaurant.name,restaurant.address,restaurant.cuisine,restaurant.place_id,session)

#search restaurants by cuisine
@app.get("/search",response_model=List[RestaurantRead])
def search(cuisine:str,session:Session=Depends(get_session)):
    return get_restaurant_by_cuisine(cuisine,session)

#change restaurant status active->inactive OR inactive->active
@app.post("/update",response_model=RestaurantRead)
def update(restaurant:str,
           status:bool,
           session:Session=Depends(get_session),
           admin_user: User = Depends(get_current_admin)):
    return update_restaurant(restaurant,status,session)