from bs4 import BeautifulSoup
import time
import csv

def scrape_course_data(page, url_curso):
    """Navega al curso y extrae los datos de los estudiantes."""
    page.goto(url_curso, wait_until="domcontentloaded")
    time.sleep(2)
    
    # Intentar mostrar 5000 estudiantes por página si es posible
    try:
        page.click("a[data-action='showcount'][href*='rpage=5000']", timeout=30000)
    except Exception as e:
        print("No se pudo expandir la lista a 5000 estudiantes. Continuando con la lista predeterminada.")
    
    # Parsear el contenido de la página
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    enlaces_estudiantes = soup.find_all('a', href=lambda x: x and 'user/view.php?id=' in x)

    # Procesar cada estudiante y guardar en CSV
    data = []
    total_estudiantes = len(enlaces_estudiantes)
    for i, enlace in enumerate(enlaces_estudiantes, start=1):
        page.goto(enlace['href'], wait_until="domcontentloaded")
        time.sleep(2)
        
        # Obtener correo electrónico
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        correo_estudiante = soup.find('a', href=lambda x: x and x.startswith('mailto:'))
        correo = correo_estudiante.text if correo_estudiante else ""
        
        # Procesar nombre y apellidos en el formato requerido
        nombre_completo = enlace.text.strip()
        partes = nombre_completo.split()
        apellido = ' '.join(partes[:2])  # Primeros dos elementos como apellido
        nombre = ' '.join(partes[2:])  # Resto como nombre
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
