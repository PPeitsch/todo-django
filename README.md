# Django ToDo List App

## Descripción
Django ToDo List App es una aplicación web para la gestión de tareas personales.

## Características Principales
- Autenticación de usuarios (registro, inicio de sesión, cierre de sesión)
- CRUD completo para tareas (Crear, Leer, Actualizar, Eliminar)
- Marcado de tareas como completadas
- Búsqueda y filtrado de tareas por contenido
- Interfaz de usuario minimalista y funcional
- Manejo de logs para seguimiento de acciones (pendiente)

## Pendiente de implementación
- Manejo de logs para seguimiento de acciones.
- Tests unitarios y de integración.
- Imagen de Docker.

## Estructura del Proyecto
```
todo-django/
├── authentication/
│   ├── templates/
│   │   └── authentication/
│   │       ├── login.html
│   │       └── signup.html
├── tasks/
│   ├── templates/
│   │   └── tasks/
│   │       ├── home.html
│   │       ├── tasks_list.html
│   │       ├── tasks_form.html
│   │       └── tasks_confirm_delete.html
├── todo_list_project/
├── templates/
│   └── base.html
├── manage.py
├── requirements.txt
└── README.md
```

## Requisitos
- Python 3.9+
- Django 5.1
- Otras dependencias listadas en `requirements.txt`

## Configuración y Ejecución

1. Clonar el repositorio:
   ```
   git clone https://github.com/PPeitsch/todo-django.git
   cd todo-django
   ```

2. Crear y activar un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Aplicar las migraciones:
   ```
   python manage.py migrate
   ```

5. Crear un superusuario (opcional):
   ```
   python manage.py createsuperuser
   ```

6. Ejecutar el servidor de desarrollo:
   ```
   python manage.py runserver
   ```

7. Acceder a la aplicación en `http://localhost:8000`

## Uso
- Regístrate como nuevo usuario o inicia sesión si ya tienes una cuenta.
- En la página principal, podrás ver tu lista de tareas.
- Usa el botón "Añadir Nueva Tarea" para crear una nueva tarea.
- Puedes editar, eliminar o marcar como completada cada tarea desde la lista.
- Utiliza la barra de búsqueda para filtrar tareas por título o descripción.

## Pruebas
Para ejecutar las pruebas unitarias y de integración:
```
python manage.py test
```

## Contribuciones
Las contribuciones son bienvenidas. Por favor, asegúrese de seguir las convenciones de codificación de PEP 8 y las mejores prácticas de Django.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulte el archivo `LICENSE` para más detalles.

## Contacto
Para cualquier pregunta o sugerencia, por favor abra un issue en este repositorio.