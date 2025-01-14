from bs4 import BeautifulSoup
import time
import csv

def scrape_course_data(page, url_curso):
    """Navega al curso y extrae los datos de los estudiantes."""
    page.goto(url_curso, wait_until="domcontentloaded")
    time.sleep(1)
    
    # Intentar hacer clic en el botón para mostrar todos los estudiantes
    try:
        page.click("a[data-action='showcount']", timeout=20000)
        time.sleep(2)  # Espera adicional para que la página cargue completamente
    except Exception as e:
        print("No se pudo expandir la lista a más estudiantes. Continuando con la lista predeterminada.")

    # Parsear el contenido de la página después de hacer clic en "Mostrar 40"
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    enlaces_estudiantes = soup.find_all('a', href=lambda x: x and 'user/view.php?id=' in x)

    # Verificar si la lista contiene 40 estudiantes ahora
    if len(enlaces_estudiantes) < 40:
        print("Advertencia: No se cargaron los 40 estudiantes. Verifique si el botón 'Mostrar' funciona correctamente.")
    
    # Procesar cada estudiante y guardar en CSV
    data = []
    total_estudiantes = len(enlaces_estudiantes)
    for i, enlace in enumerate(enlaces_estudiantes, start=1):
        page.goto(enlace['href'], wait_until="domcontentloaded")
        time.sleep(1)
        
        # Obtener correo electrónico
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        correo_estudiante = soup.find('a', href=lambda x: x and x.startswith('mailto:'))
        correo = correo_estudiante.text if correo_estudiante else ""
        
        # Procesar nombre y apellidos en el formato requerido
        nombre_completo = enlace.text.strip()
        
        # Eliminar las dos primeras letras del nombre completo
        nombre_completo = nombre_completo[2:]
        
        # Separar el nombre completo en palabras y dividir en apellidos y nombre
        partes = nombre_completo.split()
        apellido = ' '.join(partes[-2:])  # Últimos dos elementos como apellido
        nombre = ' '.join(partes[:-2])    # Resto como nombre
        nombre_formato = f"{apellido} {nombre}"
        
        # Agregar a datos
        data.append({'n': i, 'Nombre Completo': nombre_formato, 'Correo': correo})
        
        # Mostrar el progreso y sobreescribir la línea anterior
        print(f"\rProcesando estudiante {i} de {total_estudiantes} ({(i / total_estudiantes) * 100:.2f}%)", end="")

    print("\nProceso completado.")
    save_to_csv(data)

def save_to_csv(data):
    """Guarda los datos de los estudiantes en un archivo CSV."""
    with open('course_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['n', 'Nombre Completo', 'Correo']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
