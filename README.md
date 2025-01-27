
# **BotAvtoTG**

BotAvtoTG — это телеграм-бот для взаимодействия с пользователями, администрирования и управления объявлениями о продаже автомобилей.

## 🚀 **Функционал**

- **Регистрация и аутентификация пользователей**  
  Удобная регистрация новых пользователей и сохранение их данных.
  
- **Добавление объявлений**  
  Пользователи могут создавать и управлять своими объявлениями.

- **Панель администратора**  
  Возможность проверки и модерации объявлений.

- **Загрузка и хранение фотографий**  
  Поддержка работы с фотографиями через Yandex.Disk.

- **Ограничение запросов**  
  Использование rate limiter для предотвращения спама.

- **Гибкое меню и кнопки**  
  Реализация удобной навигации через кнопки в телеграм-боте.

## 🛠️ **Технологический стек**

- **Python**  
  Основной язык разработки.
  
- **Aiogram**  
  Фреймворк для создания телеграм-бота.
  
- **PostgreSQL**  
  Для работы с базой данных.
  
- **Docker**  
  Для контейнеризации и развертывания.

- **Yandex.Disk API**  
  Для работы с облачным хранилищем.

## 📂 **Структура проекта**

```
BotAvtoTG/
│
├── application/
│   ├── bot.py                     # Основной файл бота
│   ├── button/                    # Работа с кнопками
│   │   └── button_menu.py
│   ├── db/                        # Работа с базой данных
│   │   ├── database.py
│   │   ├── database_cars.py
│   │   └── database_users.py
│   ├── handlers/                  # Обработчики команд и событий
│   │   ├── admin_handler.py
│   │   ├── base_handler.py
│   │   ├── button_callback.py
│   │   ├── message.py
│   │   ├── newad.py
│   │   ├── photo.py
│   │   ├── profile.py
│   │   ├── start.py
│   │   └── user_ads.py
│   ├── utils/                     # Утилиты
│   │   ├── admin_check.py
│   │   ├── database_update.py
│   │   ├── menu.py
│   │   ├── rate_limiter.py
│   │   └── yandex_disk.py
│   └── ...
│
├── docker/
│   ├── Dockerfile                 # Docker-образ
│   ├── docker-compose.yml         # Конфигурация Docker Compose
│   └── requirements.txt           # Python зависимости
│
├── run_bot.py                     # Скрипт для запуска бота
├── requirements.txt               # Основной файл зависимостей
└── README.md                      # Документация
```

## ⚙️ **Установка и запуск**

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/Egorchik44/BotavtotG.git
cd BotavtotG
```

### 2. Настройте окружение
Создайте `.env` файл с вашими настройками:
```env
TOKEN=ваш_токен_бота
DATABASE_URL=postgresql://user:password@localhost/dbname
YANDEX_DISK_TOKEN=ваш_токен_яндекс_диска
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Запустите проект
Локально:
```bash
python run_bot.py
```

С Docker:
```bash
docker-compose up --build
```



---
