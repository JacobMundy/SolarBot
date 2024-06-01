import sqlite3
import time

# Create a connection to the SQLite database
# If the database does not exist, it will be created
conn = sqlite3.connect('bank.db')

# Create a cursor object
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS bank
             (user TEXT PRIMARY KEY, balance INTEGER)''')


c.execute('''CREATE TABLE IF NOT EXISTS daily
             (user TEXT PRIMARY KEY, last_claimed INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS settings
             (command TEXT PRIMARY KEY, command_settings BLOB)''')

c.execute("INSERT OR IGNORE INTO settings (command, command_settings) "
          "VALUES ('log_deleted_messages', 0)")
c.execute("INSERT OR IGNORE INTO settings (command, command_settings) "
          "VALUES ('log_deleted_messages_channel', 'message-logs')")

conn.commit()


def create_user(user_id: str) -> None:
    """
    Creates a new user with a balance of 2000 if the user does not exist.
    :param user_id:
    :return:
    """
    # Insert a row of data
    c.execute("INSERT OR IGNORE INTO bank (user, balance) VALUES (?, ?)", (user_id, 2000))
    conn.commit()


def get_balance(user_id: str) -> int or None:
    """
    Returns the balance of the user.
    :param user_id:
    :return: int or None
    """
    c.execute("SELECT balance FROM bank WHERE user=?", (user_id,))
    row = c.fetchone()
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
    c.execute("UPDATE bank SET balance=? WHERE user=?", (balance, user_id))
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


def claim_daily(user_id: str) -> bool:
    """
    Adds the daily reward of 1000, returns True if successful, False if already claimed.
    :param user_id:
    :return: bool
    """
    # Get the last claimed timestamp
    c.execute("SELECT last_claimed FROM daily WHERE user=?", (user_id,))
    row = c.fetchone()
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
        c.execute("INSERT OR REPLACE INTO daily (user, last_claimed) VALUES (?, ?)", (user_id, current_time))
        conn.commit()
        return True
    return False


def get_settings(command: str) -> dict:
    """
    Returns the settings for the specified command.
    :param command:
    :return: dict
    """
    c.execute("SELECT command_settings FROM settings WHERE command=?", (command,))
    row = c.fetchone()
    if row:
        return row[0]
    return {}


def set_settings(command: str, settings) -> None:
    """
    Sets the settings for the specified command.
    :param command:
    :param settings:
    :return:
    """
    c.execute("UPDATE settings SET command_settings=? WHERE command=?", (settings, command))
    conn.commit()


# conn.close()
