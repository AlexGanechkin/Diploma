# Дипломный проект "Планировщик целей" (GoalTracker)
Стек: python3.11, Django, Postgres
## Этап 1 Настройка проекта
1.1. Устанавливаем библиотеки (pip install ...):
- (...django);
- (...psycopg2-binary);
прим. либо устанавливаем все библиотеки списком (pip install -r requirements.txt)
1.2 Создаем проект (django-admin startproject *имя проекта*)
1.3. Создаем Git-репозитарий в github.com
1.4. Инициируем Git-репозитарий в проекте (git init .)
git add .
git status
git restore --staged *папка/файл*
git commit -m 'description'
1.4. Создаем файл .gitignore (в корне проекта), в него включаем ресрусы проекта, которые не будут переноситься в репозитарий


Рекомендуется подключить проверщики: black/mypy/isort/flake8

### Как выкладываем на Гит:
Делаем пуш в текущую ветку (git push origin HEAD -f)
Создаем pull request (трекинг изменений в ветке по сравнению с главной веткой) - create pull request в github
Если нужно добавить изменения в коммит без нового коммита (git commit --amend --no-edit)
После всех исправлений делаем в pull request rebase and merge (сливаем с основной веткой)
В локальном репозитории:
- подтягиваем основную ветку (git switch main, git fetch, git pull)
- делаем новую ветку (git switch -c *название ветки*)


sudo usermod -aG docker имя_пользователя 