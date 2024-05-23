import sqlite3

# Create a connection to the SQLite database
# If the database does not exist, it will be created
conn = sqlite3.connect('bank.db')

# Create a cursor object
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS bank
             (user TEXT PRIMARY KEY, balance INTEGER)''')


def create_user(user_id: str):
    # Insert a row of data
    c.execute("INSERT OR IGNORE INTO bank (user, balance) VALUES (?, ?)", (user_id, 2000))
    conn.commit()


def get_balance(user_id: str):
    # Query the database
    c.execute("SELECT balance FROM bank WHERE user=?", (user_id,))
    row = c.fetchone()
    if row:
        return row[0]
    return None


def set_balance(user_id: str, balance: int):
    # Update the balance
    c.execute("UPDATE bank SET balance=? WHERE user=?", (balance, user_id))
    conn.commit()


def add_balance(user_id: str, amount: int):
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


# conn.close()
