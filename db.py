import mysql.connector
# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='TusharSQL@123',
        database='ats_system',
        buffered=True
    )
    return conn
