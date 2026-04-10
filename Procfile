web: gunicorn main.main.wsgi:application --chdir main
worker: python main/manage.py firebase_listener
