import pymysql

dbs = {
    "api": {
        'host': 'localhost',
        'port': 3306,
        'database': 'supersql',
        'user': 'supersql',
        'password': 'bQDDCBx2EkbGfaHW'
    },
    "srf": {
        'host': 'localhost',
        'port': 3306,
        'database': 'small_red_flower',
        'user': 'small_red_flower',
        'password': 'Pxsk3xd47hmpAHf5'
    }
}


def connect_db(db_name):
    conn = pymysql.connect(
        host=dbs[db_name]["host"],  # 主机名（或IP地址）
        port=dbs[db_name]["port"],  # 端口号，默认为3306
        user=dbs[db_name]["user"],  # 用户名
        password=dbs[db_name]["password"],  # 密码
        charset='utf8mb4'  # 设置字符编码
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    conn.select_db(dbs[db_name]["database"])
    return conn, cursor
