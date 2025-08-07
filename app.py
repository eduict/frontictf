from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para los mensajes flash

# --- Configuración de la Base de Datos ---
DB_CONFIG = {
    'host': '192.168.1.80',
    'user': 'phantomdb',
    'password': 'DreamTeam',
    'database': 'rh'
}

def get_db_connection():
    """Establece la conexión con la base de datos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        flash(f"Error de conexión con la base de datos: {err}", "danger")
        return None

# --- Rutas del Panel Principal ---
@app.route('/')
def index():
    return render_template('index.html')

# --- CRUD Puestos ---
@app.route('/puestos')
def listar_puestos():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM puestos ORDER BY id_puestos")
        puestos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('puestos_list.html', puestos=puestos)
    return redirect(url_for('index'))

@app.route('/puestos/gestionar', methods=['GET', 'POST'])
@app.route('/puestos/gestionar/<int:id_puestos>', methods=['GET', 'POST'])
def gestionar_puesto(id_puestos=None):
    if request.method == 'POST':
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            details = request.form
            if id_puestos:
                query = "UPDATE puestos SET nombre=%s, descripcion=%s, salario_base=%s WHERE id_puestos=%s"
                cursor.execute(query, (details['nombre'], details['descripcion'], details['salario_base'], id_puestos))
            else:
                query = "INSERT INTO puestos (nombre, descripcion, salario_base) VALUES (%s, %s, %s)"
                cursor.execute(query, (details['nombre'], details['descripcion'], details['salario_base']))
            conn.commit()
            cursor.close()
            conn.close()
        return redirect(url_for('listar_puestos'))

    puesto = None
    if id_puestos:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM puestos WHERE id_puestos = %s", (id_puestos,))
            puesto = cursor.fetchone()
            cursor.close()
            conn.close()
    return render_template('puestos_form.html', puesto=puesto)

@app.route('/puestos/eliminar/<int:id_puestos>', methods=['POST'])
def eliminar_puesto(id_puestos):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM empleado_puesto WHERE id_puesto = %s", (id_puestos,))
            cursor.execute("DELETE FROM puestos WHERE id_puestos = %s", (id_puestos,))
            conn.commit()
            flash('Puesto eliminado correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al eliminar el puesto: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('listar_puestos'))

# --- CRUD Empleados ---
@app.route('/empleados')
def listar_empleados():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, c.comuna AS comuna_nombre 
            FROM empleados e
            LEFT JOIN comuna c ON e.id_comuna = c.id_comuna
            ORDER BY id_empleados
        """)
        empleados = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('empleados_list.html', empleados=empleados)
    return redirect(url_for('index'))

