import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from fastapi import FastAPI, Depends, Form,Request,status,Response,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from DB.models import*
from DB.crud import*
from DB.db_setup import get_session
from API.utils import*
from API.auth import create_access_token,get_current_user,get_current_admin
from API.places_service import ApifyService

app =FastAPI()
templates=Jinja2Templates(directory="TEMPLATES")

#landing page
@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

#signup and log in
@app.get("/auth/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/auth/register",response_class=HTMLResponse)
def register_page(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})

@app.post("/auth/register")
def register(request: Request,
    username: str = Form(...),
    password: str = Form(...)
    ,session:Session=Depends(get_session)):
    if get_user(username,session):
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Username already taken"
        })
    else:
        hashed=hash_password(password)
        new_user=add_user(username,hashed,session)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    
@app.post("/auth/login")
def login(request: Request,
    response: Response, 
    username: str = Form(...),
    password: str = Form(...),
    session:Session=Depends(get_session)):
    user=get_user(username,session)
    if not user or not verify_password(password,user.hashed_password):
       return templates.TemplateResponse("login.html", {
            "request": request, "error": "Invalid credentials"
        })
    
    access_token=create_access_token(data={"sub":user.username})

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/auth/logout")
def logout(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@app.post("/favorites/add",response_class=HTMLResponse)
def add_favorite_ui(
    request: Request,
    restaurant_id: str = Form(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    user_favorites=get_favorites(current_user.id,session)
    try:
        add_favorite(current_user.id, restaurant_id,session)
    except IntegrityError:
       session.rollback()
       return templates.TemplateResponse("dashboard.html",
                                      {
                                          "request": request,
                                            "favorites": user_favorites,
                                            "user": current_user,
                                            "error_message":"Favorite already Exists"  
                                      })
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/favorites/remove/{restaurant_id}",response_class=HTMLResponse)
def remove_fav(
    restaurant_id: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    remove_favorite(restaurant_id=restaurant_id,user_id=current_user.id,session=session)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):
    
    if(current_user.role=='admin'):
        return RedirectResponse(url="/admin",status_code=status.HTTP_303_SEE_OTHER)
    
    favorites = get_favorites( current_user.id,session)
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": current_user, 
        "favorites": favorites
    })
    

#restaurant endpoints

@app.get("/search", response_class=HTMLResponse)
def search_page(
    request: Request,
    cuisine: str, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):

    results = get_restaurant_by_cuisine(cuisine,session)
    
    return templates.TemplateResponse("search_results.html", {
        "request": request,
        "restaurants": results,
        "query": cuisine,
        "user": current_user
    })

#change restaurant status active->inactive OR inactive->active
@app.get("/admin/update/{restaurant_id}",response_class=HTMLResponse)
def update(restaurant_id:str,
           session:Session=Depends(get_session),
           admin_user: User = Depends(get_current_admin)):
     update_restaurant(restaurant_id,session)
     return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    

@app.get("/admin",response_class=HTMLResponse)
def adminpage(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin) 
):
    restaurants=get_restaurants(session)
    return templates.TemplateResponse("admin.html",{
        "request":request,
        "restaurants":restaurants,
        "user":current_user}
    )
    

@app.post("/admin/search")
async def search_restaurants(
    request: Request,
    query: str = Form(...), 
    location: str = Form(...), 
    session: Session = Depends(get_session),
    current_admin: User =Depends(get_current_admin)
):
  
    service = ApifyService()
    
    raw_data = await service.get_restaurants(location, query)
    
    added_count = 0
    
    for item in raw_data:
    
        c_name = item.get("title")
        c_address = item.get("address")
        c_cuisine = item.get("categoryName", "General") 
        c_place_id = item.get("placeId") 
        
        if c_name and c_place_id:

            try:
                add_restaurant(
                    name=c_name, 
                    address=c_address, 
                    cuisine=c_cuisine, 
                    place_id=c_place_id,
                    session=session
                )
                added_count += 1
            except Exception as e:
                print(f"Skipping duplicate: {c_name}")
                session.rollback()

    restaurants = get_restaurants(session)
    return templates.TemplateResponse(
        "admin.html", 
        {
            "user":current_admin,
            "request": request, 
            "restaurants": restaurants, 
            "message": f"Successfully scraped {added_count} restaurants!"
        }
    )