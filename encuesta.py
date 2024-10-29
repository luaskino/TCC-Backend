from conexion import get_db_connection, release_db_connection
import traceback
import psycopg2.extras  # Importa el módulo para usar DictCursor

def obtener_encuesta_id(encuesta_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM encuesta WHERE pedido_id = %s
            """, (encuesta_id,))
            encuesta = cursor.fetchone()  # Asegúrate de que esta línea esté bien escrita
            return dict(encuesta) if encuesta else None  # La variable 'encuesta' debe estar definida
    except Exception as e:
        print(f"Error al obtener encuesta con ID {encuesta_id}: {e}")
        print(traceback.format_exc())
        return None
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


