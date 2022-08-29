import random
import sqlite3


def create_tables() -> None:
    connection = sqlite3.connect("ships.db")
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


def record_to_ship(max_records: int, max_weapons_id: int, max_hull_id: int,
                   max_engine_id: int) -> bool:
    connection = sqlite3.connect("ships.db")
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
            return True


def record_to_weapons(max_records: int) -> bool:
    connection = sqlite3.connect("ships.db")
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


def record_to_hulls(max_records: int) -> bool:
    connection = sqlite3.connect("ships.db")
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


def record_to_engines(max_records: int) -> bool:
    connection = sqlite3.connect("ships.db")
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


def fill_the_tables() -> None:
    max_records_to_ship_table = 200
    max_records_to_weapons_table = 20
    max_records_to_hulls_table = 5
    max_records_to_engines_table = 6

    record_to_ship(
        max_records_to_ship_table,
        max_records_to_weapons_table,
        max_records_to_hulls_table,
        max_records_to_engines_table
    )
    record_to_weapons(max_records_to_weapons_table)
    record_to_hulls(max_records_to_hulls_table)
    record_to_engines(max_records_to_engines_table)


def main():
    create_tables()
    fill_the_tables()


if __name__ == "__main__":
    main()
