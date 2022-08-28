import os
import random
import sqlite3

import pytest


#
# @pytest.mark.parametrize("received_values, expected_values", get_ships_tables())
# def test_ships_table(received_values, expected_values):
#     for index, characteristic in enumerate(received_values):
#         if characteristic != expected_values[index]:
#             ships_error_message = f"""{received_values[0]}, {characteristic}
#             expected {expected_values[index]}, was {characteristic}
#             """
#
#     assert received_values == expected_values, ships_error_message
#
# #
# @pytest.mark.parametrize("received_values, expected_values", get_ships_weapons_changes())
# def test_ships_weapons(received_values, expected_values):
#     new_values = {
#         "ship": received_values[0],
#         "weapon": received_values[1],
#         "reload speed": received_values[2],
#         "rotational speed": received_values[3],
#         "diameter": received_values[4],
#         "power volley": received_values[5],
#         "count": received_values[6],
#     }
#
#     old_values = {
#         "ship": expected_values[0],
#         "weapon": expected_values[1],
#         "reload speed": expected_values[2],
#         "rotational speed": expected_values[3],
#         "diameter": expected_values[4],
#         "power volley": expected_values[5],
#         "count": expected_values[6],
#     }
#     for _ in received_values:
#         error_message = f"{new_values['ship']}, {new_values['weapon']}"
#         for key, value in new_values.items():
#             if new_values[key] != old_values[key]:
#                 error_message += f"""
#                 {key}: expected {old_values[key]}, was {value}
#                 """
#
#     assert received_values == expected_values, error_message


def get_changes_in_ship_characteristic():
    """
    При инициализации теста делает рандомные изменения в таблицах, после чего
    отправляет тесты для проверки на изменение ключевых характеристик у
    корабля в тест-функцию.
    :return: Возвращает значение в виде списка
    list[(new_values, expected_values)]
    """

    # random_change_in_tables()
    connection = sqlite3.connect("ships.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Ships")
    changed_db = cursor.fetchall()
    connection = sqlite3.connect("ships_dump.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Ships")
    dump_db = cursor.fetchall()

    return list(zip(changed_db, dump_db))


def get_table_changes(sql_query):
    """
    Возвращает список значений из таблицы, которые изменились после рандомных
    изменений.
    :param sql_query: Запрос, по которому получаем значения из таблицы
    :return: Список измененных значений
    """
    main_db_connection = sqlite3.connect("ships.db")
    main_db_cursor = main_db_connection.cursor()
    main_db_cursor.execute(sql_query)
    main_db_ship_weapons = main_db_cursor.fetchall()

    dump_db_connection = sqlite3.connect("ships_dump.db")
    dump_db_cursor = dump_db_connection.cursor()
    dump_db_cursor.execute(sql_query)
    dump_db_ship_weapons = dump_db_cursor.fetchall()

    return [
        (row[0], ) for row_index, row in enumerate(main_db_ship_weapons)
        if row != dump_db_ship_weapons[row_index]
    ]


def get_changed_ships(inner_table_name, primary_key, changed_by):
    """
    Выдает список изменненных кораблей по связанной таблице
    :parameter inner_table_name:
    Название связанной таблицы
    :parameter primary_key:
    Ключ для связанной таблицы, по которому будет определятся результат
    (По оружию, по корпусу и т.д)
    :parameter changed_by:
    Список колонок из таблицы, которые были изменены
    Например: ["Weapon-1", "Weapon-14"] означает, что были изменены два оружия
    у корабля - "Weapon-1" и "Weapon-14"
    :return: Возвращает список измененных кораблей
    """

    changed_ships_sql_query = f"""
        SELECT ship FROM Ships 
        INNER JOIN {inner_table_name} on 
        {inner_table_name}.{primary_key} = Ships.{primary_key}
        WHERE Ships.{primary_key}=(?)
        """

    main_db_connection = sqlite3.connect("ships.db")
    main_db_cursor = main_db_connection.cursor()

    changed_ships = []
    for changed_weapon in changed_by:
        main_db_cursor.execute(changed_ships_sql_query, changed_weapon)
        [changed_ships.append(ship) for ship in main_db_cursor.fetchall()]

    return changed_ships


def get_table_values(database_name, changed_ships, column, *args):
    """
    Возвращает строки из указанной БД
    :param database_name: Имя БД файла
    :param changed_ships: Список изменненных кораблей
    :param column: Колонка из связанной таблицы, по которой происходит поиск
    :param args: Список колонок, которые хотим увидеть в SQL-запросе
    :return: Строки из таблицы в виде списка, для будущей передачи в тесты
    """

    columns = ", ".join([column_name for column_name in args[0]])
    ships_with_weapons_characteristics = f"""
    SELECT ship, inner_table.{column}, {columns} FROM Ships
    INNER JOIN weapons inner_table on 
    inner_table.{column} = Ships.{column}
    WHERE ship = (?)
    """

    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    values_in_table = []
    for changed_parameter in changed_ships:
        cursor.execute(ships_with_weapons_characteristics, changed_parameter)
        [values_in_table.append(ship) for ship in cursor.fetchall()]

    return values_in_table


