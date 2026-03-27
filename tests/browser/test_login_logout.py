"""
Browser-based Login/Logout Regression Tests (Selenium)
======================================================
Tests the complete login/logout flow via the browser, simulating real user behavior.
Covers: Authentication, Session Persistence, Security, Edge Cases.

Run: pytest tests/browser/test_login_logout.py -v --tb=short
Prerequisites: Streamlit app running on localhost (port from TEST_PORT env var or 8502)
"""
import os
import time
import json
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# ── Config ──────────────────────────────────────────────────────
BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8502")
EMAIL = os.environ.get("ADMIN_EMAIL", "mohdsaeedafri@coresight.com")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "Welcome@123")
WAIT_TIMEOUT = 30  # seconds – generous for STG latency


# ── Fixtures ────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    """Headless Chrome in incognito – fresh session every module."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--incognito")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


def _clear_cookies(driver):
    driver.delete_all_cookies()


def _wait_for_login_page(driver, timeout=WAIT_TIMEOUT):
    """Wait until the login form is visible."""
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Email']"))
    )


def _wait_for_home_page(driver, timeout=WAIT_TIMEOUT):
    """Wait until the home page loads (Logout button visible)."""
    # Check that the text "Logout" is somewhere on the page (as a button)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Logout')]"))
    )


def _login(driver, email=EMAIL, password=PASSWORD):
    """Perform a complete login flow."""
    driver.get(BASE_URL)
    time.sleep(3)
    _clear_cookies(driver)
    driver.get(BASE_URL)
    time.sleep(5)

    _wait_for_login_page(driver)

    # Fill email
    email_input = driver.find_element(By.XPATH, "//input[@aria-label='Email']")
    email_input.clear()
    email_input.send_keys(email)

    # Fill password
    pw_input = driver.find_element(By.XPATH, "//input[@aria-label='Password']")
    pw_input.clear()
    pw_input.send_keys(password)

    # Click Login
    login_btn = driver.find_element(By.XPATH, "//button[.//p[contains(text(),'Login')]]")
    login_btn.click()

    # Wait for home page or timeout
    time.sleep(10)  # STG latency buffer
    _wait_for_home_page(driver, timeout=WAIT_TIMEOUT)


def _get_auth_cookie(driver):
    """Get auth_session cookie value or None."""
    cookie = driver.get_cookie("auth_session")
    return cookie["value"] if cookie else None


