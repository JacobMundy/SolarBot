import json
import sqlite3
import time
import os


# Create a connection to the SQLite database
# If the database does not exist, it will be created
dir_path = os.path.dirname(os.path.realpath(__file__))
conn = sqlite3.connect(dir_path + '/bank.db')
settings_path = dir_path + '/settings.json'

# Create a cursor object
cursor = conn.cursor()

# Create table
cursor.execute('''CREATE TABLE IF NOT EXISTS bank
             (user TEXT PRIMARY KEY, balance INTEGER, last_claimed INTEGER DEFAULT 0)''')

# Open/create the settings file and load/create the settings
if os.path.exists(settings_path):
    settings_file = open(settings_path, 'r+')
    settings = json.load(settings_file)
    settings_file.close()
else:
    settings_file = open(settings_path, 'w+')
    settings = {'log_deleted_messages': False,
                'log_deleted_messages_channel': "message-logs",
                'blacklisted_channels': []}
    json.dump(settings, settings_file)
    settings_file.close()


conn.commit()


def create_user(user_id: str) -> None:
    """
    Creates a new user with a balance of 2000 if the user does not exist.
    :param user_id:
    :return:
    """
    # Insert a row of data
    cursor.execute("INSERT OR IGNORE INTO bank (user, balance) VALUES (?, ?)", (user_id, 2000))
    conn.commit()


def get_balance(user_id: str) -> int or None:
    """
    Returns the balance of the user.
    :param user_id:
    :return: int or None
    """
    cursor.execute("SELECT balance FROM bank WHERE user=?", (user_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return None


def set_balance(user_id: str, balance: int) -> None:
    """
    Sets the balance of the user to the specified amount.
    :param user_id:
    :param balance:
    :return:
    """
    cursor.execute("UPDATE bank SET balance=? WHERE user=?", (balance, user_id))
    conn.commit()


def add_balance(user_id: str, amount: int) -> None:
    """
    Adds the specified amount to the user's balance.
    :param user_id:
    :param amount:
    :return:
    """
    # Get the current balance
    balance = get_balance(user_id)
    if balance is not None:
        set_balance(user_id, balance + amount)
    else:
        create_user(user_id)
        set_balance(user_id, amount)


def subtract_balance(user_id: str, amount: int):
    """
    Subtracts the specified amount from the user's balance.
    :param user_id:
    :param amount:
    :return:
    """
    add_balance(user_id, -amount)


def transfer_money(sender_id: str, receiver_id: str, amount: int) -> bool:
    """
    Transfers the specified amount from the sender to the receiver.
    :param sender_id:
    :param receiver_id:
    :param amount:
    :return:
    """
    sender_bal = get_balance(sender_id)
    if sender_bal < amount:
        return False

    subtract_balance(sender_id, amount)
    add_balance(receiver_id, amount)
    return True


def claim_daily(user_id: str) -> bool:
    """
    Adds the daily reward of 1000, returns True if successful, False if already claimed.
    :param user_id:
    :return: bool
    """
    # Get the last claimed timestamp
    cursor.execute("SELECT last_claimed FROM bank WHERE user=?", (user_id,))
    row = cursor.fetchone()
    if row:
        last_claimed = row[0]
    else:
        last_claimed = 0

    # Get the current timestamp
    current_time = int(time.time())

    # Check if the user can claim the daily reward
    if current_time - last_claimed >= 86400:
        # Claim the reward
        add_balance(user_id, 1000)
        # Update the last claimed timestamp
        cursor.execute("UPDATE bank SET last_claimed=? WHERE user=?", (current_time, user_id))
        conn.commit()
        return True
    return False


def get_time_until_next_daily(user_id: str) -> int:
    """
    Returns the time until the user can claim the daily reward.
    :param user_id:
    :return: int
    """
    # Get the last claimed timestamp
    cursor.execute("SELECT last_claimed FROM bank WHERE user=?", (user_id,))
    row = cursor.fetchone()
    if row:
        last_claimed = row[0]
    else:
        last_claimed = 0

    # Get the current timestamp
    current_time = int(time.time())

    # Calculate the time until the next daily reward
    return 24 - (current_time - last_claimed) // 3600

def get_leaderboard():
    """
    Returns the top 100 users with the highest balance.
    :return: list
    """
    cursor.execute("SELECT user, balance FROM bank ORDER BY balance DESC LIMIT 100")
    return cursor.fetchall()


def get_settings(command: str):
    """
    Returns the settings for the specified command.
    :param command:
    :return: dict
    """
    try:
        return settings[command]
    except KeyError:
        return {}


def set_settings(command: str, command_value) -> None:
    """
    Sets the settings for the specified command.
    :param command:
    :param command_value:
    :return:
    """
    if command not in settings:
        return
    with open(settings_path, 'w') as settings_file:
        settings[command] = command_value
        json.dump(settings, settings_file)


def add_blacklisted_channel(channel_id: str) -> None:
    """
    Adds a channel to the blacklist.
    :param channel_id:
    :return:
    """
    with open(settings_path, 'w') as settings_file:
        settings['blacklisted_channels'].append(channel_id)
        json.dump(settings, settings_file)


def remove_blacklisted_channel(channel_id: str) -> None:
    """
    Removes a channel from the blacklist.
    :param channel_id:
    :return:
    """
    with open(settings_path, 'w') as settings_file:
        settings['blacklisted_channels'].remove(channel_id)
        json.dump(settings, settings_file)


def is_blacklisted_channel(channel_id: str) -> bool:
    """
    Returns True if the channel is blacklisted, False otherwise.
    :param channel_id:
    :return: bool
    """
    return channel_id in settings['blacklisted_channels']

# conn.close()