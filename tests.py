import os
import random
import sqlite3

import pytest

from environs import Env


def create_db_dump(main_db_name: str, dump_db_name: str):
    connection = sqlite3.connect(main_db_name)
    with open("dump.sql", "w") as dump_file:
        for line in connection.iterdump():
            dump_file.write(f"{line}\n")

    connection = sqlite3.connect(dump_db_name)
    cursor = connection.cursor()
    with open("dump.sql", "r") as dump_file:
        cursor.executescript(dump_file.read())
    os.remove("dump.sql")


def change_random_ship_characteristic(db_name: str):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT weapon FROM weapons
        """
    )
    max_weapons_id = len(cursor.fetchall())

    cursor.execute(
        """
        SELECT hull FROM hulls
        """
    )
    max_hulls_id = len(cursor.fetchall())

    cursor.execute(
        """
        SELECT engine FROM engines
        """
    )
    max_engines_id = len(cursor.fetchall())

    cursor.execute(
        """
        SELECT ship FROM Ships
        """
    )
    ships_count = len(cursor.fetchall())
    characteristics = {
        "weapon": max_weapons_id,
        "hull": max_hulls_id,
        "engine": max_engines_id
    }
    random_ship = f"Ship-{random.randint(1, ships_count)}"
    random_characteristic = random.choice(list(characteristics.keys()))

    new_characteristic = f"{random_characteristic.capitalize()}-" \
                         f"{random.randint(1, characteristics[random_characteristic])}"

    params = (new_characteristic, random_ship)
    query = f"""
    UPDATE Ships SET {random_characteristic}=(?) WHERE ship = (?)
    """
    cursor.execute(query, params)
    connection.commit()


def change_random_ship_part(db_name: str, table_name: str):
    connection = sqlite3.connect(db_name)
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
    random_part_of_ship = f"{columns[0].capitalize()}-" \
                          f"{random.randint(1, max_records)}"
    random_characteristic = random.choice(columns[1:])
    new_characteristic = random.randint(1, 20)

    cursor.execute(
        f'''
        UPDATE {table_name} SET {random_characteristic}=(?)
        WHERE {columns[0]} = (?)
        ''', (new_characteristic, random_part_of_ship)
    )
    connection.commit()


def random_change_in_tables(db_name: str):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

    tables_names = [table[0] for table in cursor.fetchall()
                    if table[0] != "Ships"]
    tables_changes = {}

    for table in tables_names:
        tables_changes[table] = random.randint(1, 30)

    for table, changes in tables_changes.items():
        [change_random_ship_part(db_name, table) for _ in range(changes)]

    for _ in range(50):
        change_random_ship_characteristic(db_name=db_name)


def get_table_changes(sql_query: str):
    """
    Возвращает список из строк основной таблицы и дампа для будущей проверки.
    :param sql_query: Запрос, по которому получаем значения из таблицы
    :return: Список строк из таблиц list[((main_table_row_1), (dump_table_row_2))]
    """
    env = Env()
    env.read_env()

    main_db_name = env.str("MAIN_DB_NAME", "ships.sqlite3")
    dump_db_name = env.str("DUMP_DB_NAME", "ships_dump.sqlite3")

    main_db_connection = sqlite3.connect(main_db_name)
    main_db_cursor = main_db_connection.cursor()
    main_db_cursor.execute(sql_query)
    main_db_ships = main_db_cursor.fetchall()

    dump_db_connection = sqlite3.connect(dump_db_name)
    dump_db_cursor = dump_db_connection.cursor()
    dump_db_cursor.execute(sql_query)
    dump_db_ships = dump_db_cursor.fetchall()

    return list(zip(main_db_ships, dump_db_ships))


def create_tests(values):
    """
    Создает тест-кейсы из новых и старых значений в таблице
    :param values: Список значений для сравнений
    :return: Возваращает список с тестами, в который не включены тесты, если
    у корабля изменилась главная характеристика (оружие, корпус, движок),
    т.к эти тесты создаются в функции get_changes_in_ship_characteristic.
    """

    tests = []
    for rows in values:
        new_characteristic = rows[0][1]
        old_characteristic = rows[1][1]

        if new_characteristic != old_characteristic:
            tests.append(
                pytest.param(
                    rows[0], rows[1], marks=pytest.mark.skip(
                        reason="checked in other test"
                    )
                )
            )
            continue
        tests.append((rows[0], rows[1]))
    return tests


def get_changes_in_ship_characteristic():
    """
    При инициализации теста делает рандомные изменения в таблицах, после чего
    отправляет тесты для проверки на изменение ключевых характеристик у
    корабля в тест-функцию.
    :return: Возвращает значение в виде списка
    list[(new_values, expected_values)]
    """

    env = Env()
    env.read_env()

    main_db_name = env.str("MAIN_DB_NAME", "ships.sqlite3")
    dump_db_name = env.str("DUMP_DB_NAME", "ships_dump.sqlite3")

    if not os.path.exists(dump_db_name):
        create_db_dump(main_db_name=main_db_name, dump_db_name=dump_db_name)
        random_change_in_tables(db_name=main_db_name)

    connection = sqlite3.connect(main_db_name)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Ships")

    changed_db = cursor.fetchall()
    connection = sqlite3.connect(dump_db_name)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Ships")
    dump_db = cursor.fetchall()

    return list(zip(changed_db, dump_db))


def get_ships_weapons_changes():
    all_ships_sql_query = """
            SELECT ship, w.weapon, reload_speed, rotational_speed, diameter, 
            power_volley, count FROM Ships 
            INNER JOIN weapons w on Ships.weapon = w.weapon 
            """

    values_in_table = get_table_changes(all_ships_sql_query)
    values_for_tests = create_tests(values_in_table)
    return values_for_tests


def get_ships_hulls_changes():
    all_ships_sql_query = """
    SELECT ship, h.hull, armor, type, capacity FROM Ships
    INNER JOIN hulls h on Ships.hull = h.hull
    """

    values_in_table = get_table_changes(all_ships_sql_query)
    values_for_tests = create_tests(values_in_table)
    return values_for_tests


def get_ships_engines_changes():
    all_ships_sql_query = """
    SELECT ship, e.engine, power, type FROM Ships
    INNER JOIN engines e on Ships.engine = e.engine
    """

    values_in_table = get_table_changes(all_ships_sql_query)
    values_for_tests = create_tests(values_in_table)
    return values_for_tests


@pytest.mark.parametrize(
    "received_values, expected_values", get_changes_in_ship_characteristic()
)
def test_ships_table(received_values, expected_values):
    for index, characteristic in enumerate(received_values):
        if characteristic != expected_values[index]:
            ships_error_message = f"""{received_values[0]}, {characteristic}
            expected {expected_values[index]}, was {characteristic}
            """

    assert received_values == expected_values, ships_error_message


@pytest.mark.parametrize(
    "received_values, expected_values", get_ships_weapons_changes()
)
def test_ships_weapons(received_values, expected_values):
    new_values = {
        "ship": received_values[0],
        "weapon": received_values[1],
        "reload speed": received_values[2],
        "rotational speed": received_values[3],
        "diameter": received_values[4],
        "power volley": received_values[5],
        "count": received_values[6],
    }

    old_values = {
        "ship": expected_values[0],
        "weapon": expected_values[1],
        "reload speed": expected_values[2],
        "rotational speed": expected_values[3],
        "diameter": expected_values[4],
        "power volley": expected_values[5],
        "count": expected_values[6],
    }
    for _ in received_values:
        error_message = f"{new_values['ship']}, {new_values['weapon']}"
        for ship_characteristic_name, ship_characteristic_value in new_values.items():
            if new_values[ship_characteristic_name] != old_values[ship_characteristic_name]:
                error_message += f"""
                {ship_characteristic_name}: expected {old_values[ship_characteristic_name]}, was {ship_characteristic_value}
                """

    assert received_values == expected_values, error_message


@pytest.mark.parametrize(
    "received_values, expected_values", get_ships_hulls_changes()
)
def test_ships_hulls(received_values, expected_values):
    new_values = {
        "ship": received_values[0],
        "hull": received_values[1],
        "armor": received_values[2],
        "type": received_values[3],
        "capacity": received_values[4],
    }

    old_values = {
        "ship": expected_values[0],
        "hull": expected_values[1],
        "armor": expected_values[2],
        "type": expected_values[3],
        "capacity": expected_values[4],
    }
    for _ in received_values:
        error_message = f"{new_values['ship']}, {new_values['hull']}"
        for ship_characteristic_name, ship_characteristic_value in new_values.items():
            if new_values[ship_characteristic_name] != old_values[ship_characteristic_name]:
                error_message += f"""
                {ship_characteristic_name}: expected {old_values[ship_characteristic_name]}, was {ship_characteristic_value}
                """

    assert received_values == expected_values, error_message


@pytest.mark.parametrize(
    "received_values, expected_values", get_ships_engines_changes()
)
def test_ships_engines(received_values, expected_values):
    new_values = {
        "ship": received_values[0],
        "engine": received_values[1],
        "power": received_values[2],
        "type": received_values[3],
    }

    old_values = {
        "ship": expected_values[0],
        "engine": expected_values[1],
        "power": expected_values[2],
        "type": expected_values[3],
    }
    for _ in received_values:
        error_message = f"{new_values['ship']}, {new_values['engine']}"
        for ship_characteristic_name, ship_characteristic_value in new_values.items():
            if new_values[ship_characteristic_name] != old_values[ship_characteristic_name]:
                error_message += f"""
                {ship_characteristic_name}: expected {old_values[ship_characteristic_name]}, was {ship_characteristic_value}
                """

    assert received_values == expected_values, error_message
