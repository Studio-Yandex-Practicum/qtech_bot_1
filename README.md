[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![FastApi](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)


## Описание проекта
Телеграм-бот адаптации и помощи сотрудникам российского разработчика IT-оборудования QTECH 


Запуск приложения
/c/Dev/QtechBot

### Запуск проекта

Клонировать репозиторий и перейти в него в командной строке:

```
git clone 
```
Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
Запустить локальный сервер:
```
uvicorn app.main:app --reload
```
### Документация
После запуска докуметация будет доступно по ссылке 
http://127.0.0.1:8000/docs


### Команды alembic - справочно
```
alembic init --template async alembic
alembic revision --autogenerate -m "First migration" 
alembic upgrade head
```