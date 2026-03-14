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
```
## Домашние работы:
- HW1: Python Practice
- HW4: Python Practice
- HW5: Comment Service
