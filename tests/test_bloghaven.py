import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BlogHavenTests(unittest.TestCase):
    def setUp(self):
        # Connect to Selenium container
        options = Options()
        self.driver = webdriver.Remote(
            command_executor="http://localhost:4444/wd/hub",
            options=options
        )
        self.driver.maximize_window()

    def tearDown(self):
        # Close the browser after each test
        self.driver.quit()

    def test_login_page_loads(self):
        # Test that the login page loads and displays the login form
        try:
            self.driver.get("http://bloglite:5000/login")
            # Wait for the email field to be present
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            # Assert that the email and password fields are visible
            self.assertTrue(email_field.is_displayed(), "Email field is not visible on login page")
            self.assertTrue(password_field.is_displayed(), "Password field is not visible on login page")
        except TimeoutException as e:
            self.fail(f"Timeout waiting for login page elements: {str(e)}")

    def test_signup_page_loads(self):
        # Test that the signup page loads and displays the signup form
        try:
            self.driver.get("http://bloglite:5000/sign-up")
            # Wait for the email field to be present
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            # Assert that the email, username, and password fields are visible
            self.assertTrue(email_field.is_displayed(), "Email field is not visible on signup page")
            self.assertTrue(username_field.is_displayed(), "Username field is not visible on signup page")
            self.assertTrue(password_field.is_displayed(), "Password field is not visible on signup page")
        except TimeoutException as e:
            self.fail(f"Timeout waiting for signup page elements: {str(e)}")

    def test_navigation_bar_visibility(self):
        # Test that the navigation bar is visible on the login page
        try:
            self.driver.get("http://bloglite:5000/login")
            # Wait for the navigation bar to be present
            nav_bar = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "nav"))
            )
            # Find a navigation link (e.g., "Home")
            home_link = nav_bar.find_element(By.LINK_TEXT, "Home")
            # Assert that the navigation bar and link are visible
            self.assertTrue(nav_bar.is_displayed(), "Navigation bar is not visible on login page")
            self.assertTrue(home_link.is_displayed(), "Home link is not visible in navigation bar")
        except TimeoutException as e:
            self.fail(f"Timeout waiting for navigation bar elements: {str(e)}")

    def test_home_page_title(self):
        # Test that the home page loads and has the correct title for unauthenticated users
        try:
            self.driver.get("http://bloglite:5000")
            # Wait for the title element to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "title"))
            )
            page_title = self.driver.title
            # Assert that the title contains "Home"
            self.assertIn("Home", page_title, "Home page title does not contain 'Home'")
        except TimeoutException as e:
            self.fail(f"Timeout waiting for home page title: {str(e)}")

if __name__ == "__main__":
    unittest.main()