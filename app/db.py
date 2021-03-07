import psycopg2
import base64
import pandas as pd

class DB():
    def __init__(self, user, password, host, port, db):
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port
        self.__db = db

    def get_user(self):
        return self.__user

    def __get_password(self):
        return self.__password

    def get_host(self):
        return self.__host

    def get_port(self):
        return self.__port

    def get_db(self):
        return self.__db

    def connection(self, autocommit=False):
        conn = psycopg2.connect(
            user=self.get_user(),
            password=self.__get_password(),
            host=self.get_host(),
            port=self.get_port(),
            database=self.get_db()
        )
        conn.autocommit = autocommit
        return conn

    def exec_query(self, query):
        try:
            conn = self.connection(autocommit=True)
            cur = conn.cursor()
            cur.execute(query)
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(e)
            return False

    def create_database(self, database_name):
        query = f"""
        CREATE DATABASE {database_name}"""
        print(query)
        return self.exec_query(query)


class MagaluDB(DB):
    def __init__(self, user, password, host='localhost', port=5433, db='magalu'):
        super().__init__(user, password, host, port, db)
        #self.create_database(db)
        #self.create_clientes_table()

    def create_clientes_table(self):
        query = f"""
            CREATE TABLE clientes (
            cliente_id SERIAL PRIMARY KEY,
            cliente_name VARCHAR (50),
            cliente_email VARCHAR (50) UNIQUE,
            TOKEN VARCHAR (50) UNIQUE);
        """
        print(query)
        try:
            self.exec_query(query)
            return True
        except Exception as e:
            print(e)
            return False

    def get_all_from_table(self, table_name):
        query = f'SELECT * FROM "{table_name}"'
        print(query)
        conn = self.connection()
        df = pd.read_sql_query(query, conn)
        return df

    def insert_into_clientes(self, name, email):
        token = self.create_token(name+email)
        query = f"INSERT INTO clientes (cliente_name, cliente_email, cliente_token) VALUES ('{name.lower()}', '{email.lower()}', '{token}')"
        self.exec_query(query)
        return query

    def create_token(self, text):
        bytes_text = bytes(text.lower(), 'utf-8')
        token = base64.b64encode(bytes_text).decode()
        return token

    def check_token(self, token):
        decoded = base64.b64decode(token).decode()
        df = pd.read_sql_query('SELECT * from clientes')
        return decoded in df['token'].values()

    def get_token(self, name, email):
        query = f"""
        SELECT cliente_token FROM clientes
        WHERE cliente_name = '{name}' and cliente_email = '{email}'"""
        conn = self.connection()
        df = pd.read_sql_query(query, conn)
        return df.iloc[0,0]
