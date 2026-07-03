import sqlite3

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    mysql = None
    MySQLError = Exception

class Database:
    def __init__(self, db_type=None, host="localhost", user="root", password="Psalm#23@1"):
        self.host = host
        self.user = user
        self.password = password
        self.database = "sportsclub"
        self.db_file = "sportsclub.db"
        self.conn = None
        self.cursor = None
        self.db_type = db_type or "mysql"

        if self.db_type == "mysql":
            if not self._connect_mysql():
                self.db_type = "sqlite"
                self._connect_sqlite()
        else:
            self._connect_sqlite()

        if self.conn:
            self.initialize_database()

    def _connect_mysql(self):
        if mysql is None:
            print("MySQL connector is not installed; falling back to SQLite.")
            return False

        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
            )
            self.cursor = self.conn.cursor()
            print("Connected to MySQL database.")
            return True
        except MySQLError as e:
            print(f"Error connecting to MySQL: {e}. Falling back to SQLite.")
            self.conn = None
            self.cursor = None
            return False

    def _connect_sqlite(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            print(f"Connected to SQLite database: {self.db_file}")
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to SQLite: {e}")
            self.conn = None
            self.cursor = None
            return False

    def initialize_database(self):
        if not self.conn:
            return

        try:
            if self.db_type == "mysql":
                self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                self.conn.database = self.database

            self._create_tables()
        except (MySQLError, sqlite3.Error) as e:
            print(f"Error initializing database: {e}")

    def _create_tables(self):
        if self.db_type == "mysql":
            tables = {
                "members": (
                    "CREATE TABLE IF NOT EXISTS members ("
                    "  member_id INT AUTO_INCREMENT PRIMARY KEY,"
                    "  name VARCHAR(50) NOT NULL,"
                    "  age INT,"
                    "  gender VARCHAR(10),"
                    "  sport VARCHAR(30),"
                    "  phone VARCHAR(10)"
                    ") ENGINE=InnoDB"
                ),
                "coaches": (
                    "CREATE TABLE IF NOT EXISTS coaches ("
                    "  coach_id INT AUTO_INCREMENT PRIMARY KEY,"
                    "  coach_name VARCHAR(50) NOT NULL,"
                    "  sport VARCHAR(30),"
                    "  experience INT"
                    ") ENGINE=InnoDB"
                ),
                "sports_events": (
                    "CREATE TABLE IF NOT EXISTS sports_events ("
                    "  event_id INT AUTO_INCREMENT PRIMARY KEY,"
                    "  event_name VARCHAR(100) NOT NULL,"
                    "  sport VARCHAR(30),"
                    "  event_date DATE,"
                    "  venue VARCHAR(100)"
                    ") ENGINE=InnoDB"
                ),
                "fees": (
                    "CREATE TABLE IF NOT EXISTS fees ("
                    "  payment_id INT AUTO_INCREMENT PRIMARY KEY,"
                    "  member_id INT,"
                    "  amount FLOAT,"
                    "  payment_date DATE,"
                    "  FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE ON UPDATE CASCADE"
                    ") ENGINE=InnoDB"
                ),
            }
        else:
            tables = {
                "members": (
                    "CREATE TABLE IF NOT EXISTS members ("
                    "  member_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "  name TEXT NOT NULL,"
                    "  age INTEGER,"
                    "  gender TEXT,"
                    "  sport TEXT,"
                    "  phone TEXT"
                    ")"
                ),
                "coaches": (
                    "CREATE TABLE IF NOT EXISTS coaches ("
                    "  coach_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "  coach_name TEXT NOT NULL,"
                    "  sport TEXT,"
                    "  experience INTEGER"
                    ")"
                ),
                "sports_events": (
                    "CREATE TABLE IF NOT EXISTS sports_events ("
                    "  event_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "  event_name TEXT NOT NULL,"
                    "  sport TEXT,"
                    "  event_date TEXT,"
                    "  venue TEXT"
                    ")"
                ),
                "fees": (
                    "CREATE TABLE IF NOT EXISTS fees ("
                    "  payment_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "  member_id INTEGER,"
                    "  amount REAL,"
                    "  payment_date TEXT,"
                    "  FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE ON UPDATE CASCADE"
                    ")"
                ),
            }

        for table_name, table_description in tables.items():
            try:
                self.cursor.execute(table_description)
            except (MySQLError, sqlite3.Error) as e:
                print(f"Error creating table {table_name}: {e}")

    def _prepare_query(self, query):
        if self.db_type == "sqlite":
            return query.replace("%s", "?")
        return query

    def execute_query(self, query, data=None):
        try:
            prepared_query = self._prepare_query(query)
            if data is not None:
                self.cursor.execute(prepared_query, data)
            else:
                self.cursor.execute(prepared_query)
            self.conn.commit()
            return True
        except (MySQLError, sqlite3.Error) as e:
            print(f"Error executing query: {e}")
            return False

    def fetch_all(self, query, data=None):
        try:
            prepared_query = self._prepare_query(query)
            if data is not None:
                self.cursor.execute(prepared_query, data)
            else:
                self.cursor.execute(prepared_query)
            return self.cursor.fetchall()
        except (MySQLError, sqlite3.Error) as e:
            print(f"Error fetching data: {e}")
            return []

    def reset_auto_increment(self, table_name, id_column):
        if self.db_type == "mysql":
            try:
                self.cursor.execute("SET @count = 0")
                self.cursor.execute(f"UPDATE {table_name} SET {id_column} = @count:= @count + 1")
                self.cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1")
                self.conn.commit()
                return True
            except MySQLError as e:
                print(f"Error resetting auto increment: {e}")
                return False
        else:
            # SQLite handles rowids automatically; no reset required.
            return True

    # --- Member Methods ---
    def add_member(self, name, age, gender, sport, phone):
        query = "INSERT INTO members (name, age, gender, sport, phone) VALUES (%s, %s, %s, %s, %s)"
        data = (name, age, gender, sport, phone)
        return self.execute_query(query, data)

    def get_all_members(self):
        query = "SELECT * FROM members"
        return self.fetch_all(query)

    def delete_member(self, member_id):
        query = "DELETE FROM members WHERE member_id = %s"
        success = self.execute_query(query, (member_id,))
        if success:
            self.reset_auto_increment("members", "member_id")
        return success
        
    def update_member(self, member_id, name, age, gender, sport, phone):
        query = "UPDATE members SET name=%s, age=%s, gender=%s, sport=%s, phone=%s WHERE member_id=%s"
        data = (name, age, gender, sport, phone, member_id)
        return self.execute_query(query, data)

    # --- Coach Methods ---
    def add_coach(self, name, sport, experience):
        query = "INSERT INTO coaches (coach_name, sport, experience) VALUES (%s, %s, %s)"
        data = (name, sport, experience)
        return self.execute_query(query, data)

    def get_all_coaches(self):
        query = "SELECT * FROM coaches"
        return self.fetch_all(query)

    def delete_coach(self, coach_id):
        query = "DELETE FROM coaches WHERE coach_id = %s"
        success = self.execute_query(query, (coach_id,))
        if success:
            self.reset_auto_increment("coaches", "coach_id")
        return success

    # --- Event Methods ---
    def add_event(self, name, sport, date, venue):
        query = "INSERT INTO sports_events (event_name, sport, event_date, venue) VALUES (%s, %s, %s, %s)"
        data = (name, sport, date, venue)
        return self.execute_query(query, data)

    def get_all_events(self):
        query = "SELECT * FROM sports_events"
        return self.fetch_all(query)
        
    def delete_event(self, event_id):
        query = "DELETE FROM sports_events WHERE event_id = %s"
        success = self.execute_query(query, (event_id,))
        if success:
            self.reset_auto_increment("sports_events", "event_id")
        return success

    def update_event(self, event_id, name, sport, date, venue):
        query = "UPDATE sports_events SET event_name=%s, sport=%s, event_date=%s, venue=%s WHERE event_id=%s"
        data = (name, sport, date, venue, event_id)
        return self.execute_query(query, data)

    # --- Fee Methods ---
    def add_fee(self, member_id, amount, date):
        query = "INSERT INTO fees (member_id, amount, payment_date) VALUES (%s, %s, %s)"
        data = (member_id, amount, date)
        return self.execute_query(query, data)

    def get_all_fees(self):
        query = "SELECT f.payment_id, m.name, f.amount, f.payment_date FROM fees f JOIN members m ON f.member_id = m.member_id"
        return self.fetch_all(query)

    # --- Update Coach ---
    def update_coach(self, coach_id, name, sport, experience):
        query = "UPDATE coaches SET coach_name=%s, sport=%s, experience=%s WHERE coach_id=%s"
        data = (name, sport, experience, coach_id)
        return self.execute_query(query, data)

    # --- Delete Fee ---
    def delete_fee(self, payment_id):
        query = "DELETE FROM fees WHERE payment_id = %s"
        return self.execute_query(query, (payment_id,))
