from utils.DBM import connect_db
from base import app


def create_api_def_name(uri):
    return uri[0:].replace("/", "_")


def query_contact(query):
    return ",".join([i for i in query])


get = """
@%s.route('%s' , methods=['%s'])
def %s():
    conn, cursor = connect_db('%s')
    cursor.execute('%s')
    return cursor.fetchall()"""


class ApiLoad():
    def __init__(self, api):
        self.api = api

    def create(self):
        for group_name, group in self.api.items():
            for v in group:
                exec(get % ("app", v["uri"], v["method"],
                            group_name + create_api_def_name(v['uri']),
                            group_name,
                            v["sql"]))
