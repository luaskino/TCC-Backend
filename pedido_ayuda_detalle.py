from conexion import get_db_connection, release_db_connection
import traceback
import psycopg2.extras

import traceback

def actualizar_pedido_detalle(detalle_id, data):
    conn = get_db_connection()
    try:
        # Imprimir los datos recibidos para depuración
        print(f"Datos recibidos para actualizar detalle con ID {detalle_id}: {data}")

        # Consultar la cantidad actual del pedido antes de hacer la actualización
        with conn.cursor() as cursor:
            cursor.execute("SELECT cantidad FROM pedido_ayuda_detalle WHERE detalle_id = %s", (detalle_id,))
            resultado = cursor.fetchone()

            # Si no se encuentra el detalle con el detalle_id proporcionado, retornar False
            if not resultado:
                print(f"No se encontró el detalle con ID {detalle_id}")
                return False

            cantidad_actual = resultado[0]

            # Validar que la cantidad_recibida no sea mayor que la cantidad
            if 'cantidad_recibida' in data and data['cantidad_recibida'] > cantidad_actual:
                print(f"Error: La cantidad recibida ({data['cantidad_recibida']}) no puede ser mayor que la cantidad disponible ({cantidad_actual})")
                return False

        # Crear la lista de columnas a actualizar
        update_columns = []
        update_values = []

        # Verificar qué campos están en el data y construir la consulta dinámica
        if 'item_nombre' in data:
            update_columns.append("item_nombre = %s")
            update_values.append(data['item_nombre'] or None)
        
        if 'cantidad' in data:
            update_columns.append("cantidad = %s")
            update_values.append(int(data['cantidad']) if data['cantidad'] is not None else None)
        
        if 'cantidad_recibida' in data:
            update_columns.append("cantidad_recibida = %s")
            update_values.append(int(data['cantidad_recibida']) if data['cantidad_recibida'] is not None else 0)

        # Si no hay campos para actualizar, retornar False
        if not update_columns:
            return False

        # Añadir el ID del detalle al final de los valores para el WHERE
        update_values.append(detalle_id)

        # Crear la consulta dinámica
        query = f"""
            UPDATE pedido_ayuda_detalle
            SET {', '.join(update_columns)}
            WHERE detalle_id = %s
        """

        # Ejecutar la consulta
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(update_values))
            conn.commit()
            return True

    except Exception as e:
        print(f"Error al actualizar detalle con ID {detalle_id}: {e}")
        print(traceback.format_exc())
        return False
    finally:
        release_db_connection(conn)
