import psycopg2

connect_db = psycopg2.connect(database='user_db', user='postgres', password='password')


def create_db(conn):
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS customers(
        client_id INTEGER UNIQUE PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(40)
        );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS phones(
        id SERIAL PRIMARY KEY,
        client_id INTEGER REFERENCES customers(client_id),
        phone VARCHAR(18)
        );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS phones_client(
        id SERIAL PRIMARY KEY,
        client_id INTEGER REFERENCES customers(client_id),
        phone_id INTEGER REFERENCES phones(phones_id),
        );""")
    conn.commit()


def add_client(conn, client_id, first_name, last_name, email, phones=None):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO customers(client_id, first_name, last_name, email) VALUES (%s, %s, %s, %s);
        """, (client_id, first_name, last_name, email))
    cur.execute("""
        INSERT INTO phones(client_id, phone) VALUES(%s, %s);
        """, (client_id, phones))
    conn.commit()


def add_phone(conn, client_id, phone):
    cur = conn.cursor()
    cur.execute("""
        UPDATE phones SET phone=%s WHERE client_id=%s;
        """, (phone, client_id))
    conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    cur = conn.cursor()
    cur.execute("""
        SELECT * from customers WHERE id = %s
         """, client_id)
    info = cur.fetchone()
    if first_name is None:
        first_name = info[1]
    if last_name is None:
        last_name = info[2]
    if email is None:
        email = info[3]
    cur.execute("""
        UPDATE customers SET first_name = %s, last_name = %s, email =%s where client_id = %s
        """, (first_name, last_name, email, client_id))
    conn.commit()


def delete_phone(conn, client_id, phone, phone_id):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM phones WHERE phone = %s, client_id = %s 
        """, (phone, client_id))
    cur.execute("""
        DELETE FROM phones_client WHERE phone = %s, client_id = %s, phone_id = %s
        """, (phone, client_id, phone_id))
    conn.commit()


def delete_client(conn, client_id):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM phones WHERE client_id = %s
        """, (client_id))
    cur.execute("""
        DELETE FROM customers WHERE id = %s
        """, (client_id))
    cur.execute("""
        DELETE FROM phones_client WHERE id = %s
        """, (client_id))
    conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    cur = conn.cursor()
    if first_name is None:
        first_name = '%'
    else:
        first_name = '%' + first_name + '%'
    if last_name is None:
        last_name = '%'
    else:
        last_name = '%' + last_name + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if phone is None:
        cur.execute("""
            SELECT c.client_id, c.first_name, c.last_name, c.email, p.phone FROM customers c
            LEFT JOIN phones p ON c.id = p.client_id
            WHERE c.first_name LIKE %s AND c.last_name LIKE %s
            AND c.email LIKE %s
            """, (first_name, last_name, email))
    else:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, p.phone FROM customers c
            LEFT JOIN phones p ON c.id = p.client_id
            WHERE c.first_name LIKE %s AND c.last_name LIKE %s
            AND c.email LIKE %s AND p.phone like %s
            """, (first_name, last_name, email, phone))

