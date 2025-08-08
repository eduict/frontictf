import mysql.connector

conexion= mysql.connector.connect(
    host="192.169.1.80",
    user="phantomdb",
    password="DreamTeam",
    database="rh"
)

cursor=conexion.connect()

cursor.execute("""
    CREATE TABLE estudiantes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rut VARCHAR(12) NOT NULL,
    dverificador CHAR(1) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NOT NULL,
    curso VARCHAR(20) NOT NULL
    );
""")