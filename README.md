# B2B Convenios

## Descripción
B2B Convenios es una plataforma que permite a las empresas asignar créditos a sus empleados de manera eficiente y segura. Con una amplia gama de características, esta aplicación busca facilitar la gestión de convenios empresariales.

## Características
- **Gestión para la creación de clientes**: Crea, edita y elimina clientes.
- **Autenticación Segura**: Acceso seguro mediante autenticación por medio de un usuario y una contraseña.
- **Interfaz de Usuario Intuitiva**: Facilita la gestión a través de una interfaz sencilla.

## Requisitos
- Python 3.8.10. Descarga [aquí](https://www.python.org/downloads/release/python-3810/). 
  - **Windows installer (64-bit)**

  - **Realizar una instalación personalizada, para que Python 3.8.10 se instale en la carpeta de preferencia.**
  Nota: Recordar donde se instala Python, ya que esa es la ruta que se debe usar para crear el entorno virtual.

  Para crear el entorno virtual, especifica la ruta con la versión de Python específica.
  Ejemplo:
  ```bash
  C:\Users\jramirez\AppData\Local\Programs\Python\Python38\python.exe -m venv env

  Activar el entorno virtual:
  ```bash
  env\Scripts\activate
  ```


## Instalación
### Clonar el repositorio
```bash
git clone https://github.com/sistemasimr/b2b-convenios.git
```

## Instalar dependencias
```bash
pip install -r requirements.txt
```

## Realizar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

## Correr el proyecto
```bash
python manage.py runserver 0.0.0.0:80
```

## Documentación
Para más detalles, revisar la Documentación Completa del proyecto en:
https://bigjohn.atlassian.net/l/cp/58CK1kFa
