from playwright.sync_api import sync_playwright
import time

def login(user_data_dir, correo_login, contraseña):
    """Inicia sesión en el sistema usando Playwright y devuelve la página autenticada."""
    p = sync_playwright().start()
    context = p.chromium.launch_persistent_context(user_data_dir=user_data_dir, channel="msedge", headless=False)
    page = context.new_page()
    page.goto("https://evirtual.utm.edu.ec", wait_until="domcontentloaded")
    time.sleep(2)
    
    # Completar el formulario de login
    page.fill("input[name='username']", correo_login)
    page.fill("input[name='password']", contraseña)
    page.click("button[type='submit']")
    
    # Esperar a que se autentique
    page.wait_for_selector("#page-header", timeout=10000)
    
    return page
