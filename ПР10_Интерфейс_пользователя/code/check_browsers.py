"""Проверка интерфейса в Chrome и Firefox на запущенном учебном стенде."""
import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def viewport(driver, width, height):
    driver.set_window_size(width, height)
    for _ in range(3):
        inner = driver.execute_script('return [innerWidth, innerHeight]')
        outer = driver.get_window_size()
        if inner == [width, height]:
            break
        driver.set_window_size(outer['width'] + width - inner[0],
                               outer['height'] + height - inner[1])
    assert driver.execute_script('return [innerWidth, innerHeight]') == [width, height]


def capture(driver, output, name):
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script('return document.readyState') == 'complete')
    driver.execute_async_script('document.fonts.ready.then(() => arguments[0]())')
    driver.save_screenshot(str(output / name))
    return driver.execute_script('''return {
        width: innerWidth, height: innerHeight,
        scroll_width: document.documentElement.scrollWidth,
        horizontal_overflow: document.documentElement.scrollWidth > innerWidth
    }''')


def check(base_url, output):
    output = Path(output)
    (output / 'img').mkdir(parents=True, exist_ok=True)
    results = []
    for browser in ('chrome', 'firefox'):
        if browser == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
            driver = webdriver.Chrome(options=options)
        else:
            options = webdriver.FirefoxOptions()
            options.add_argument('-headless')
            driver = webdriver.Firefox(options=options)
        try:
            wait = WebDriverWait(driver, 10)
            prefix = 'chromium' if browser == 'chrome' else 'firefox'
            first = '04' if browser == 'chrome' else '06'
            validation = '05' if browser == 'chrome' else '07'
            viewport(driver, 1366, 900)
            driver.get(base_url + '/')
            home = capture(driver, output / 'img', f'{first}_{prefix}_desktop_home.png')
            assert len(driver.find_elements(By.CSS_SELECTOR, '[data-testid="room-card"]')) == 3
            driver.get(base_url + '/register')
            driver.find_element(By.CSS_SELECTOR, '#register-form button[type=submit]').click()
            errors = wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, '.field.has-error'))
            assert len(errors) == 5
            capture(driver, output / 'img', f'{validation}_{prefix}_validation.png')
            driver.get(base_url + '/login')
            driver.find_element(By.ID, 'login').send_keys('ivanov01')
            driver.find_element(By.ID, 'password').send_keys('Password1')
            driver.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
            wait.until(lambda d: d.current_url.endswith('/dashboard'))
            assert driver.find_element(By.TAG_NAME, 'h1').text == 'Мои заявки'
            if browser == 'firefox':
                capture(driver, output / 'img', '08_firefox_my_requests.png')
            driver.get(base_url + '/requests/new')
            driver.find_element(By.CSS_SELECTOR, '#room_id option[value="1"]').click()
            driver.find_element(By.CSS_SELECTOR, '#payment_method_id option[value="2"]').click()
            driver.find_element(By.ID, 'start_at').send_keys('05.11.2030 10:00')
            if browser == 'firefox':
                capture(driver, output / 'img', '09_firefox_new_request.png')
            mobile = {}
            if browser == 'chrome':
                viewport(driver, 390, 844)
                for path, name in [('/', '01_mobile_home.png'),
                                   ('/register', '02_mobile_registration.png')]:
                    # Регистрация доступна только гостю, поэтому завершаем сессию.
                    if path == '/register':
                        driver.delete_all_cookies()
                    driver.get(base_url + path)
                    mobile[path] = capture(driver, output / 'img', name)
                driver.get(base_url + '/login')
                driver.find_element(By.ID, 'login').send_keys('ivanov01')
                driver.find_element(By.ID, 'password').send_keys('Password1')
                driver.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
                wait.until(lambda d: d.current_url.endswith('/dashboard'))
                driver.get(base_url + '/requests/new')
                mobile['/requests/new'] = capture(driver, output / 'img', '03_mobile_new_request.png')
                assert all(not item['horizontal_overflow'] for item in mobile.values())
            js_errors = None
            if browser == 'chrome':
                js_errors = [entry for entry in driver.get_log('browser')
                             if entry.get('source') == 'javascript' and entry['level'] == 'SEVERE']
                assert not js_errors, js_errors
            results.append({
                'browser': driver.capabilities['browserName'],
                'version': driver.capabilities['browserVersion'],
                'checked_at': datetime.now(timezone.utc).isoformat(),
                'platform': platform.platform(), 'desktop': home,
                'mobile': mobile or None, 'empty_registration_errors': len(errors),
                'page_errors': js_errors,
                'page_errors_method': 'Chrome browser log' if js_errors is not None else 'not collected',
                'checked_paths': ['/', '/register', '/login', '/dashboard', '/requests/new'],
            })
        finally:
            driver.quit()
    (output / 'browser_checks.json').write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:5000')
    parser.add_argument('--output', type=Path, default=Path('browser-evidence'))
    args = parser.parse_args()
    check(args.base_url.rstrip('/'), args.output)
