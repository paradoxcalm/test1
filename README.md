# Telegram-бот для Эльдара

## Команды бота:

- `/start` — приветственное сообщение
- `/help` — справка

## Запуск

Скопируйте `.env.example` в `.env` и отредактируйте `.env` файл, заполнив в нём все переменные окружения:

```bash
cp wbnotifierbot/.env.example wbnotifierbot/.env
```

Для управления зависимостями используется [poetry](https://python-poetry.org/),
требуется Python 3.11.

Установка зависимостей и запуск бота:

```bash
poetry install
poetry run python -m wbnotifierbot
```

## Ideas

- Место для идей ;-)

## Деплой

[Описание того, как можно развернуть бота на сервере](DEPLOY.md)