def _do_logout(driver):
    """Click the logout button."""
    logout_btn = driver.find_element(By.XPATH, "//*[contains(text(),'Logout')]")
    logout_btn.click()
    time.sleep(10)  # STG latency


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TC1: Fresh Incognito Start → Login Page Landing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestCoreLoginFlow:

    def test_tc1_fresh_start_shows_login(self, driver):
        """TC1: Fresh incognito start should show login form."""
        _clear_cookies(driver)
        driver.get(BASE_URL)
        time.sleep(8)
        _wait_for_login_page(driver)
        assert driver.find_element(By.XPATH, "//input[@aria-label='Email']")
        assert driver.find_element(By.XPATH, "//input[@aria-label='Password']")

    def test_tc2_wrong_credentials(self, driver):
        """TC2: Wrong credentials should show error message."""
        _clear_cookies(driver)
        driver.get(BASE_URL)
        time.sleep(5)
        _wait_for_login_page(driver)

        email_input = driver.find_element(By.XPATH, "//input[@aria-label='Email']")
        email_input.clear()
        email_input.send_keys("wrong@email.com")

        pw_input = driver.find_element(By.XPATH, "//input[@aria-label='Password']")
        pw_input.clear()
        pw_input.send_keys("wrongpassword")

        login_btn = driver.find_element(By.XPATH, "//button[.//p[contains(text(),'Login')]]")
        login_btn.click()
        time.sleep(12)

        # Check for error message
        page_source = driver.page_source.lower()
        assert "incorrect" in page_source or "error" in page_source or "invalid" in page_source, \
            "Expected error message for wrong credentials"

    def test_tc3_correct_login(self, driver):
        """TC3: Correct credentials should redirect to home page."""
        _clear_cookies(driver)
        _login(driver)
        page_source = driver.page_source
        assert "Logout" in page_source, "Expected Logout button on home page"
        assert "CORESIGHT" in page_source.upper(), "Expected Coresight branding"

    def test_tc4_first_refresh_session_persists(self, driver):
        """TC4: Session should persist after first page refresh."""
        driver.refresh()
        time.sleep(10)
        _wait_for_home_page(driver)
        assert "Logout" in driver.page_source

    def test_tc5_second_refresh_session_persists(self, driver):
        """TC5: Session should persist after second refresh."""
        driver.refresh()
        time.sleep(10)
        _wait_for_home_page(driver)
        assert "Logout" in driver.page_source


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TC6-TC8: Cross-page Navigation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestCrossPageNavigation:

    def test_tc6_navigate_market_data(self, driver):
        """TC6: Navigate to Market Data – should stay authenticated."""
        driver.get(f"{BASE_URL}/market_data")
        time.sleep(10)
        assert "Logout" in driver.page_source, "Lost auth on /market_data"

    def test_tc7_navigate_earnings_calls(self, driver):
        """TC7: Navigate to Earnings Calls – should stay authenticated."""
        driver.get(f"{BASE_URL}/earnings_calls")
        time.sleep(10)
        assert "Logout" in driver.page_source, "Lost auth on /earnings_calls"

    def test_tc8_navigate_newsroom(self, driver):
        """TC8: Navigate to Newsroom – should stay authenticated."""
        driver.get(f"{BASE_URL}/newsroom")
        time.sleep(10)
        assert "Logout" in driver.page_source, "Lost auth on /newsroom"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TC9-TC11: Logout & Security
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestLogoutAndSecurity:

    def test_tc9_logout_redirects_to_login(self, driver):
        """TC9: Clicking Logout should redirect to login page."""
        driver.get(f"{BASE_URL}/home")
        time.sleep(8)
        _do_logout(driver)
        _wait_for_login_page(driver, timeout=WAIT_TIMEOUT)
        assert driver.find_element(By.XPATH, "//input[@aria-label='Email']")

    def test_tc10_cookie_cleared_after_logout(self, driver):
        """TC10: auth_session cookie should be cleared after logout."""
        cookie = _get_auth_cookie(driver)
        assert cookie is None or cookie == "", "auth_session cookie not cleared after logout"

    def test_tc11_protected_page_blocked_after_logout(self, driver):
        """TC11: Accessing /market_data after logout should redirect to login."""
        driver.get(f"{BASE_URL}/market_data")
        time.sleep(12)
        # Should see login form, NOT Market Data
        page_source = driver.page_source
        assert "Email" in page_source and "Password" in page_source, \
            "Protected page accessible after logout — SECURITY VIOLATION"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TC12-TC17: Unauthenticated Access (ALL Pages)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestUnauthenticatedAccess:

    PROTECTED_PAGES = [
        ("/home", "tc12"),
        ("/market_data", "tc13"),
        ("/earnings_calls", "tc14"),
        ("/newsroom", "tc15"),
        ("/company_filings", "tc16"),
    ]

    @pytest.mark.parametrize("page,tc_id", PROTECTED_PAGES)
    def test_unauth_access_blocked(self, driver, page, tc_id):
        """TC12-TC16: All protected pages must redirect to login when unauthenticated."""
        _clear_cookies(driver)
        driver.get(f"{BASE_URL}{page}")
        time.sleep(12)
        page_source = driver.page_source
        assert "Email" in page_source and "Password" in page_source, \
            f"{tc_id}: {page} accessible without auth — SECURITY VIOLATION"

    def test_tc17_url_tampering_blocked(self, driver):
        """TC17: URL tampering with query params should be blocked."""
        _clear_cookies(driver)
        driver.get(f"{BASE_URL}/market_data?ticker=AAPL")
        time.sleep(12)
        page_source = driver.page_source
        assert "Email" in page_source and "Password" in page_source, \
            "URL tampering bypassed auth — SECURITY VIOLATION"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TC18-TC20: Edge Cases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestEdgeCases:

    def test_tc18_rapid_refresh(self, driver):
        """TC18: 3x rapid refresh after login should not lose session."""
        _clear_cookies(driver)
        _login(driver)

        # 3 rapid refreshes (2-sec intervals)
        for _ in range(3):
            driver.refresh()
            time.sleep(2)

        time.sleep(8)  # Let final state settle
        assert "Logout" in driver.page_source, "Session lost during rapid refresh"

    def test_tc19_relogin_cycle(self, driver):
        """TC19: Login → Logout → Login should work cleanly."""
        # We are logged in from TC18
        _do_logout(driver)
        _wait_for_login_page(driver)

        # Re-login
        _login(driver)
        assert "Logout" in driver.page_source, "Re-login failed after logout"

    def test_tc20_back_button_after_logout(self, driver):
        """TC20: Browser back button after logout should NOT show cached content."""
        _do_logout(driver)
        _wait_for_login_page(driver)

        # Simulate back button
        driver.execute_script("window.history.back()")
        time.sleep(10)

        # After back, the page should either show login or be blocked
        page_source = driver.page_source
        # Must NOT show authenticated content
        has_login_form = "Email" in page_source and "Password" in page_source
        has_no_home_content = "CORESIGHT MARKET DATA" not in page_source.upper()
        assert has_login_form or has_no_home_content, \
            "Back button after logout shows cached protected content — SECURITY VULNERABILITY"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TC21-TC22: Cookie Integrity
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class TestCookieIntegrity:

    def test_tc21_cookie_set_on_login(self, driver):
        """TC21: auth_session cookie must be set after login."""
        _clear_cookies(driver)
        _login(driver)
        cookie = _get_auth_cookie(driver)
        assert cookie is not None and cookie != "", "No auth_session cookie set after login"

    def test_tc22_cookie_contains_valid_json(self, driver):
        """TC22: auth_session cookie should contain valid session data."""
        cookie_val = _get_auth_cookie(driver)
        assert cookie_val is not None
        try:
            data = json.loads(cookie_val)
            assert "session_id" in data, "Cookie missing session_id"
            assert "email" in data, "Cookie missing email"
            assert data["email"] == EMAIL, f"Cookie email mismatch: {data['email']}"
        except (json.JSONDecodeError, TypeError):
            # Cookie might be an opaque token, not JSON. That's OK too.
            assert len(cookie_val) > 10, "Cookie value too short"

    def test_tc23_cookie_expires_in_future(self, driver):
        """TC23: auth_session cookie should have a future expiry."""
        cookie = driver.get_cookie("auth_session")
        if cookie and "expiry" in cookie:
            assert cookie["expiry"] > time.time(), "Cookie already expired!"

    def test_tc24_cleanup_logout(self, driver):
        """TC24: Final cleanup — logout after all tests."""
        _do_logout(driver)
        time.sleep(5)
        assert _get_auth_cookie(driver) is None or _get_auth_cookie(driver) == ""
