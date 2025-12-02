import sqlite3
from contextlib import contextmanager
import hashlib
from datetime import datetime

DB_PATH = 'hospital_guard.db'

@contextmanager
def get_db_connection(db_path=DB_PATH):
    """Context manager for database connections."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

def init_db(db_path=DB_PATH):
    """Inicializa la base de datos y crea las tablas si no existen."""
    with get_db_connection(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            dni TEXT UNIQUE,
            edad INTEGER,
            genero TEXT,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            obra_social TEXT,
            numero_afiliado TEXT,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            fecha_consulta DATETIME,
            motivo TEXT,
            diagnostico TEXT,
            tratamiento TEXT,
            medico TEXT,
            estado TEXT,
            prioridad TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS personal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            especialidad TEXT,
            matricula TEXT UNIQUE,
            turno TEXT,
            estado TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS recursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            nombre TEXT NOT NULL,
            cantidad INTEGER,
            estado TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )''')
        conn.commit()

# --- Pacientes ---

def agregar_paciente(datos):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO pacientes (nombre, apellido, dni, edad, genero, telefono, email, direccion, obra_social, numero_afiliado) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            datos['nombre'], datos['apellido'], datos['dni'], datos['edad'], datos['genero'], 
            datos['telefono'], datos['email'], datos['direccion'], datos['obra_social'], datos['numero_afiliado']))
        conn.commit()

def obtener_pacientes():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM pacientes')
        return c.fetchall()

def actualizar_paciente(paciente_id, datos):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''UPDATE pacientes SET nombre=?, apellido=?, dni=?, edad=?, genero=?, telefono=?, email=?, direccion=?, obra_social=?, numero_afiliado=? 
                     WHERE id=?''', (
            datos['nombre'], datos['apellido'], datos['dni'], datos['edad'], datos['genero'], 
            datos['telefono'], datos['email'], datos['direccion'], datos['obra_social'], datos['numero_afiliado'], paciente_id))
        conn.commit()

def eliminar_paciente(paciente_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM pacientes WHERE id=?', (paciente_id,))
        conn.commit()

def pacientes():
    return obtener_pacientes()

def pacientes_filtrado(valor):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM pacientes WHERE nombre LIKE ? OR apellido LIKE ? OR dni LIKE ?''', 
                  (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
        return c.fetchall()

# --- Consultas ---

def agregar_consulta(datos):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO consultas (paciente_id, fecha_consulta, motivo, diagnostico, tratamiento, medico, estado, prioridad) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
            datos['paciente_id'], datos['fecha_consulta'], datos['motivo'], datos.get('diagnostico', ''), 
            datos.get('tratamiento', ''), datos['medico'], datos['estado'], datos['prioridad']))
        conn.commit()

def obtener_consultas():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM consultas')
        return c.fetchall()

def actualizar_consulta(consulta_id, datos):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''UPDATE consultas SET paciente_id=?, fecha_consulta=?, motivo=?, diagnostico=?, tratamiento=?, medico=?, estado=?, prioridad=? 
                     WHERE id=?''', (
            datos['paciente_id'], datos['fecha_consulta'], datos['motivo'], datos.get('diagnostico', ''), 
            datos.get('tratamiento', ''), datos['medico'], datos['estado'], datos['prioridad'], consulta_id))
        conn.commit()

def eliminar_consulta(consulta_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM consultas WHERE id=?', (consulta_id,))
        conn.commit()

def consultas():
    """Devuelve todas las consultas con datos de paciente."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT c.id, p.nombre || " " || p.apellido, c.fecha_consulta, c.motivo, c.prioridad, c.medico, c.estado 
                     FROM consultas c JOIN pacientes p ON c.paciente_id = p.id ORDER BY c.fecha_consulta DESC''')
        return c.fetchall()

def consultas_filtrado(valor):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT c.id, p.nombre || " " || p.apellido, c.fecha_consulta, c.motivo, c.prioridad, c.medico, c.estado 
                     FROM consultas c JOIN pacientes p ON c.paciente_id = p.id 
                     WHERE p.nombre LIKE ? OR p.apellido LIKE ? OR c.motivo LIKE ? OR c.medico LIKE ? 
                     ORDER BY c.fecha_consulta DESC''', (f'%{valor}%', f'%{valor}%', f'%{valor}%', f'%{valor}%'))
        return c.fetchall()

