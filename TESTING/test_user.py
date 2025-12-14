import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
load_dotenv()
BASE_URL=os.getenv("BASE_URL")

#test that the home page for the user is a dashboard
def test_user_dashboard(logged_in_driver):
    """
    GIVEN a user has logged in
    WHEN they are redirected 
    THEN they are on the dashboard page
    """
    assert "/dashboard" in logged_in_driver.current_url

#test the search feature for users 
def test_search(logged_in_driver,seed_restaurant):
    """
    #GIVEN a user has logged in AND there are restaurants in the DB
    #WHEN they search by cuisine using the search field 
    #THEN they are redirected to the search page with the 
"""
    restaurant=seed_restaurant
    logged_in_driver.get(f"{BASE_URL}/dashboard")

    WebDriverWait(logged_in_driver,5).until(
        EC.presence_of_element_located((By.TAG_NAME,"input"))
    )

    search_box=logged_in_driver.find_element(By.NAME,"cuisine")
    search_box.clear()

    search_box.send_keys(restaurant.cuisine) 
    search_box.send_keys(Keys.RETURN)

    expected_header=f'Results for "{restaurant.cuisine}"'
    
    WebDriverWait(logged_in_driver,10).until(
        EC.presence_of_element_located((
            By.XPATH, 
            f"//h2[contains(text(), '{expected_header}')]"
        ))
    )
    
    
    assert restaurant.name in logged_in_driver.page_source

    logged_in_driver.get(f"{BASE_URL}/dashboard")

    WebDriverWait(logged_in_driver,5).until(
        EC.presence_of_element_located((By.TAG_NAME,"input"))
    )

    search_box=logged_in_driver.find_element(By.NAME,"cuisine")
    search_box.clear()

    search_box.send_keys(restaurant.name) 
    search_box.send_keys(Keys.RETURN)

    expected_header=f'Results for "{restaurant.name}"'
    
    WebDriverWait(logged_in_driver,10).until(
        EC.presence_of_element_located((
            By.XPATH, 
            f"//h2[contains(text(), '{expected_header}')]"
        ))
    )
    
    assert restaurant.name in logged_in_driver.page_source

def test_add_favorite(logged_in_driver,seed_restaurant):
    logged_in_driver.get(f"{BASE_URL}/search?cuisine={seed_restaurant.cuisine}")

    expected_header=f'Results for "{seed_restaurant.cuisine}"'
    
    WebDriverWait(logged_in_driver,10).until(
      EC.presence_of_element_located((
            By.XPATH, 
            f"//h2[contains(text(), '{expected_header}')]"
        ))   
    )

    add_favorite_button=logged_in_driver.find_element(By.ID,f'fav-btn-{seed_restaurant.id}')
    add_favorite_button.click()

    WebDriverWait(logged_in_driver,10).until(
        EC.presence_of_element_located(
            (
            By.XPATH, 
            f"//h2[contains(text(), 'My Favorites')]"
        )
        )
    )

    assert seed_restaurant.name in logged_in_driver.page_source



def test_remove_favorite(logged_in_driver,favorite):
    logged_in_driver.get(f"{BASE_URL}/dashboard")
    remove_button=logged_in_driver.find_element(By.ID,f"remove-btn-{favorite.id}")
    remove_button.click()
    WebDriverWait(logged_in_driver,10).until(
         EC.presence_of_element_located(
            (
            By.XPATH, 
            f"//h2[contains(text(), 'My Favorites')]"
        )
        )
    )

    assert favorite.name not in logged_in_driver.page_source

@pytest.mark.parametrize("user_type", ["user","admin"], indirect=True)
def test_log_out(logged_in_driver,user_type):
    logout_button=logged_in_driver.find_element(By.LINK_TEXT,"Logout")
    logout_button.click()

    WebDriverWait(logged_in_driver,10).until(
        EC.presence_of_element_located((
            By.LINK_TEXT,"Get Started"
        ))
    )

    cookie=logged_in_driver.get_cookie("access_token")

    assert cookie is None