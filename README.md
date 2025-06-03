# 🥘 Foodgram — «Продуктовый помощник»

## 📌 Описание проекта

**Foodgram** — это веб-приложение, в котором пользователи могут публиковать рецепты, добавлять их в избранное, формировать список покупок и подписываться на других пользователей. Перед походом в магазин можно скачать список необходимых ингредиентов.

Проект включает:

* Frontend на **React**
* Backend на **Django + Django REST Framework**
* Использует **PostgreSQL**, **Docker**, **Nginx**

---

## ⚙️ Функциональность

* Регистрация и авторизация пользователей
* Создание, редактирование и удаление рецептов
* Добавление рецептов в избранное
* Создание списка покупок из ингредиентов рецептов
* Подписки на других пользователей
* Фильтрация рецептов по тегам
* Загрузка аватара
* Генерация PDF-файла с продуктами

---

## 🧱 Структура проекта

```
├── backend/          # Django-приложение (сервер)
├── frontend/         # React-приложение (клиент)
├── infra/            # Docker и конфигурации инфраструктуры
└── docs/             # Документация по API
```

---

## 📁 Переменные окружения (`.env`)

Пример наполнения `.env` файла:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=foodgram
DB_PORT=5432
DB_HOST=db

SECRET_KEY= ваш секретный ключ
```

Создайте файл `.env` на основе шаблона:

```bash
cp infra/
nano .env
# Далее заполните файл по шаблону
```

---

## 🚀 Установка и запуск

### 🔧 Требования

* Установленные Docker и Docker Compose

### 📦 Запуск в контейнерах

1. Клонировать репозиторий:

```bash
git clone https://github.com/antbtv/foodgram-st.git
cd foodgram-st/infra/
```

2. Запустить контейнеры:

```bash
# Для Linux используйте sudo 
docker-compose up -d --build
```

3. Применить миграции:

```bash
# Для Linux используйте sudo 
docker-compose exec backend python manage.py migrate
```

4. Добавить данные в базу данных:

```bash
# Для Linux используйте sudo 
docker-compose exec backend python manage.py shell 

exec(open("test_media/load_test_ingredients.py").read())
```

5. Создать суперпользователя:

```bash
# Для Linux используйте sudo 
docker-compose exec backend python manage.py createsuperuser
```

---

## 📚 Документация по API

Документация доступна после запуска по адресу:
**`http://127.0.0.1/api/docs/`**

OpenAPI-схема: `docs/openapi-schema.yml`

Также в проекте есть Postman-коллекция:
`postman_collection/foodgram.postman_collection.json`


Для очистки базы данных следует применить следующую команду:
```bash
# Для Linux используйте sudo 
docker-compose exec backend bash -c "chmod +x /app/postman_collection/clear_db.sh && /app/postman_collection/clear_db.sh"
```
---

## 👨‍💻 Автор

* 🧑‍💻 **ant_btv** — Backend-разработчик

---

## Контакты
Для вопросов: antonbut48@gmail.com