def create_tests(new_values, expected_values):
    """
    Создает тесты-кейсы из новых значений в таблице и старых
    :param new_values: Список строк из новой таблицы, где изменены значения
    :param expected_values: Список строк из старой таблицы
    :return: Возваращает список с тестами, в который не включены тесты, если
    у корабля изменилась главная характеристика (оружие, оружие, корпус, движок),
    т.к эти тесты создаются в функции get_changes_in_ship_characteristic.
    """
    tests = []
    for index, row in enumerate(new_values):
        new_characteristic = row[1]
        old_characteristic = expected_values[index][1]
        if new_characteristic != old_characteristic:
            tests.append(
                pytest.param(
                    row, expected_values[index], marks=pytest.mark.skip(
                        reason="checked in other test"
                    )
                )
            )
            continue
        tests.append((row, expected_values[index]))
    return tests


def get_ships_weapons_changes():
    all_ships_weapons_sql_query = """
    SELECT weapon, reload_speed, rotational_speed, diameter, power_volley, count
    FROM weapons
    """
    changed_weapons = get_table_changes(all_ships_weapons_sql_query)
    changed_ships = get_changed_ships(
        inner_table_name="weapons",
        primary_key="weapon",
        changed_by=changed_weapons
    )
    table_columns = ("reload_speed", "rotational_speed", "diameter",
                     "power_volley", "count")
    new_values_in_table = get_table_values(
        "ships.db",
        changed_ships,
        "weapon",
        table_columns
    )
    expected_values = get_table_values(
        "ships_dump.db",
        changed_ships,
        "weapon",
        table_columns
    )

    values_for_tests = create_tests(new_values_in_table, expected_values)
    return values_for_tests


def get_ships_hulls_changes():
    all_ships_hulls_sql_query = """
    SELECT hull, armor, type, capacity FROM hulls
    """

    changed_hulls = get_table_changes(all_ships_hulls_sql_query)
    changed_ships = get_changed_ships(
        inner_table_name="hulls",
        primary_key="hull",
        changed_by=changed_hulls
    )
    table_columns = ("hull", "armor", "type", "capacity")
    new_values_in_table = get_table_values(
        "ships.db",
        changed_ships,
        "hull",
        table_columns
    )
    expected_values = get_table_values(
        "ships_dump.db",
        changed_ships,
        "hull",
        table_columns
    )

    values_for_tests = create_tests(new_values_in_table, expected_values)
    return values_for_tests


def get_ships_engines_changes():
    all_ships_engines_sql_query = """
    SELECT engine, power, type FROM engines
    """

    changed_engines = get_table_changes(all_ships_engines_sql_query)
    changed_ships = get_changed_ships(
        inner_table_name="engines",
        primary_key="engine",
        changed_by=changed_engines
    )
    table_columns = ("engine", "power", "type")
    new_values_in_table = get_table_values(
        "ships.db",
        changed_ships,
        "engine",
        table_columns
    )
    expected_values = get_table_values(
        "ships_dump.db",
        changed_ships,
        "engine",
        table_columns
    )

    values_for_tests = create_tests(new_values_in_table, expected_values)
    return values_for_tests


def create_db_dump():
    connection = sqlite3.connect("ships.db")
    with open("dump.sql", "w") as dump_file:
        for line in connection.iterdump():
            dump_file.write(f"{line}\n")

    connection = sqlite3.connect("ships_dump.db")
    cursor = connection.cursor()
    with open("dump.sql", "r") as dump_file:
        cursor.executescript(dump_file.read())
    os.remove("dump.sql")


def change_random_ship_characteristic():
    connection = sqlite3.connect("ships.db")
    cursor = connection.cursor()
    cursor.execute(
        '''
        SELECT ship FROM Ships
        '''
    )
    ships_count = len(cursor.fetchall())
    characteristics = ["weapon", "hull", "engine"]

    random_ship = f"Ship-{random.randint(1, ships_count)}"
    random_characteristic = random.choice(characteristics)
    new_characteristic = f"{random_characteristic.capitalize()}-{random.randint(1, 15)}"

    params = (new_characteristic, random_ship)
    query = f"""
    UPDATE Ships SET {random_characteristic}=(?) WHERE ship = (?)
    """
    cursor.execute(query, params)
    connection.commit()


def change_random_ship_part(table_name: str):
    connection = sqlite3.connect("ships.db")
    cursor = connection.cursor()

    cursor.execute(
        f'''
        PRAGMA table_info({table_name})
        '''
    )
    columns = [column[1] for column in cursor.fetchall()]
    cursor.execute(
        f'''
        SELECT * FROM {table_name}
        '''
    )
    max_records = len(cursor.fetchall())
    random_part_of_ship = f"{columns[0].capitalize()}-{random.randint(1, max_records)}"
    random_characteristic = random.choice(columns[1:])
    new_characteristic = random.randint(1, 20)

    cursor.execute(
        f'''
        UPDATE {table_name} SET {random_characteristic}=(?)
        WHERE {columns[0]} = (?)
        ''', (new_characteristic, random_part_of_ship)
    )
    connection.commit()


def random_change_in_tables():
    connection = sqlite3.connect("ships.db")
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables_names = [table[0] for table in cursor.fetchall()
                    if table[0] != "Ships"]
    tables_changes = {}

    for table in tables_names:
        tables_changes[table] = random.randint(1, 30)

    for table, changes in tables_changes.items():
        [change_random_ship_part(table) for _ in range(changes)]

    for _ in range(50):
        change_random_ship_characteristic()


if __name__ == "__main__":
    get_ships_weapons_changes()