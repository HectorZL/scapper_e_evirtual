import os
import csv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time

# Cargar correo y contraseña desde archivo.data
with open('credenciales.data', 'r') as f:
    correo_login = f.readline().strip()
    contraseña = f.readline().strip()

def enviar_mensaje(page, userid, mensaje):
    """Función para enviar un mensaje a un usuario usando Playwright."""
    # Navegar a la página de mensajes del usuario
    url_mensaje = f"https://evirtual.utm.edu.ec/message/index.php?id={userid}"
    page.goto(url_mensaje, wait_until="domcontentloaded")
    time.sleep(2)  # Esperar que la página cargue completamente

    # Escribir el mensaje en el área de texto
    textarea = page.query_selector('textarea[data-region="send-message-txt"]')
    if textarea:
        textarea.fill(mensaje)
        time.sleep(1)  # Esperar un momento antes de enviar

        # Hacer clic en el botón de enviar
        boton_enviar = page.query_selector('button[data-action="send-message"]')
        if boton_enviar:
            boton_enviar.click()
            time.sleep(1)  # Esperar un segundo tras enviar
        else:
            print(f"Botón de enviar no encontrado para el usuario {userid}.")
    else:
        print(f"Área de texto no encontrada para el usuario {userid}.")

def main():
    # URL de la página de inicio de sesión
    url_login = "https://evirtual.utm.edu.ec"

    # URL de la página del curso
    url_curso = "https://evirtual.utm.edu.ec/user/index.php?id=1234"

    # Crear una instancia de Playwright
    with sync_playwright() as p:
        # Lanzar el navegador Microsoft Edge en modo headless con directorio de datos de usuario
        context = p.chromium.launch_persistent_context(user_data_dir="C:\\Users\\HectorZL\\AppData\\Local\\Microsoft\\Edge\\User Data", channel="msedge", headless=False)
        page = context.new_page()

        # Navegar a la página de inicio de sesión
        page.goto(url_login, wait_until="domcontentloaded")
        time.sleep(2)

        # Rellenar los campos de inicio de sesión
        page.fill("input[name='username']", correo_login)
        page.fill("input[name='password']", contraseña)
        time.sleep(1)
        page.click("button#loginbtn")

        # Esperar a que la página de inicio de sesión se cargue completamente
        page.wait_for_selector("#page-header", timeout=3000)

        # Navegar a la página del curso
        page.goto(url_curso, wait_until="domcontentloaded")
        time.sleep(3)

        # Hacer clic en el botón para mostrar 5000 estudiantes por página
        try:
            page.click("a[data-action='showcount'][href*='rpage=5000']")
        except Exception as e:
            print(f"Error al hacer clic en el botón para mostrar 5000 estudiantes por página: {e}")
        time.sleep(3)

        # Parsear el contenido HTML de la página
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Encontrar la tabla de participantes
        table = soup.find('table', {'id': 'participants'})
        if table is None:
            print("No se encontró la tabla con el ID 'participants'.")
            return

        data = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 2:
                continue
            nombre = cols[1].text.strip()
            enlace = cols[1].find('a')
            if enlace is not None:
                enlace = enlace['href']
            else:
                enlace = ""

            # Extraer el ID del usuario desde el enlace de perfil
            userid = enlace.split("id=")[-1] if "id=" in enlace else None
            if not userid:
                print(f"No se pudo extraer el ID del usuario desde el enlace {enlace}.")
                continue

            # Añadir los datos a la lista para procesamiento
            data.append({'Nombre': nombre, 'UserID': userid, 'Link Profile': enlace})

        # Mensaje a enviar a todos los usuarios
        mensaje = '''Buenas tardes companeros!

Le saluda el estudiante Hector del curso de Calculo en Varias Variables

Esto es un recordatorio para que ingrese al grupo de whattsap(Grupo de comunicacion)

link aqui abajo

Follow this link to join my WhatsApp group: https://chat.whatsapp.com/EqBnid6yapeDcphtxRYhS9

Sin mas , buena tarde!'''

        # Enviar mensajes a cada usuario
        for i, row in enumerate(data, 1):
            print(f"Enviando mensaje al usuario {row['Nombre']} (ID: {row['UserID']})...")
            enviar_mensaje(page, row['UserID'], mensaje)

        print("Mensajes enviados a todos los usuarios.")

if __name__ == "__main__":
    main()
