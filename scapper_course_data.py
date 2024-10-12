import os
import csv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time

# Cargar correo y contraseña desde archivo.data
with open('credenciales.data', 'r') as f:
    correo_login = f.readline().strip()  # Renombrar variable para evitar conflicto
    contraseña = f.readline().strip()

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
        time.sleep(2)  # Esperar 2 segundos

        # Rellenar los campos de inicio de sesión
        page.fill("input[name='username']", correo_login)  # Usar la variable renombrada
        page.fill("input[name='password']", contraseña)
        
        time.sleep(1)  # Esperar 1 segundo
        
        # Hacer clic en el botón de inicio de sesión
        page.click("button#loginbtn")

        # Esperar a que la página de inicio de sesión se cargue completamente
        page.wait_for_selector("#page-header", timeout=3000)

        # Navegar a la página del curso
        page.goto(url_curso, wait_until="domcontentloaded")
        time.sleep(3)  # Esperar 3 segundos

        # Hacer clic en el botón para mostrar 5000 estudiantes por página
        try:
            page.click("a[data-action='showcount'][href*='rpage=5000']")
        except Exception as e:
            print(f"Error al hacer clic en el botón para mostrar 5000 estudiantes por página: {e}")

        # Esperar a que la tabla se actualice con los 5000 estudiantes
        time.sleep(3)
        
        # Espera adicional para que la tabla se cargue
        page.wait_for_selector("#participants", timeout=3000)

        # Parsear el contenido HTML de la página
        html = page.content()

        soup = BeautifulSoup(html, 'html.parser')

        # Encontrar la tabla
        table = soup.find('table', {'id': 'participants'})

        if table is None:
            print("No se encontró la tabla con el ID 'participants'.")
            return

        data = []
        for row in table.find_all('tr')[1:]:  # Saltar la fila de encabezado
            cols = row.find_all(['td', 'th'])
            if len(cols) < 2:
                continue
            nombre = cols[1].text.strip()
            if nombre.startswith("Seleccionar '"):
                nombre = nombre.replace("Seleccionar '", "").replace("'", "")
            if not nombre:  # Agregar esta condición para evitar nombres vacíos
                continue
            # Eliminar los dos caracteres adicionales al comienzo
            nombre = nombre[2:]
            # Separar el nombre en palabras
            palabras = nombre.split(' ')
            # Ordenar el nombre de manera que el apellido vaya primero
            apellido = ' '.join(palabras[-2:])
            nombre = ' '.join(palabras[:-2])
            # Unir el apellido y el nombre
            nombre = f"{apellido} {nombre}"
            enlace = cols[1].find('a')
            if enlace is not None:
                enlace = enlace['href']
            else:
                enlace = ""
            
            # Extraer el correo electrónico desde la página de perfil
            page.goto(enlace, wait_until="domcontentloaded")
            time.sleep(2)
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            correo_estudiante = soup.find('a', href=lambda x: x and x.startswith('mailto:'))  # Renombrar variable aquí
            if correo_estudiante:
                correo_estudiante = correo_estudiante.text
            else:
                correo_estudiante = ""
            
            data.append({'Nombre': nombre, 'Link Profile': enlace, 'Correo': correo_estudiante})  # Cambiar nombre a correo_estudiante
        
        # Crear un archivo CSV y escribir los datos
        with open('course_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['n', 'Nombre', 'Link Profile', 'Correo']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i, row in enumerate(data, 1):
                writer.writerow({'n': i, 'Nombre': row['Nombre'], 'Link Profile': row['Link Profile'], 'Correo': row['Correo']})

if __name__ == "__main__":
    main()
