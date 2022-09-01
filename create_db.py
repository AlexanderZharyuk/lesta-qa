import random
import sqlite3

from environs import Env


def create_tables(db_name: str) -> None:
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Ships
        ([ship] TEXT PRIMARY KEY, [weapon] TEXT, [hull] TEXT, [engine] TEXT)
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS weapons
        ([weapon] TEXT PRIMARY KEY, [reload_speed] INTEGER, 
        [rotational_speed] INTEGER, [diameter] INTEGER, 
        [power_volley] INTEGER, [count] INTEGER)
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS hulls
        ([hull] TEXT PRIMARY KEY, [armor] INTEGER, 
        [type] INTEGER, [capacity] INTEGER)
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS engines
        ([engine] TEXT PRIMARY KEY, [power] INTEGER, [type] INTEGER)
        '''
    )

    connection.commit()


def create_ships(db_name: str, max_records: int, max_weapons_id: int,
                 max_hull_id: int, max_engine_id: int) -> bool | None:
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    number_of_records = 0

    while True:
        params = (
            f"Ship-{random.randint(1, max_records)}",
            f"Weapon-{random.randint(1, max_weapons_id)}",
            f"Hull-{random.randint(1, max_hull_id)}",
            f"Engine-{random.randint(1, max_engine_id)}"
        )
        try:
            cursor.execute(
                '''
                INSERT INTO Ships (ship, weapon, hull, engine) 
                VALUES (?, ?, ?, ?)
                ''', params
            )
        except sqlite3.IntegrityError:
            continue
        else:
            connection.commit()

        number_of_records += 1
        if number_of_records == max_records:
            return


def create_weapons(db_name: str, max_records: int) -> bool:
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    number_of_records = 0

    while True:
        params = (
            f"Weapon-{random.randint(1, max_records)}",
            random.randint(1, 20),
            random.randint(1, 15),
            random.randint(1, 12),
            random.randint(1, 15),
            random.randint(1, 3)
        )
        try:
            cursor.execute(
                '''
                INSERT INTO weapons (
                weapon, reload_speed, rotational_speed, diameter,
                power_volley, count
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ''', params
            )
        except sqlite3.IntegrityError:
            continue
        else:
            connection.commit()

        number_of_records += 1
        if number_of_records == max_records:
            return True


def create_hulls(db_name: str, max_records: int) -> bool:
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    number_of_records = 0

    while True:
        params = (
            f"Hull-{random.randint(1, max_records)}",
            random.randint(1, 20),
            random.randint(1, 15),
            random.randint(1, 12),
        )
        try:
            cursor.execute(
                '''
                INSERT INTO hulls (
                hull, armor, type, capacity
                )
                VALUES (?, ?, ?, ?)
                ''', params
            )
        except sqlite3.IntegrityError:
            continue
        else:
            connection.commit()

        number_of_records += 1
        if number_of_records == max_records:
            return True


def create_engines(db_name: str, max_records: int) -> bool:
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    number_of_records = 0

    while True:
        params = (
            f"Engine-{random.randint(1, max_records)}",
            random.randint(1, 20),
            random.randint(1, 15),
        )
        try:
            cursor.execute(
                '''
                INSERT INTO engines (
                engine, power, type
                )
                VALUES (?, ?, ?)
                ''', params
            )
        except sqlite3.IntegrityError:
            continue
        else:
            connection.commit()

        number_of_records += 1
        if number_of_records == max_records:
            return True


def fill_tables(db_name: str) -> None:
    max_records_to_ship_table = 200
    max_records_to_weapons_table = 20
    max_records_to_hulls_table = 5
    max_records_to_engines_table = 6

    create_ships(
        db_name=db_name,
        max_records=max_records_to_ship_table,
        max_weapons_id=max_records_to_weapons_table,
        max_hull_id=max_records_to_hulls_table,
        max_engine_id=max_records_to_engines_table
    )
    create_weapons(db_name, max_records_to_weapons_table)
    create_hulls(db_name, max_records_to_hulls_table)
    create_engines(db_name, max_records_to_engines_table)


def main():
    env = Env()
    env.read_env()

    db_name = env.str("MAIN_DB_NAME", "ships.sqlite3")
    create_tables(db_name=db_name)
    fill_tables(db_name=db_name)


if __name__ == "__main__":
    main()
