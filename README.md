# Learning Log
---

## 🛠 Стек технологий

- **Язык**: Python 3.12 / 3.10+
- **Фреймворк**: Django 5.x
- **UI / Стили**: Bootstrap 4 (`django-bootstrap4`)
- **Статика**: WhiteNoise
- **WSGI-сервер**: Gunicorn
- **База данных**: SQLite (хранится в постоянном Docker volume)
- **Контейнеризация**: Docker & Docker Compose

---

## 📁 Структура проекта

```text
.
├── compose.yaml                # Спецификация Docker Compose для сборки и запуска
├── Dockerfile                  # Инструкция сборки Docker-образа (на базе python:3.12-slim)
├── .env.example                # Пример переменных окружения для сервера
├── .gitignore                  # Исключения для Git (.env, ll_env, db.sqlite3 и т.д.)
├── .dockerignore               # Исключения для Docker
├── requirements.txt            # Зависимости Python
├── README.md                   # Руководство по развертыванию и запуску
├── manage.py                   # Главный скрипт управления Django
├── learning_log/               # Основной пакет конфигурации проекта
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Настройки проекта (интеграция с .env, WhiteNoise)
│   ├── urls.py                 # Главные маршруты URL
│   └── wsgi.py
├── learning_logs/              # Приложение журнала (темы и записи)
│   ├── admin.py                # Регистрация моделей Topic и Entry в админке
│   ├── forms.py                # Формы TopicForm и EntryForm
│   ├── models.py               # Модели Topic и Entry (с привязкой к User)
│   ├── urls.py                 # Маршруты приложения тем
│   ├── views.py                # Контроллеры с разграничением прав (@login_required, 404)
│   ├── tests.py                # Модульные тесты
│   └── templates/learning_logs/
│       ├── base.html           # Базовый шаблон со стилями Bootstrap
│       ├── index.html          # Домашняя страница
│       ├── topics.html         # Список тем пользователя
│       ├── topic.html          # Детальная страница темы и записи
│       ├── new_topic.html      # Форма создания новой темы
│       ├── new_entry.html      # Форма создания новой записи
│       └── edit_entry.html     # Форма редактирования записи
└── users/                      # Приложение авторизации и пользователей
    ├── urls.py                 # Маршруты входа, выхода и регистрации
    ├── views.py                # Контроллер регистрации
    ├── tests.py                # Тесты авторизации
    └── templates/registration/
        ├── login.html          # Страница входа
        ├── logged_out.html     # Страница выхода
        └── register.html       # Страница регистрации
```

---

## 🔑 Переменные окружения (`.env`)

Для запуска на сервере или локально создайте файл `.env` в корне проекта (скопировав из `.env.example`):

```bash
cp .env.example .env
```

| Переменная | Описание | Пример значения |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | Секретный ключ Django (для продакшна обязательно задать уникальный длинный ключ) | `my-secure-random-key` |
| `DJANGO_DEBUG` | Режим отладки (`True` для разработки, `False` на сервере) | `False` |
| `DJANGO_ALLOWED_HOSTS` | Список разрешённых хостов/IP через запятую | `192.168.1.11,localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Доверенные источники для защиты от CSRF | `http://192.168.1.11:8000` |
| `DJANGO_USE_HTTPS` | Включение безопасных кук и протокола HTTPS (`True`/`False`) | `False` |
| `SQLITE_PATH` | Путь к файлу базы данных внутри контейнера | `/app/data/db.sqlite3` |
| `APP_BIND_IP` | IP-адрес для привязки сервиса на хосте | `0.0.0.0` |
| `APP_PORT` | Внешний порт на сервере | `8000` |

---

## 🚀 Развёртывание на сервере через Docker Compose

### 1. Клонирование репозитория

```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd <ПАПКА_РЕПОЗИТОРИЯ>
```

### 2. Настройка `.env`

Создайте файл `.env` и настройте параметры (укажите IP сервера и выделенный порт):

```bash
cp .env.example .env
nano .env
```

### 3. Сборка и запуск контейнеров

Запустите контейнер в фоновом режиме:

```bash
docker compose up -d --build
```

Проверьте статус запущенных контейнеров:

```bash
docker compose ps
```

Просмотр логов:

```bash
docker compose logs --tail=100 web
```

### 4. Создание учетной записи администратора

После успешного старта выполните команду внутри контейнера:

```bash
docker compose exec web python manage.py createsuperuser
```

Следуйте подсказкам в консоли для ввода логина, e-mail и пароля.

### 5. Проверка работы

Откройте приложение в браузере по адресу:
`http://<IP_СЕРВЕРА>:<APP_PORT>/` (например, `http://192.168.1.11:8000/`)

Панель администратора: `http://<IP_СЕРВЕРА>:<APP_PORT>/admin/`

---

## 💻 Локальный запуск без Docker (для разработки)

1. Создайте и активируйте виртуальное окружение:
   ```bash
   python3 -m venv ll_env
   source ll_env/bin/activate   # На Linux/macOS
   # или .\ll_env\Scripts\activate на Windows
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Примените миграции:
   ```bash
   python manage.py migrate
   ```

4. Запустите сервер разработки:
   ```bash
   python manage.py runserver
   ```
   Приложение будет доступно по адресу `http://127.0.0.1:8000/`.

5. Запуск тестов:
   ```bash
   python manage.py test
   ```
