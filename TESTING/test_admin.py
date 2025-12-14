import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL=os.getenv("BASE_URL")

#test that landing page for admin is /admin NOT dashboard
@pytest.mark.parametrize("user_type",["admin"],indirect=True)
def test_admin_homepage(logged_in_driver):
    
    #GIVEN an admin is logged in
    #WHEN they are redirected to their homepage
    #THEN the home page is the admin dashboard @ /admin
    
    assert "/admin" in logged_in_driver.current_url

#test adding restaurants using the scrapper
@pytest.mark.parametrize("user_type",["admin"],indirect=True)
def test_scrapping(logged_in_driver):
    
    #GIVEN an admin is logged in
    #WHEN they use the scrape form to add restaurants for a cuisine
    #THEN the page redirect to the admin dashboard with new rows of restaurants
    #according to how many were scrapped (could be 0)
    
    initial_rows = logged_in_driver.find_elements(By.CLASS_NAME, "restaurant-row")
    initial_count = len(initial_rows)

    logged_in_driver.find_element(By.ID, "location-box").clear()
    logged_in_driver.find_element(By.ID, "location-box").send_keys("Cairo")
    
    logged_in_driver.find_element(By.ID, "search-box").clear()
    logged_in_driver.find_element(By.ID, "search-box").send_keys("Burger")

    logged_in_driver.find_element(By.ID, "import-btn").click()
    WebDriverWait(logged_in_driver, 60).until(
        EC.presence_of_element_located((By.ID, "status-msg"))
    )

    status_msg=logged_in_driver.find_element(By.ID, "status-msg").text
    
    new_rows = logged_in_driver.find_elements(By.CLASS_NAME, "restaurant-row")
    new_count = len(new_rows)
    match = re.search(r'\d+', status_msg)
    scraped_count = int(match.group()) if match else 0
    assert new_count - initial_count == scraped_count

#test toggling the active status
@pytest.mark.parametrize("user_type",["admin"],indirect=True)
def test_toggle_status(logged_in_driver,seed_restaurant):

    #GIVEN an admin is logged in and there are restaurants in the db
    #WHEN they toggle a restaurant's active status
    #THEN the restaurant's status badge updates active->inactive and inactive->active

    logged_in_driver.get(f"{BASE_URL}/admin")
    WebDriverWait(logged_in_driver,5).until(
        EC.presence_of_element_located(
            (
            By.XPATH, 
            f"//strong[contains(text(), 'System Inventory')]"
        )
    ))
    restaurant=seed_restaurant
    initial_badge=logged_in_driver.find_element(By.ID,f"status-badge-{restaurant.id}")
    assert "Active" in initial_badge.text

    logged_in_driver.find_element(By.ID,f"toggle-status-{restaurant.id}").click()

    logged_in_driver.refresh()

    new_badge=logged_in_driver.find_element(By.ID,f"status-badge-{restaurant.id}")
    assert "Inactive" in new_badge.text

    #reverse test inactive to active
    logged_in_driver.find_element(By.ID,f"toggle-status-{restaurant.id}").click()

    logged_in_driver.refresh()
    reverted_badge=logged_in_driver.find_element(By.ID,f"status-badge-{restaurant.id}")
    assert "Active" in reverted_badge.text
