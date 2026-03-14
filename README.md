# Homework 6 - Comments Service (Улучшения и Docker)

## Описание проекта
Django REST API сервис для управления постами, комментариями и лайками с улучшенной функциональностью.

### Запуск через Docker
```bash
# Перейдите в папку с docker-compose
cd storage/docker

# Запустите контейнеры
docker-compose up --build

# Приложение будет доступно:
# - API: http://localhost:8000
# - Swagger: http://localhost:8000/swagger/
# - Admin: http://localhost:8000/admin/
```


## Применение миграций

### 1. Миграции базы данных
```bash
# Перейдите в папку с Django проектом
cd django_proj

# Создайте миграции (если есть изменения в моделях)
python manage.py makemigrations

# Примените миграции (включая мок данные)
python manage.py migrate
```

### 2. Мок данные (тестовое наполнение)
Миграции автоматически создадут тестовые данные:
- 4 пользователя (пароль для всех: `password123`)
- 4 поста
- Комментарии и лайки

### 3. Проверка миграций
```bash
# Проверьте статус миграций
python manage.py showmigrations

# Откат миграций (если нужно)
python manage.py migrate comments zero
```

### 4. Через Makefile
```bash
make migrate  # создаст и применит все миграции
```

### 5. Через Docker
```bash
cd storage/docker
docker-compose up --build  # миграции применятся автоматически
```

### Важно
- Миграции должны применяться **строго по порядку**
- При первом запуске обязательно выполнить `migrate`
- Мок данные создаются **автоматически** при миграции


## Homework 7 - Comments Service (Авторизация, тесты и Docker)

### Новые возможности:

#### Авторизация и права доступа
- Регистрация: `POST /api/auth/register/`
- Вход: `POST /api/auth/login/`
- Информация о себе: `GET /api/auth/me/`
- JWT токены для аутентификации

#### Права доступа
- Все могут читать посты и комментарии
- Только автор может редактировать/удалять свои посты и комментарии
- Администраторы могут редактировать/удалять всё
- Лайки могут ставить только авторизованные пользователи

#### Тесты
```bash
# Запуск тестов локально
cd django_proj
python manage.py test comments

# Запуск тестов в Docker
cd storage/docker
docker-compose --profile test run test
```

#### Docker Compose
```bash
# Запуск всего приложения
cd storage/docker
docker-compose up --build

# Запуск только тестов
docker-compose --profile test run test

# Запуск в фоне
docker-compose up -d

# Остановка
docker-compose down
```
## Домашние работы:
- HW1: Python Practice
- HW4: Python Practice
- HW5: Comment Service
