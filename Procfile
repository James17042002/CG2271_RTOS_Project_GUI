web: bash -c "cd main && gunicorn main.wsgi:application"
worker: bash -c "cd main && python manage.py firebase_listener"
