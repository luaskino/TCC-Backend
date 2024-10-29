from conexion import get_db_connection, release_db_connection
import traceback
import psycopg2.extras  # Importa el módulo para usar DictCursor

def obtener_encuesta_id(pedido_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM encuesta WHERE pedido_id = %s
            """, (pedido_id,))
            encuestas = cursor.fetchall()  # Utiliza fetchall() para obtener todos los registros
            return [dict(encuesta) for encuesta in encuestas] if encuestas else []  # Convierte cada registro a un diccionario
    except Exception as e:
        print(f"Error al obtener encuestas con pedido_id {pedido_id}: {e}")
        print(traceback.format_exc())
        return []
    finally:
        release_db_connection(conn)


def insertar_encuesta(data):
    conn = get_db_connection()
    try:
        print("Datos recibidos para registrar encuesta:", data)
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO encuesta (pedido_id, usuario_id, ayudaste, comentario, fecha)
                VALUES (%s, %s, %s, %s, CURRENT_DATE)
            """, (
                int(data.get('pedido_id')),
                int(data.get('usuario_id')),
                data.get('ayudaste'),
                data.get('comentario') or None
            ))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error al registrar encuesta: {e}")
        print(traceback.format_exc())
        return False
    finally:
        release_db_connection(conn)