def consultas_en_espera_lista():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT c.id, p.nombre || " " || p.apellido, c.motivo, c.prioridad, datetime(c.fecha_consulta) as tiempo_espera 
                     FROM consultas c JOIN pacientes p ON c.paciente_id = p.id 
                     WHERE c.estado = 'En espera' 
                     ORDER BY CASE c.prioridad WHEN 'Alta' THEN 1 WHEN 'Media' THEN 2 WHEN 'Baja' THEN 3 END, c.fecha_consulta''')
        return c.fetchall()

def consultas_recientes():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT c.id, p.nombre || " " || p.apellido, c.fecha_consulta, c.motivo, c.prioridad, c.estado 
                     FROM consultas c JOIN pacientes p ON c.paciente_id = p.id 
                     ORDER BY c.fecha_consulta DESC LIMIT 10''')
        return c.fetchall()

def actualizar_estado_consulta(consulta_id, nuevo_estado):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('UPDATE consultas SET estado=? WHERE id=?', (nuevo_estado, consulta_id))
        conn.commit()

# --- Personal ---

def agregar_personal(datos):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO personal (nombre, apellido, especialidad, matricula, turno, estado) 
                     VALUES (?, ?, ?, ?, ?, ?)''', (
            datos['nombre'], datos['apellido'], datos['especialidad'], datos['matricula'], datos['turno'], datos['estado']))
        conn.commit()

def obtener_personal():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM personal')
        return c.fetchall()

def actualizar_personal(personal_id, datos):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''UPDATE personal SET nombre=?, apellido=?, especialidad=?, matricula=?, turno=?, estado=? 
                     WHERE id=?''', (
            datos['nombre'], datos['apellido'], datos['especialidad'], datos['matricula'], datos['turno'], datos['estado'], personal_id))
        conn.commit()

def eliminar_personal(personal_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM personal WHERE id=?', (personal_id,))
        conn.commit()

def personal():
    return obtener_personal()

def personal_filtrado(valor):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM personal WHERE nombre LIKE ? OR apellido LIKE ? OR matricula LIKE ?''', 
                  (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
        return c.fetchall()

# --- Recursos ---

def agregar_recurso(datos):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO recursos (tipo, nombre, cantidad, estado) VALUES (?, ?, ?, ?)''', (
            datos['tipo'], datos['nombre'], datos['cantidad'], datos['estado']))
        conn.commit()

def obtener_recursos():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM recursos')
        return c.fetchall()

def actualizar_recurso(recurso_id, datos):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''UPDATE recursos SET tipo=?, nombre=?, cantidad=?, estado=? WHERE id=?''', (
            datos['tipo'], datos['nombre'], datos['cantidad'], datos['estado'], recurso_id))
        conn.commit()

def eliminar_recurso(recurso_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM recursos WHERE id=?', (recurso_id,))
        conn.commit()

def recursos():
    return obtener_recursos()

def recursos_filtrado(valor):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM recursos WHERE tipo LIKE ? OR nombre LIKE ?''', (f'%{valor}%', f'%{valor}%'))
        return c.fetchall()

def recursos_criticos_lista():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM recursos WHERE cantidad <= 5')
        return c.fetchall()

# --- Estadísticas y Usuarios ---

def consultas_en_espera():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM consultas WHERE estado = "En espera"')
        return c.fetchone()[0]

def consultas_hoy():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM consultas WHERE date(fecha_consulta) = date("now")')
        return c.fetchone()[0]

def personal_activo():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM personal WHERE estado = "Activo"')
        return c.fetchone()[0]

def recursos_criticos():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM recursos WHERE cantidad <= 5')
        return c.fetchone()[0]

def obtener_estadisticas_prioridad():
    """Devuelve estadísticas de consultas por prioridad para el día actual."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT prioridad, COUNT(*) as cantidad FROM consultas 
                     WHERE date(fecha_consulta) = date('now') GROUP BY prioridad''')
        return c.fetchall()

def obtener_estadisticas_recursos_estado():
    """Devuelve estadísticas de recursos por estado."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT estado, COUNT(*) as cantidad FROM recursos GROUP BY estado''')
        return c.fetchall()

def registrar_usuario(usuario, password):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM usuarios WHERE usuario=?', (usuario,))
        if c.fetchone():
            return False
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute('INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)', (usuario, password_hash))
        conn.commit()
        return True

def verificar_usuario(usuario, password):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT password_hash FROM usuarios WHERE usuario=?', (usuario,))
        row = c.fetchone()
        if not row:
            return False
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return row[0] == password_hash