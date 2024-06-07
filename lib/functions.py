import configparser
from miki import cur, con

import datetime


def get_future_time(delta_str):
    delta_unit = str(delta_str)[-1].lower()
    delta_value = int(str(delta_str)[:-1])

    if delta_unit == 'd':
        delta = datetime.timedelta(days=delta_value)
    elif delta_unit == 'm':
        delta = datetime.timedelta(minutes=delta_value)
    elif delta_unit == 'h':
        delta = datetime.timedelta(hours=delta_value)
    elif delta_unit == 's':
        delta = datetime.timedelta(seconds=delta_value)
    elif delta_unit == 'w':
        delta = datetime.timedelta(weeks=delta_value)
    else:
        delta = datetime.timedelta()

    future_time = datetime.datetime.now() + delta
    return int(future_time.timestamp())


def get_current_date():
    current_time = datetime.datetime.now()
    return current_time.strftime("%d-%m-%Y")


def create_db():
    cur.execute("CREATE TABLE Users(name UNIQUE, money, timeout, ban_timeout, mute_timeout, warn)")
    cur.execute("CREATE TABLE Shop(id INTEGER UNIQUE PRIMARY KEY, name, description, price)")
    cur.execute("CREATE TABLE History(id INTEGER UNIQUE PRIMARY KEY, name, description)")


def create_profile(id_name):
    data = [(id_name, 0, 0, 0, 0, 0), ]
    cur.executemany("INSERT INTO Users VALUES(?, ?, ?, ?, ?, ?)", data)
    con.commit()
    cur.execute("SELECT * FROM Users WHERE name = ?", (id_name,))
    return cur.fetchone()


def add_history(id_name, description):
    data = [(None, id_name, description), ]
    cur.executemany("INSERT INTO History VALUES(?, ?, ?)", data)
    con.commit()


# config
def create_config():
    id_chat = "0000000000000000000"
    config = configparser.ConfigParser()

    config.add_section('Login')
    config.add_section('Protect')
    config.add_section('Log')
    config.add_section('Event')
    config.add_section('Roles')

    config.set('Login', 'token', '')
    config.set('Login', 'command_chat', id_chat)
    config.set('Login', 'guild_id', id_chat)
    config.set('Protect', 'white_list', "[281772955690860544, ]")
    config.set('Log', 'log_chat', id_chat)
    config.set('Event', 'event_chat', id_chat)
    config.set('Event', 'event_categorize', id_chat)
    config.set('Roles', 'role_ban', id_chat)
    config.set('Roles', 'role_mute', id_chat)

    with open('config.cfg', 'w') as configfile:
        config.write(configfile)


