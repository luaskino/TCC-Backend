from conexion import get_db_connection, release_db_connection
import traceback
import psycopg2.extras  # Importa el módulo para usar DictCursor

def obtener_categorias():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM categoria_donacion")
            pedidos = cursor.fetchall()
            return [dict(pedido) for pedido in pedidos]
    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        print(traceback.format_exc())
        return []
    finally:
        release_db_connection(conn)