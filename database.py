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
    # Query the database
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
    # Update the balance
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
        # Update the balance
        set_balance(user_id, balance + amount)
    else:
        # If the user does not exist, create a new entry
        create_user(user_id)
        set_balance(user_id, amount)


def subtract_balance(user_id: str, amount: int):
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

    print(f"last_claimed: {last_claimed} \n"
          f"current_time: {current_time} \n")
    # Check if the user can claim the daily reward
    if current_time - last_claimed >= 86400:
        # Claim the reward
        add_balance(user_id, 1000)
        # Update the last claimed timestamp
        c.execute("INSERT OR REPLACE INTO daily (user, last_claimed) VALUES (?, ?)", (user_id, current_time))
        conn.commit()
        return True
    return False

# conn.close()
