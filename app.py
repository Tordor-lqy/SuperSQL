import json
from flask import request, render_template
from werkzeug.routing import BaseConverter
from utils.DBM import *
from utils.ApiLoad import ApiLoad, app
from jinja2 import Template
from flask_cors import CORS
import base64
import paramiko
import re
import time
import requests
import json
import pymysql
import threading

CORS(app, cors_allowed_origins="*")


class WildcardConverter(BaseConverter):
    regex = r'(|/.*?)'
    weight = 200


app.url_map.converters['wildcard'] = WildcardConverter


def check_uri(path):
    conn, cur = connect_db("api")
    cur.execute(
        "SELECT * FROM api_config LEFT JOIN api_db_config"
        " ON api_config.api_db_id = api_db_config.db_id "
        "WHERE api_config.api_uri = '%s' " % path)
    api_info = cur.fetchone()
    # print(api_info)
    if api_info is None:
        return False, {"msg": "api error or not exist"}
    return True, api_info


def connect_api_db(api_info):
    conn = pymysql.connect(
        host=api_info["db_host"],  # 主机名（或IP地址）
        port=api_info["db_port"],  # 端口号，默认为3306
        user=api_info["db_user"],  # 用户名
        password=api_info["db_password"],  # 密码
        charset='utf8mb4'  # 设置字符编码
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    conn.select_db(api_info["db_name"])
    return conn, cursor


def query_str(query):
    return ",".join(["%s=%s" % (i, i) for i in query])


@app.route("/api<wildcard:path>", methods=["GET", "PUT", "POST", "DELETE"])
def all_api(path):
    effective, data = check_uri(path)
    if not effective:
        return data, 400
    if request.method != data["api_method"]:
        return {"msg": "invalid"}, 400
    # 解析base64编码获取参数信息
    query = list(eval(base64.b64decode(data["api_query"]).decode("UTF-8")))
    conn, cur = connect_api_db(data)
    # 获取 query 参数
    p = request.args
    for q in query:
        exec("%s = p.get('%s')" % (q, q))
        if eval(q) is None:
            return {"msg": "error"}, 400
        print(eval(q))
    # 获取 json 参数
    try:
        body = request.get_json()
    except Exception as e:
        body = {}

    var = {}
    if data["api_is_use_script"] == 1:
        try:
            code = base64.b64decode(data["api_script"]).decode("UTF-8")
            # print(eval(code))
            exec(eval(code))
        except Exception as e:
            return {"msg": f"script error {e}"}, 400

    try:
        # print(query_str(query) + ("," if len(query) > 0 else "") + "body=body , var=var")
        sql = eval(
            f'Template(data["api_sql"])'
            f'.render'
            f'({query_str(query) + ("," if len(query) > 0 else "") + "body=body , var=var"})')
    except Exception as e:
        return {"msg": f"sql template error {e}"}, 400
    # print(sql)
    try:
        cur.execute(sql)
        conn.commit()
        res = cur.fetchall()
        res = [] if res == () else res
    except Exception as e:
        return {"msg": f"exec sql error {e}"}, 400

    var["data"] = res

    if data["api_is_use_post_script"] != 1:
        return var["data"]

    try:
        code = base64.b64decode(data["api_post_script"]).decode("UTF-8")
        exec(eval(code))
    except Exception as e:
        return {"msg": f"post script error {e}"}, 400

    return var["data"]


@app.route("/super/get/all/api")
def get_all_api():
    conn, cur = connect_db("api")
    cur.execute("select * from api_config")
    return cur.fetchall()


@app.route("/super/get/all/database")
def get_all_database():
    conn, cur = connect_db("api")
    cur.execute("select * from api_db_config")
    return cur.fetchall()


@app.route("/super/update/api", methods=["POST"])
def update_api():
    body = request.get_json()
    conn, cur = connect_db("api")
    cur.execute(
        f"update api_config set"
        f"  api_method = \"{body['api_method']}\""
        f", api_sql = \'{body['api_sql']}\'"
        f", api_query = \"{body['api_query']}\""
        f", api_uri = \"{body['api_uri']}\""
        f", api_db_id = \"{body['api_db_id']}\""
        f", api_is_use_body = \"{body['api_is_use_body']}\""
        f", api_is_use_script = \"{body['api_is_use_script']}\""
        f", api_script = \"{body['api_script']}\""
        f", api_post_script = \"{body['api_post_script']}\""
        f", api_is_use_post_script = \"{body['api_is_use_post_script']}\""
        f"where api_config_id = \"{body['api_config_id']}\""
    )
    conn.commit()
    return {"status": "success", "data": body}


@app.route("/super/insert/api", methods=["POST"])
def insert_api():
    body = request.get_json()
    conn, cur = connect_db("api")
    cur.execute(
        f"insert into api_config (api_method, api_sql, api_query, api_uri , api_db_id) "
        f"values "
        f"(\"{body['api_method']}\" "
        f", \'{body['api_sql']}\'"
        f", \"{body['api_query']}\""
        f", \"{body['api_uri']}\" "
        f", \"{body['api_db_id']}\")"
    )
    conn.commit()
    return {"status": "success", "data": body}


@app.route("/super/delete/api", methods=["DELETE"])
def delete_api():
    api_config_id = request.args.get("api_config_id")
    conn, cur = connect_db("api")
    cur.execute(f"delete from api_config where api_config_id = \"{api_config_id}\"")
    conn.commit()
    return {"status": "success"}


@app.route("/super/insert/database", methods=["POST"])
def insert_database():
    body = request.get_json()
    conn, cur = connect_db("api")
    cur.execute(f"insert into api_db_config (db_type , db_name , db_host , db_port , db_user , db_password )"
                f"value "
                f"(\"{body['db_type']}\" "
                f", \"{body['db_name']}\""
                f", \"{body['db_host']}\""
                f", \"{body['db_port']}\""
                f", \"{body['db_user']}\""
                f", \"{body['db_password']}\")"
                )
    conn.commit()
    return {"status": "success"}


@app.route("/super/update/database", methods=["POST"])
def update_database():
    body = request.get_json()
    conn, cur = connect_db("api")
    cur.execute(f"update api_db_config set db_type = \"{body['db_type']}\""
                f", db_name = \"{body['db_name']}\""
                f", db_password = \"{body['db_password']}\""
                f", db_host = \"{body['db_host']}\""
                f", db_user = \"{body['db_user']}\""
                f",db_port = \"{body['db_port']}\""
                f"where db_id = \"{body['db_id']}\"")
    conn.commit()
    return {"status": "success"}


@app.route("/super/delete/database", methods=["DELETE"])
def delete_database():
    db_id = request.args.get("db_id")
    conn, cur = connect_db("api")
    cur.execute(f"delete from api_db_config where db_id = \"{db_id}\"")
    conn.commit()
    return {"status": "success"}


@app.route("/super/get/all/auth", methods=["GET"])
def get_all_auth():
    conn, cur = connect_db("api")
    cur.execute(f"select * from api_authentication")
    result = cur.fetchall()
    if result == ():
        result = []
    return result


@app.route("/super/add/auth", methods=["POST"])
def post_auth():
    conn, cur = connect_db("api")
    body = request.get_json()
    cur.execute(
        "insert into api_authentication ( authentication_secretkey,authentication_algorithm,authentication_name)"
        "value "
        f"('{body['authentication_secretkey']}'"
        f", '{body['authentication_algorithm']}'"
        f", '{body['authentication_name']}'"
        f")"
    )


@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7876)
