import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

import pytest
import time
from threading import Thread
import uvicorn
from sqlmodel import Session,select,delete

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from DB.db_setup import engine
from DB.models import User, Restaurant, UserFavorite
from API.utils import hash_password
from API.findmymeal import app

from dotenv import load_dotenv
load_dotenv()
BASE_URL=os.getenv("BASE_URL")


@pytest.fixture(scope="session", autouse=True)
def run_server():
    def run():
        uvicorn.run(app, host="127.0.0.1", port=8000)
    
    t = Thread(target=run, daemon=True)
    t.start()
    time.sleep(2) 
    yield


@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.fixture(scope="function",autouse=True)
def yield_db():
    #deletes all preexisting data in the db before test 
    with Session(engine) as session:
        session.exec(delete(UserFavorite))
        session.exec(delete(User))
        session.exec(delete(Restaurant))
        session.commit()        
    yield
    #deletes all data in the db after test 
    with Session(engine) as session:
        session.exec(delete(UserFavorite))
        session.exec(delete(User))
        session.exec(delete(Restaurant))
        session.commit()


@pytest.fixture(scope="function")
def seed_restaurant():


    rtest = Restaurant(id='rtest', name="Test Burger", cuisine="American", address="123 Bun St", place_id="p1", active=True)

    with Session(engine) as session:
        session.add(rtest)
        session.commit()

        session.refresh(rtest)

    
    #yield restaurant data and objs for use
    yield rtest

@pytest.fixture(scope="function")
def yield_user():
    user=User(id="uidfake",
                  username="testusername",
                  hashed_password=hash_password("T3st!P@ssw0rd_SeCuRe_99"),
                  role="user")
    
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

        yield {"obj":user,"password":"T3st!P@ssw0rd_SeCuRe_99"}

        

@pytest.fixture(scope="function")
def favorite(yield_user,seed_restaurant):
    with Session(engine) as session:
     
        fav = UserFavorite(userid=yield_user["obj"].id, restaurantid=seed_restaurant.id)
        
        session.add(fav)
        
        session.commit()
        session.refresh(fav)

        yield seed_restaurant
        

@pytest.fixture(scope ="function")
def user_type(yield_user,yield_admin,request):
    if not hasattr(request,"param"):
        return yield_user
    if request.param=='admin':
        return yield_admin
    else:
        return yield_user

@pytest.fixture(scope="function")
def logged_in_driver(driver,user_type):
    
    driver.get(f"{BASE_URL}/auth/login")
   
    driver.find_element(By.NAME, "username").send_keys(user_type['obj'].username)
    driver.find_element(By.NAME, "password").send_keys(user_type["password"])
    driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]").click()
    
   #wait until logout button appears
    WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.LINK_TEXT,"Logout"))
    )

    
    yield driver

@pytest.fixture(scope="function")
def yield_admin():
    user=User(id="uidfakeadmin",
                  username="testadmin",
                  hashed_password=hash_password("T3st!P@ssw0rd_SeCuRe_99"),
                  role="admin")
    
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

        yield {"obj":user,"password":"T3st!P@ssw0rd_SeCuRe_99"}



