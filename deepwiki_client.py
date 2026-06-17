from __future__ import annotations

import time
from urllib.parse import urlparse


class DeepWikiClient:
    def __init__(self, base_url: str, teardown: bool = True):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", not teardown)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(options=options, service=service)
        self.driver.implicitly_wait(50)
        self.base_url = base_url
        self.teardown = teardown

    def close(self) -> None:
        if self.teardown:
            self.driver.quit()

    def ask(self, prompt: str) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(self.driver, 1200)
        self.driver.get(self.base_url)
        form = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form")))
        textarea = form.find_element(By.CSS_SELECTOR, "textarea")
        self._toggle_deep_research()
        textarea.click()
        textarea.clear()
        self.driver.execute_script("arguments[0].value = arguments[1];", textarea, prompt)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", textarea)
        textarea.send_keys(".. ")
        textarea.send_keys(Keys.ENTER)
        time.sleep(10)
        return self.driver.current_url

    def collect_response(self, url: str) -> str | None:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        self.driver.get(url)
        wait = WebDriverWait(self.driver, 120)

        def page_ready(driver):
            if "/search/not-found" in driver.current_url:
                return "not_found"
            buttons = driver.find_elements(By.CSS_SELECTOR, '[aria-label="Copy"]')
            return buttons or False

        state = wait.until(page_ready)
        if state == "not_found":
            return None
        copy_buttons = state
        wait.until(EC.element_to_be_clickable(copy_buttons[-1])).click()
        menu_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem' and normalize-space(text())='Copy response']")))
        menu_item.click()
        time.sleep(1)
        content = self._read_browser_clipboard()
        if content:
            return content
        content = self._read_system_clipboard()
        if content:
            return content
        return self._read_visible_response_text(copy_buttons[-1])

    def _toggle_deep_research(self) -> None:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(self.driver, 20)
        try:
            button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[.//span[normalize-space(text())="Fast"]]')))
            button.click()
            menu_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem' and .//span[normalize-space(text())='Deep Research']]")))
            menu_item.click()
        except Exception:
            return

    def _read_browser_clipboard(self) -> str:
        origin = _origin_for_url(self.driver.current_url or self.base_url)
        try:
            self.driver.execute_cdp_cmd(
                "Browser.grantPermissions",
                {
                    "origin": origin,
                    "permissions": ["clipboardReadWrite", "clipboardSanitizedWrite"],
                },
            )
        except Exception:
            pass
        try:
            content = self.driver.execute_async_script(
                """
                const done = arguments[arguments.length - 1];
                if (!navigator.clipboard || !navigator.clipboard.readText) {
                  done("");
                  return;
                }
                navigator.clipboard.readText().then(
                  text => done(text || ""),
                  () => done("")
                );
                """
            )
        except Exception:
            return ""
        return str(content or "").strip()

    def _read_system_clipboard(self) -> str:
        try:
            import pyperclip

            return str(pyperclip.paste() or "").strip()
        except Exception:
            return ""

    def _read_visible_response_text(self, copy_button) -> str:
        try:
            content = self.driver.execute_script(
                """
                const button = arguments[0];
                const candidates = [];
                let node = button;
                for (let depth = 0; depth < 8 && node; depth += 1, node = node.parentElement) {
                  const text = (node.innerText || node.textContent || "").trim();
                  if (text.length > 50 && !text.includes("Copy response")) {
                    candidates.push(text);
                  }
                }
                for (const selector of ["main pre", "main code", "article", "main"]) {
                  for (const el of document.querySelectorAll(selector)) {
                    const text = (el.innerText || el.textContent || "").trim();
                    if (text.length > 50 && !text.includes("Copy response")) {
                      candidates.push(text);
                    }
                  }
                }
                candidates.sort((a, b) => b.length - a.length);
                return candidates[0] || "";
                """,
                copy_button,
            )
        except Exception:
            return ""
        return str(content or "").strip()


def _origin_for_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return "https://deepwiki.com"
