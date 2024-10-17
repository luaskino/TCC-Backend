import psycopg2
from psycopg2 import pool

# Configuración de la conexión a la base de datos
def get_db_connection():
    return psycopg2.connect(
        "postgresql://neondb_owner:i7MqZnBdOl1e@ep-curly-fog-a5soxpav.us-east-2.aws.neon.tech/donapy?sslmode=require"
)

# Si prefieres usar un pool de conexiones
# connection_pool = pool.SimpleConnectionPool(1, 10,
#     user='neondb_owner',
#     password='i7MqZnBdOl1e',
#     host='ep-curly-fog-a5soxpav.us-east-2.aws.neon.tech',
#     port='5432',
#     database='donapy',
#     sslmode='require'
# )

# def get_db_connection():
#     return connection_pool.getconn()

def release_db_connection(conn):
    conn.close()
    # connection_pool.putconn(conn)
