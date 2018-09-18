import mysql.connector as db

schema = """
create table if not exists kibosh (
  my_key varchar(128) not null,
  my_value varchar(1024),
  primary key (my_key)
);
"""


class DB:
    def __init__(self, credentials):
        self.credentials = credentials

    def __begin_tx(self):
        self.connection = db.connect(**self.credentials)
        self.cursor = self.connection.cursor(dictionary=True)

    def __end_tx(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

        self.cursor = None
        self.connection = None

    def write_schema(self):
        self.__begin_tx()
        self.cursor.execute(schema)
        self.__end_tx()

    def insert(self, key, value):
        self.__begin_tx()
        raw_sql = """
insert into kibosh(my_key, my_value)
values(%(my_key_value)s, %(my_value_value)s)
on duplicate key update my_value=%(my_value_value)s
"""
        self.cursor.execute(raw_sql, {
            "my_key_value": key,
            "my_value_value": value,
        })
        self.__end_tx()

    def query(self, key):
        self.__begin_tx()

        self.cursor.execute("select * from kibosh where my_key=%(my_key_value)s", {"my_key_value": key})
        rows = self.cursor.fetchall()

        self.__end_tx()
        return rows

    def list(self):
        self.__begin_tx()

        self.cursor.execute("select * from kibosh")
        rows = self.cursor.fetchall()

        self.__end_tx()
        return rows

    def delete(self, key):
        self.__begin_tx()

        self.cursor.execute("delete from kibosh where my_key=%(my_key_value)s", {"my_key_value": key})

        self.__end_tx()
