# Дипломный проект "Планировщик целей" (GoalTracker)
Стек: python3.11, Django, Postgres
## Этап 1 Запуск проекта
1.1. Клонируем образ проекта из github (git clone *ссылка на репозиторий*)
1.2. Создаем виртуальное окружение (python -m venv venv)
1.2. Устанавливаем библиотеки (pip install -r requirements.txt)
1.3. Создаем .env файл в корне проекта, необходимо указать следующие переменные:
- DJANGO_SECRET_KEY='secret_key'
- DEBUG=True
- DB_USER=*логин пользователя*
- DB_PASSWORD=*пароль пользователя к БД*
- DB_NAME=*наименование БД*
1.4. Создаем образ БД и запускаем БД (docker-compose up -d)
1.5. Создаем и накатываем миграции (python manage.py makemigrations, python manage.py migrate)
1.6. Запускаем приложение (python manage.py runserver)
В результате по адресу http://127.0.0.1:8000/ должна появиться приветственная страница Django 
_The install worked successfully! Congratulations!_
1.7. Создаем учетную запись администратора (python manage.py createsuperuser), которая доступна по ссылке http://127.0.0.1:8000/admin/