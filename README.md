# Тестовое для Lesta Studio

Тесты по проверке данных кораблей в таблицах.

## Как использовать
Установить библиотеку `pytest`:
```shell
pip install requirements.txt
```
В репозитории есть два скрипта:

- `create_db.py` - Создает БД, для будущей работы. Заполняет ее рандомными данными, в количестве: 200 кораблей, 20 оружий, 5 корпусов и 6 движков.

В репозитории уже лежит тестовая, можете использовать существующую БД, либо можете ее удалить и создать новую командой:
```shell
python3 create_db.py
```

- `tests.py` - Скрипт с тестами, который при инициализации создает дамп существующей базы и заполняет основную БД рандомными характеристиками. Запуск тестов происходит командой:
```shell
pytest -v tests.py
```
Подробное описание ошибок выводится в консоль в виде подобного репорта:
```shell
...
AssertionError: Ship-157, Engine-5
E                         power: expected 15, was 18
E
E                         type: expected 10, was 16
...
```