[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![FastApi](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)


## Описание проекта
Телеграм-бот адаптации и помощи сотрудникам российского разработчика IT-оборудования QTECH 


### Запуск проекта

Клонировать репозиторий и перейти в него в командной строке:

``` shell
git clone 
```

- Cоздать и активировать виртуальное окружение:

``` shell
python3 -m venv venv
```

* Если у вас Linux/macOS

``` shell
source venv/bin/activate
```

* Если у вас windows

```shell
source venv/scripts/activate
```

- Установить зависимости из файла requirements.txt:

```shell
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### Запустить локальный сервер для администрирования БД бота:

```shell
uvicorn app.main:app --reload
```

* adminpage

После запуска adminpage http://localhost:8000/

*  Документация

После запуска докуметация будет доступно по ссылке http://127.0.0.1:8000/docs

### Команды alembic - справочно 

```shell
alembic init --template async alembic
alembic revision --autogenerate -m "First migration" 
alembic upgrade head
```

### Для аналитики бота поднимаем postgresql в docker - контейне 
    (предполагается, docker уже установлен)
```shell
docker compose up -d
```
### Запуск бота
```shell
cd bot && python main.py
```
Команда для просмотра аналитики задается в ENV-файле параметром ANALYTICS_CALL=<вызывающая аналитику команда>. Бот реагирует только на нажатие кнопок, на ввод любого текста предлагает воспользоваться кнопками, кроме <вызывающая аналитику команда>, тогда открывается меню аналитики.
