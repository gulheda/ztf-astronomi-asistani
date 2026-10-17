"""GitHub Actions visual smoke capture for the real ZTF archive mode."""
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import expect
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8501"


def wait_until_ready(process, timeout=20):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Streamlit exited before becoming ready")
        try:
            with urllib.request.urlopen(URL, timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.25)
    raise TimeoutError("Streamlit did not become ready within 20 seconds")


def main():
    output = ROOT / "output/ui"
    output.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, STREAMLIT_BROWSER_GATHER_USAGE_STATS="false")
    server = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true",
         "--server.address=127.0.0.1", "--server.port=8501"],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        wait_until_ready(server)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1050}, device_scale_factor=1)
                page.goto(URL, wait_until="networkidle", timeout=20000)
                source = page.get_by_role("combobox", name="Veri kaynağı")
                source.click()
                page.get_by_role("option", name="Gerçek ZTF arşivi", exact=True).click()
                page.get_by_text("GERÇEK ZTF ARŞİVİ:").wait_for(timeout=10000)
                page.wait_for_load_state("networkidle", timeout=10000)
                metric_value = page.locator('[data-testid="stMetricValue"]').first
                expect(metric_value).to_have_text("1", timeout=10000)
                page.locator('[data-testid="stDataFrame"]').wait_for(state="visible", timeout=10000)
                page.screenshot(path=str(output / "real-archive.png"), full_page=True)
                source.click()
                page.get_by_role("option", name="Demo", exact=True).click()
                page.get_by_text("DEMO:").wait_for(timeout=10000)
                page.wait_for_load_state("networkidle", timeout=10000)
                page.locator('[data-testid="stDataFrame"]').wait_for(state="visible", timeout=10000)
                page.screenshot(path=str(output / "demo.png"), full_page=True)
            finally:
                browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


if __name__ == "__main__":
    main()
