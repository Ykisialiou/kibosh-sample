import mysql.connector as db
import json
import os

schema = """
create table if not exists kibosh (
  id int not null primary key AUTO_INCREMENT,
  description varchar(1024),
  image_path varchar(255), 
  votes_up int,
  votes_down int
);
"""

seed_data = [
    {
        "description": "Dog in cow's clothing",
        "image_path": "dog_with_cows.jpg",
        "votes_up": 2,
        "votes_down": 1,
    },
    {
        "description": "A rabbit mouse? A rabbit? Hybrid?",
        "image_path": "rabbit.jpg",
        "votes_up": 3,
        "votes_down": 0,
    },
]


class DB:
    def __init__(self):
        self.in_memory = self.is_memory_db()
        if self.in_memory:
            self.memory_db = []
            self.next_id = 0
        else:
            self.credentials = self.get_credentials_from_env()

    def is_memory_db(self):
        vcap_service = json.loads(os.environ.get('VCAP_SERVICES', "{}"))
        if vcap_service.get("mysql", ""):
            return False
        return True

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

    def bootstrap(self):
        if not self.in_memory:
            self.write_schema()
        if len(self.list()) == 0:
            for entry in seed_data:
                self.insert(entry)

    def insert(self, entry):
        if self.in_memory:
            self.insert_memory(entry)
        else:
            self.insert_mysql(entry)

    def insert_memory(self, entry):
        self.memory_db.append(
            {
                "id": self.next_id,
                "description": entry["description"],
                "image_path": entry["image_path"],
                "votes_up": entry["votes_up"],
                "votes_down": entry["votes_down"]
            }
        )
        self.next_id += 1

    def insert_mysql(self, entry):
        self.__begin_tx()
        raw_sql = """
        insert into kibosh(description, image_path, votes_up, votes_down)
        values(%(description)s, %(image_path)s, %(votes_up)s, %(votes_down)s)
        """
        self.cursor.execute(raw_sql, entry)
        self.__end_tx()

    def list(self):
        if self.in_memory:
            return self.memory_db

        self.__begin_tx()
        self.cursor.execute("select * from kibosh")
        rows = self.cursor.fetchall()
        self.__end_tx()

        return rows

    def vote_up(self, id):
        if self.in_memory:
            for entry in self.memory_db:
                if entry["id"] == id:
                    entry["votes_up"] += 1
        else:
            self.__begin_tx()
            raw_sql = """update kibosh set votes_up = votes_up + 1 where id = %(id)s"""
            self.cursor.execute(raw_sql, {"id": id})
            self.__end_tx()

    def vote_down(self, id):
        if self.in_memory:
            for entry in self.memory_db:
                if entry["id"] == id:
                    entry["votes_down"] += 1
        else:
            self.__begin_tx()
            raw_sql = """update kibosh set votes_down = votes_down + 1 where id = %(id)s"""
            self.cursor.execute(raw_sql, {"id": id})
            self.__end_tx()

    def get_credentials_from_env(self):
        vcap_service = json.loads(os.environ['VCAP_SERVICES'])

        my_sql = vcap_service['mysql'][0]
        secrets = my_sql["credentials"]["secrets"][0]
        services = my_sql["credentials"]["services"][0]

        return {
            'host': services["status"]["loadBalancer"]["ingress"][0]["ip"],
            'database': 'my_db',
            'user': 'root',
            'password': secrets["data"]["mysql-root-password"],
            'port': services["spec"]["ports"][0]["port"]
        }
