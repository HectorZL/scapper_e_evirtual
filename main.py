from config import load_credentials
from auth import login
from course_scraper import scrape_course_data
from utils import get_user_data_dir, validate_course_url
import os

def main():
    # Cargar las credenciales
    correo_login, contraseña = load_credentials('credenciales.data')
    
    # Solicitar la URL del curso hasta que sea válida
    while True:
        url_curso = input("Por favor, ingrese la URL del curso: ")
        if validate_course_url(url_curso):
            break
        else:
            print("La URL ingresada no tiene el formato correcto. Inténtelo de nuevo.")
    
    # Obtener el directorio de usuario
    user_data_dir = get_user_data_dir()

    # Iniciar sesión y scrapeo
    with login(user_data_dir, correo_login, contraseña) as page:
        scrape_course_data(page, url_curso)

if __name__ == "__main__":
    main()
