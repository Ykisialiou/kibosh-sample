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


def newDB():
    if is_memory_db():
        return DBMemory()
    else:
        return DBMysql()


def is_memory_db():
    vcap_service = json.loads(os.environ.get('VCAP_SERVICES', "{}"))
    if vcap_service.get("mysql", None):
        return False
    return True


class DBMysql:
    def __init__(self):
        self.credentials = self.get_credentials_from_env()
        self.in_memory = False

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
        self.write_schema()
        if len(self.list()) == 0:
            for entry in seed_data:
                self.insert(entry)

    def insert(self, entry):
        self.__begin_tx()
        raw_sql = """
        insert into kibosh(description, image_path, votes_up, votes_down)
        values(%(description)s, %(image_path)s, %(votes_up)s, %(votes_down)s)
        """
        self.cursor.execute(raw_sql, entry)
        self.__end_tx()

    def list(self):
        self.__begin_tx()
        self.cursor.execute("select * from kibosh")
        rows = self.cursor.fetchall()
        self.__end_tx()

        return rows

    def vote_up(self, id):
        self.__begin_tx()
        raw_sql = """update kibosh set votes_up = votes_up + 1 where id = %(id)s"""
        self.cursor.execute(raw_sql, {"id": id})
        self.__end_tx()

    def vote_down(self, id):
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


class DBMemory:
    def __init__(self):
        self.memory_db = []
        self.next_id = 0
        self.in_memory = True

    def bootstrap(self):
        if len(self.list()) == 0:
            for entry in seed_data:
                self.insert(entry)

    def insert(self, entry):
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

    def list(self):
        return self.memory_db

    def vote_up(self, id):
        for entry in self.memory_db:
            if entry["id"] == id:
                entry["votes_up"] += 1

    def vote_down(self, id):
        for entry in self.memory_db:
            if entry["id"] == id:
                entry["votes_down"] += 1
