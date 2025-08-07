import mysql.connector

# --- Configuración de la Base de Datos ---
DB_CONFIG = {
    'host': '192.168.1.80',
    'user': 'phantomdb',
    'password': 'DreamTeam',
    'database': 'rh'
}

def modificar_columna_certificado():
    """
    Se conecta a la base de datos y modifica la columna 'certificado'
    de la tabla 'capacitaciones' para que pueda almacenar URLs.
    """
    conn = None
    cursor = None
    try:
        print("Intentando conectar a la base de datos...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Comando SQL para modificar el tipo de columna.
        # Se ha quitado el punto y coma final para evitar errores de sintaxis en algunos conectores.
        sql_command = "ALTER TABLE capacitaciones MODIFY COLUMN certificado VARCHAR(255)"
        
        print(f"Conexión exitosa. Ejecutando comando SQL: {sql_command}")
        cursor.execute(sql_command)
        
        # Confirmar los cambios
        conn.commit()
        
        print("Comando ejecutado correctamente.")
        print("La columna 'certificado' ahora es de tipo VARCHAR(255).")
        
    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        print("Asegúrate de que la configuración de la base de datos sea correcta y el servidor esté en funcionamiento.")
        
    finally:
        # Cierra el cursor y la conexión si se establecieron
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Conexión a la base de datos cerrada.")

if __name__ == '__main__':
    modificar_columna_certificado()