@app.route('/empleados/gestionar', methods=['GET', 'POST'])
@app.route('/empleados/gestionar/<int:id_empleados>', methods=['GET', 'POST'])
def gestionar_empleado(id_empleados=None):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('listar_empleados'))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        details = {
            'nombre': request.form['nombre'], 'apellido': request.form['apellido'],
            'fecha_nacimiento': request.form['fecha_nacimiento'] or None,
            'direccion': request.form['direccion'], 'telefono': request.form['telefono'],
            'correo': request.form['correo'], 'estado_civil': request.form['estado_civil'],
            'nacionalidad': request.form['nacionalidad'],
            'fecha_ingreso': request.form['fecha_ingreso'] or None,
            'id_comuna': request.form['id_comuna'] or None
        }
        
        if id_empleados:
            details['id_empleados'] = id_empleados
            query = """UPDATE empleados SET nombre=%(nombre)s, apellido=%(apellido)s, fecha_nacimiento=%(fecha_nacimiento)s, direccion=%(direccion)s, telefono=%(telefono)s, correo=%(correo)s, estado_civil=%(estado_civil)s, nacionalidad=%(nacionalidad)s, fecha_ingreso=%(fecha_ingreso)s, id_comuna=%(id_comuna)s WHERE id_empleados=%(id_empleados)s"""
        else:
            query = """INSERT INTO empleados (nombre, apellido, fecha_nacimiento, direccion, telefono, correo, estado_civil, nacionalidad, fecha_ingreso, id_comuna) VALUES (%(nombre)s, %(apellido)s, %(fecha_nacimiento)s, %(direccion)s, %(telefono)s, %(correo)s, %(estado_civil)s, %(nacionalidad)s, %(fecha_ingreso)s, %(id_comuna)s)"""
        
        try:
            cursor.execute(query, details)
            conn.commit()
            flash('Empleado guardado correctamente.', 'success')
        except mysql.connector.Error as err:
            flash(f"Error al guardar el empleado: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('listar_empleados'))

    empleado = None
    if id_empleados:
        cursor.execute("SELECT * FROM empleados WHERE id_empleados = %s", (id_empleados,))
        empleado = cursor.fetchone()
    
    cursor.execute("SELECT id_comuna, comuna FROM comuna ORDER BY comuna")
    comunas = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('empleados_form.html', empleado=empleado, comunas=comunas)

@app.route('/empleados/eliminar/<int:id_empleados>', methods=['POST'])
def eliminar_empleado(id_empleados):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM contratos WHERE id_empleado = %s", (id_empleados,))
            cursor.execute("DELETE FROM capacitaciones WHERE id_empleado = %s", (id_empleados,))
            cursor.execute("DELETE FROM permisos WHERE id_empleado = %s", (id_empleados,))
            cursor.execute("DELETE FROM empleado_puesto WHERE id_empleado = %s", (id_empleados,))
            
            cursor.execute("DELETE FROM empleados WHERE id_empleados = %s", (id_empleados,))
            conn.commit()
            flash('Empleado eliminado correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al eliminar el empleado: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('listar_empleados'))

# --- CRUD Contratos ---
@app.route('/contratos')
def listar_contratos():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, e.nombre, e.apellido
            FROM contratos c JOIN empleados e ON c.id_empleado = e.id_empleados
            ORDER BY id_contratos
        """)
        contratos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('contratos_list.html', contratos=contratos)
    return redirect(url_for('index'))

@app.route('/contratos/gestionar', methods=['GET', 'POST'])
@app.route('/contratos/gestionar/<int:id_contratos>', methods=['GET', 'POST'])
def gestionar_contrato(id_contratos=None):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('listar_contratos'))
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        details = {
            'id_empleado': request.form['id_empleado'],
            'tipo_contrato': request.form['tipo_contrato'],
            'fecha_inicio': request.form['fecha_inicio'] or None,
            'fecha_fin': request.form['fecha_fin'] or None,
            'salario': request.form['salario']
        }
        if id_contratos:
            details['id_contratos'] = id_contratos
            query = "UPDATE contratos SET id_empleado=%(id_empleado)s, tipo_contrato=%(tipo_contrato)s, fecha_inicio=%(fecha_inicio)s, fecha_fin=%(fecha_fin)s, salario=%(salario)s WHERE id_contratos=%(id_contratos)s"
        else:
            query = "INSERT INTO contratos (id_empleado, tipo_contrato, fecha_inicio, fecha_fin, salario) VALUES (%(id_empleado)s, %(tipo_contrato)s, %(fecha_inicio)s, %(fecha_fin)s, %(salario)s)"
        
        try:
            cursor.execute(query, details)
            conn.commit()
            flash('Contrato guardado correctamente.', 'success')
        except mysql.connector.Error as err:
            flash(f"Error al guardar el contrato: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('listar_contratos'))

    contrato = None
    if id_contratos:
        cursor.execute("SELECT * FROM contratos WHERE id_contratos = %s", (id_contratos,))
        contrato = cursor.fetchone()
    
    cursor.execute("SELECT id_empleados, nombre, apellido FROM empleados ORDER BY apellido, nombre")
    empleados = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('contratos_form.html', contrato=contrato, empleados=empleados)

@app.route('/contratos/eliminar/<int:id_contratos>', methods=['POST'])
def eliminar_contrato(id_contratos):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM contratos WHERE id_contratos = %s", (id_contratos,))
            conn.commit()
            flash('Contrato eliminado correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al eliminar el contrato: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('listar_contratos'))

# --- CRUD Empleado_Puesto ---
@app.route('/empleado_puesto')
def listar_empleado_puesto():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                ep.*,
                e.nombre as empleado_nombre,
                e.apellido as empleado_apellido,
                p.nombre as puesto_nombre
            FROM empleado_puesto ep
            JOIN empleados e ON ep.id_empleado = e.id_empleados
            JOIN puestos p ON ep.id_puesto = p.id_puestos
            ORDER BY id_empleado_puesto
        """)
        asignaciones = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('empleado_puesto_list.html', asignaciones=asignaciones)
    return redirect(url_for('index'))

@app.route('/empleado_puesto/gestionar', methods=['GET', 'POST'])
@app.route('/empleado_puesto/gestionar/<int:id_empleado_puesto>', methods=['GET', 'POST'])
def gestionar_empleado_puesto(id_empleado_puesto=None):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('listar_empleado_puesto'))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        details = {
            'id_empleado': request.form['id_empleado'],
            'id_puesto': request.form['id_puesto'],
            'especialidad_docente': request.form['especialidad_docente'] or None
        }
        
        if id_empleado_puesto:
            details['id_empleado_puesto'] = id_empleado_puesto
            query = "UPDATE empleado_puesto SET id_empleado=%(id_empleado)s, id_puesto=%(id_puesto)s, especialidad_docente=%(especialidad_docente)s WHERE id_empleado_puesto=%(id_empleado_puesto)s"
        else:
            query = "INSERT INTO empleado_puesto (id_empleado, id_puesto, especialidad_docente) VALUES (%(id_empleado)s, %(id_puesto)s, %(especialidad_docente)s)"
        
        try:
            cursor.execute(query, details)
            conn.commit()
            flash('Asignación guardada correctamente.', 'success')
        except mysql.connector.Error as err:
            flash(f"Error al guardar la asignación: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('listar_empleado_puesto'))

    asignacion = None
    if id_empleado_puesto:
        cursor.execute("SELECT * FROM empleado_puesto WHERE id_empleado_puesto = %s", (id_empleado_puesto,))
        asignacion = cursor.fetchone()
    
    cursor.execute("SELECT id_empleados, nombre, apellido FROM empleados ORDER BY apellido, nombre")
    empleados = cursor.fetchall()

    cursor.execute("SELECT id_puestos, nombre FROM puestos ORDER BY nombre")
    puestos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('empleado_puesto_form.html', asignacion=asignacion, empleados=empleados, puestos=puestos)

@app.route('/empleado_puesto/eliminar/<int:id_empleado_puesto>', methods=['POST'])
def eliminar_empleado_puesto(id_empleado_puesto):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM empleado_puesto WHERE id_empleado_puesto = %s", (id_empleado_puesto,))
            conn.commit()
            flash('Asignación eliminada correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al eliminar la asignación: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('listar_empleado_puesto'))

# --- CRUD Capacitaciones ---
@app.route('/capacitaciones')
def listar_capacitaciones():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, e.nombre AS empleado_nombre, e.apellido AS empleado_apellido
            FROM capacitaciones c
            JOIN empleados e ON c.id_empleado = e.id_empleados
            ORDER BY id_capacitaciones
        """)
        capacitaciones = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('capacitaciones_list.html', capacitaciones=capacitaciones)
    return redirect(url_for('index'))

@app.route('/capacitaciones/gestionar', methods=['GET', 'POST'])
@app.route('/capacitaciones/gestionar/<int:id_capacitaciones>', methods=['GET', 'POST'])
def gestionar_capacitacion(id_capacitaciones=None):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('listar_capacitaciones'))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        details = {
            'id_empleado': request.form['id_empleado'],
            'nombre_curso': request.form['nombre_curso'],
            'institucion': request.form['institucion'],
            'fecha_inicio': request.form['fecha_inicio'] or None,
            'fecha_fin': request.form['fecha_fin'] or None,
            'certificado': request.form['certificado'] or None
        }

        if id_capacitaciones:
            details['id_capacitaciones'] = id_capacitaciones
            query = """
                UPDATE capacitaciones SET
                id_empleado=%(id_empleado)s, nombre_curso=%(nombre_curso)s,
                institucion=%(institucion)s, fecha_inicio=%(fecha_inicio)s,
                fecha_fin=%(fecha_fin)s, certificado=%(certificado)s
                WHERE id_capacitaciones=%(id_capacitaciones)s
            """
        else:
            query = """
                INSERT INTO capacitaciones (
                id_empleado, nombre_curso, institucion, fecha_inicio, fecha_fin, certificado
                ) VALUES (
                %(id_empleado)s, %(nombre_curso)s, %(institucion)s, %(fecha_inicio)s, %(fecha_fin)s, %(certificado)s
                )
            """
        
        try:
            cursor.execute(query, details)
            conn.commit()
            flash('Capacitación guardada correctamente.', 'success')
        except mysql.connector.Error as err:
            flash(f"Error al guardar la capacitación: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('listar_capacitaciones'))

    capacitacion = None
    if id_capacitaciones:
        cursor.execute("SELECT * FROM capacitaciones WHERE id_capacitaciones = %s", (id_capacitaciones,))
        capacitacion = cursor.fetchone()
    
    cursor.execute("SELECT id_empleados, nombre, apellido FROM empleados ORDER BY apellido, nombre")
    empleados = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('capacitaciones_form.html', capacitacion=capacitacion, empleados=empleados)

@app.route('/capacitaciones/eliminar/<int:id_capacitaciones>', methods=['POST'])
def eliminar_capacitacion(id_capacitaciones):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM capacitaciones WHERE id_capacitaciones = %s", (id_capacitaciones,))
            conn.commit()
            flash('Capacitación eliminada correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al eliminar la capacitación: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('listar_capacitaciones'))

# --- CRUD Comunas ---
@app.route('/comunas')
def listar_comunas():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM comuna ORDER BY id_comuna")
        comunas = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('comunas_list.html', comunas=comunas)
    return redirect(url_for('index'))

@app.route('/comunas/gestionar', methods=['GET', 'POST'])
@app.route('/comunas/gestionar/<int:id_comuna>', methods=['GET', 'POST'])
def gestionar_comuna(id_comuna=None):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('listar_comunas'))
    
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        details = {
            'comuna': request.form['comuna']
        }
        if id_comuna:
            details['id_comuna'] = id_comuna
            query = "UPDATE comuna SET comuna=%(comuna)s WHERE id_comuna=%(id_comuna)s"
        else:
            query = "INSERT INTO comuna (comuna) VALUES (%(comuna)s)"
        
        try:
            cursor.execute(query, details)
            conn.commit()
            flash('Comuna guardada correctamente.', 'success')
        except mysql.connector.Error as err:
            flash(f"Error al guardar la comuna: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('listar_comunas'))

    comuna = None
    if id_comuna:
        cursor.execute("SELECT * FROM comuna WHERE id_comuna = %s", (id_comuna,))
        comuna = cursor.fetchone()
    
    cursor.close()
    conn.close()

    return render_template('comunas_form.html', comuna=comuna)

@app.route('/comunas/eliminar/<int:id_comuna>', methods=['POST'])
def eliminar_comuna(id_comuna):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE empleados SET id_comuna = NULL WHERE id_comuna = %s", (id_comuna,))
            cursor.execute("DELETE FROM comuna WHERE id_comuna = %s", (id_comuna,))
            conn.commit()
            flash('Comuna eliminada correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al eliminar la comuna: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('listar_comunas'))

# --- CRUD Permisos ---
@app.route('/permisos')
def listar_permisos():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                p.*,
                e.nombre AS empleado_nombre,
                e.apellido AS empleado_apellido
            FROM permisos p
            JOIN empleados e ON p.id_empleado = e.id_empleados
            ORDER BY id_permisos
        """)
        permisos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('permisos_list.html', permisos=permisos)
    return redirect(url_for('index'))

@app.route('/permisos/gestionar', methods=['GET', 'POST'])
@app.route('/permisos/gestionar/<int:id_permisos>', methods=['GET', 'POST'])
def gestionar_permiso(id_permisos=None):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('listar_permisos'))
    
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        details = {
            'id_empleado': request.form['id_empleado'],
            'tipo': request.form['tipo'],
            'fecha_inicio': request.form['fecha_inicio'] or None,
            'fecha_fin': request.form['fecha_fin'] or None,
            'estado': request.form['estado'],
            'motivo': request.form['motivo'] or None
        }

        if id_permisos:
            details['id_permisos'] = id_permisos
            query = "UPDATE permisos SET id_empleado=%(id_empleado)s, tipo=%(tipo)s, fecha_inicio=%(fecha_inicio)s, fecha_fin=%(fecha_fin)s, estado=%(estado)s, motivo=%(motivo)s WHERE id_permisos=%(id_permisos)s"
        else:
            query = "INSERT INTO permisos (id_empleado, tipo, fecha_inicio, fecha_fin, estado, motivo) VALUES (%(id_empleado)s, %(tipo)s, %(fecha_inicio)s, %(fecha_fin)s, %(estado)s, %(motivo)s)"
        
        try:
            cursor.execute(query, details)
            conn.commit()
            flash('Permiso guardado correctamente.', 'success')
        except mysql.connector.Error as err:
            flash(f"Error al guardar el permiso: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('listar_permisos'))

    permiso = None
    if id_permisos:
        cursor.execute("SELECT * FROM permisos WHERE id_permisos = %s", (id_permisos,))
        permiso = cursor.fetchone()
    
    cursor.execute("SELECT id_empleados, nombre, apellido FROM empleados ORDER BY apellido, nombre")
    empleados = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('permisos_form.html', permiso=permiso, empleados=empleados)

@app.route('/permisos/eliminar/<int:id_permisos>', methods=['POST'])
def eliminar_permiso(id_permisos):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM permisos WHERE id_permisos = %s", (id_permisos,))
            conn.commit()
            flash('Permiso eliminado correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al eliminar el permiso: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('listar_permisos'))
    
# --- CRUD Postulantes ---
@app.route('/postulantes')
def listar_postulantes():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                p.*,
                puesto.nombre AS puesto_nombre,
                com.comuna AS comuna_nombre
            FROM postulantes p
            LEFT JOIN puestos puesto ON p.id_puesto = puesto.id_puestos
            LEFT JOIN comuna com ON p.id_comuna = com.id_comuna
            ORDER BY id_postulantes
        """)
        postulantes = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('postulantes_list.html', postulantes=postulantes)
    return redirect(url_for('index'))

@app.route('/postulantes/gestionar', methods=['GET', 'POST'])
@app.route('/postulantes/gestionar/<int:id_postulantes>', methods=['GET', 'POST'])
def gestionar_postulante(id_postulantes=None):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('listar_postulantes'))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        details = {
            'nombre': request.form['nombre'],
            'apellido': request.form['apellido'],
            'fecha_nacimiento': request.form['fecha_nacimiento'] or None,
            'correo': request.form['correo'],
            'telefono': request.form['telefono'],
            'direccion': request.form['direccion'],
            'nacionalidad': request.form['nacionalidad'],
            'nivel_educativo': request.form['nivel_educativo'],
            'experiencia_previa': request.form['experiencia_previa'],
            'id_puesto': request.form['id_puesto'] or None,
            'fecha_postulacion': request.form['fecha_postulacion'] or None,
            'estado': request.form['estado'],
            'comentarios': request.form['comentarios'] or None,
            'id_comuna': request.form['id_comuna'] or None
        }

        if id_postulantes:
            details['id_postulantes'] = id_postulantes
            query = """
                UPDATE postulantes SET
                nombre=%(nombre)s, apellido=%(apellido)s, fecha_nacimiento=%(fecha_nacimiento)s,
                correo=%(correo)s, telefono=%(telefono)s, direccion=%(direccion)s,
                nacionalidad=%(nacionalidad)s, nivel_educativo=%(nivel_educativo)s,
                experiencia_previa=%(experiencia_previa)s, id_puesto=%(id_puesto)s,
                fecha_postulacion=%(fecha_postulacion)s, estado=%(estado)s,
                comentarios=%(comentarios)s, id_comuna=%(id_comuna)s
                WHERE id_postulantes=%(id_postulantes)s
            """
        else:
            query = """
                INSERT INTO postulantes (
                nombre, apellido, fecha_nacimiento, correo, telefono, direccion,
                nacionalidad, nivel_educativo, experiencia_previa, id_puesto,
                fecha_postulacion, estado, comentarios, id_comuna
                ) VALUES (
                %(nombre)s, %(apellido)s, %(fecha_nacimiento)s, %(correo)s, %(telefono)s,
                %(direccion)s, %(nacionalidad)s, %(nivel_educativo)s, %(experiencia_previa)s,
                %(id_puesto)s, %(fecha_postulacion)s, %(estado)s, %(comentarios)s, %(id_comuna)s
                )
            """
        
        try:
            cursor.execute(query, details)
            conn.commit()
            flash('Postulante guardado correctamente.', 'success')
        except mysql.connector.Error as err:
            flash(f"Error al guardar el postulante: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('listar_postulantes'))

    postulante = None
    if id_postulantes:
        cursor.execute("SELECT * FROM postulantes WHERE id_postulantes = %s", (id_postulantes,))
        postulante = cursor.fetchone()
    
    cursor.execute("SELECT id_puestos, nombre FROM puestos ORDER BY nombre")
    puestos = cursor.fetchall()
    
    cursor.execute("SELECT id_comuna, comuna FROM comuna ORDER BY comuna")
    comunas = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('postulantes_form.html', postulante=postulante, puestos=puestos, comunas=comunas)

@app.route('/postulantes/eliminar/<int:id_postulantes>', methods=['POST'])
def eliminar_postulante(id_postulantes):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM seguimiento_postulantes WHERE id_postulante = %s", (id_postulantes,))
            cursor.execute("DELETE FROM postulantes WHERE id_postulantes = %s", (id_postulantes,))
            conn.commit()
            flash('Postulante eliminado correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al eliminar el postulante: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('listar_postulantes'))
    
# --- CRUD Seguimiento de Postulantes ---
@app.route('/seguimiento_postulantes')
def listar_seguimiento_postulantes():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                sp.*,
                p.nombre AS postulante_nombre,
                p.apellido AS postulante_apellido
            FROM seguimiento_postulantes sp
            JOIN postulantes p ON sp.id_postulante = p.id_postulantes
            ORDER BY id_seguimiento_postulantes
        """)
        seguimientos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('seguimiento_postulantes_list.html', seguimientos=seguimientos)
    return redirect(url_for('index'))

@app.route('/seguimiento_postulantes/gestionar', methods=['GET', 'POST'])
@app.route('/seguimiento_postulantes/gestionar/<int:id_seguimiento_postulantes>', methods=['GET', 'POST'])
def gestionar_seguimiento_postulante(id_seguimiento_postulantes=None):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('listar_seguimiento_postulantes'))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        details = {
            'id_postulante': request.form['id_postulante'],
            'fecha': request.form['fecha'] or None,
            'etapa': request.form['etapa'],
            'observaciones': request.form['observaciones'] or None
        }

        if id_seguimiento_postulantes:
            details['id_seguimiento_postulantes'] = id_seguimiento_postulantes
            query = """
                UPDATE seguimiento_postulantes SET
                id_postulante=%(id_postulante)s, fecha=%(fecha)s, etapa=%(etapa)s,
                observaciones=%(observaciones)s
                WHERE id_seguimiento_postulantes=%(id_seguimiento_postulantes)s
            """
        else:
            query = """
                INSERT INTO seguimiento_postulantes (
                id_postulante, fecha, etapa, observaciones
                ) VALUES (
                %(id_postulante)s, %(fecha)s, %(etapa)s, %(observaciones)s
                )
            """
        
        try:
            cursor.execute(query, details)
            conn.commit()
            flash('Seguimiento guardado correctamente.', 'success')
        except mysql.connector.Error as err:
            flash(f"Error al guardar el seguimiento: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('listar_seguimiento_postulantes'))

    seguimiento = None
    if id_seguimiento_postulantes:
        cursor.execute("SELECT * FROM seguimiento_postulantes WHERE id_seguimiento_postulantes = %s", (id_seguimiento_postulantes,))
        seguimiento = cursor.fetchone()
    
    cursor.execute("SELECT id_postulantes, nombre, apellido FROM postulantes ORDER BY apellido, nombre")
    postulantes = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('seguimiento_postulantes_form.html', seguimiento=seguimiento, postulantes=postulantes)

@app.route('/seguimiento_postulantes/eliminar/<int:id_seguimiento_postulantes>', methods=['POST'])
def eliminar_seguimiento_postulante(id_seguimiento_postulantes):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM seguimiento_postulantes WHERE id_seguimiento_postulantes = %s", (id_seguimiento_postulantes,))
            conn.commit()
            flash('Seguimiento eliminado correctamente.', 'success')
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error al eliminar el seguimiento: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('listar_seguimiento_postulantes'))

if __name__ == '__main__':
    app.run(debug=True)