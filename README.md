# Django ToDo List App

## Description
Django ToDo List App is a web application for managing personal tasks. It provides a simple and efficient way to organize your to-do list.

## Main Features
- User authentication (registration, login, logout)
- Complete CRUD for tasks (Create, Read, Update, Delete)
- Mark tasks as completed
- Search and filter tasks by content
- Minimalist and functional user interface
- Multilingual support (English and Spanish)

## Project Structure
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

## Requirements
- Python 3.9+
- Django 5.1
- Other dependencies listed in `requirements.txt`

## Setup and Execution

1. Clone the repository:
   ```
   git clone https://github.com/PPeitsch/todo-django.git
   cd todo-django
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at `http://localhost:8000`

## Usage
- Register as a new user or log in if you already have an account.
- On the main page, you'll see your task list.
- Use the "Add New Task" button to create a new task.
- You can edit, delete, or mark each task as completed from the list.
- Use the search bar to filter tasks by title or description.

## Testing
To run unit and integration tests:
```
python manage.py test
```

## Contributions
Contributions are welcome. Please ensure you follow PEP 8 coding conventions and Django best practices.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact
For any questions or suggestions, please open an issue in this repository.