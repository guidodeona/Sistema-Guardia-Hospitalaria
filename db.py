import sqlite3
from datetime import datetime
import hashlib

def init_db(db_path='hospital_guard.db'):
    """Inicializa la base de datos y crea las tablas si no existen."""
    conn = sqlite3.connect(db_path)
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
    conn.close()

# Aquí puedes agregar funciones CRUD para cada entidad, por ejemplo:
def agregar_paciente(datos, db_path='hospital_guard.db'):
    """Agrega un paciente a la base de datos."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO pacientes (nombre, apellido, dni, edad, genero, telefono, email, direccion, obra_social, numero_afiliado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        datos['nombre'], datos['apellido'], datos['dni'], datos['edad'], datos['genero'], datos['telefono'], datos['email'], datos['direccion'], datos['obra_social'], datos['numero_afiliado']))
    conn.commit()
    conn.close()

def obtener_pacientes(db_path='hospital_guard.db'):
    """Devuelve una lista de todos los pacientes."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM pacientes')
    pacientes = c.fetchall()
    conn.close()
    return pacientes

def actualizar_paciente(paciente_id, datos, db_path='hospital_guard.db'):
    """Actualiza los datos de un paciente."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''UPDATE pacientes SET nombre=?, apellido=?, dni=?, edad=?, genero=?, telefono=?, email=?, direccion=?, obra_social=?, numero_afiliado=? WHERE id=?''', (
        datos['nombre'], datos['apellido'], datos['dni'], datos['edad'], datos['genero'], datos['telefono'], datos['email'], datos['direccion'], datos['obra_social'], datos['numero_afiliado'], paciente_id))
    conn.commit()
    conn.close()

def eliminar_paciente(paciente_id, db_path='hospital_guard.db'):
    """Elimina un paciente por su ID."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM pacientes WHERE id=?', (paciente_id,))
    conn.commit()
    conn.close()

# Consultas

def agregar_consulta(datos, db_path='hospital_guard.db'):
    """Agrega una consulta a la base de datos."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO consultas (paciente_id, fecha_consulta, motivo, diagnostico, tratamiento, medico, estado, prioridad) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
        datos['paciente_id'], datos['fecha_consulta'], datos['motivo'], datos.get('diagnostico', ''), datos.get('tratamiento', ''), datos['medico'], datos['estado'], datos['prioridad']))
    conn.commit()
    conn.close()

def obtener_consultas(db_path='hospital_guard.db'):
    """Devuelve una lista de todas las consultas."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM consultas')
    consultas = c.fetchall()
    conn.close()
    return consultas

def actualizar_consulta(consulta_id, datos, db_path='hospital_guard.db'):
    """Actualiza los datos de una consulta."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''UPDATE consultas SET paciente_id=?, fecha_consulta=?, motivo=?, diagnostico=?, tratamiento=?, medico=?, estado=?, prioridad=? WHERE id=?''', (
        datos['paciente_id'], datos['fecha_consulta'], datos['motivo'], datos.get('diagnostico', ''), datos.get('tratamiento', ''), datos['medico'], datos['estado'], datos['prioridad'], consulta_id))
    conn.commit()
    conn.close()

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

def obtener_personal(db_path='hospital_guard.db'):
    """Devuelve una lista de todo el personal."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM personal')
    personal = c.fetchall()
    conn.close()
    return personal

def actualizar_personal(personal_id, datos, db_path='hospital_guard.db'):
    """Actualiza los datos de un miembro del personal."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''UPDATE personal SET nombre=?, apellido=?, especialidad=?, matricula=?, turno=?, estado=? WHERE id=?''', (
        datos['nombre'], datos['apellido'], datos['especialidad'], datos['matricula'], datos['turno'], datos['estado'], personal_id))
    conn.commit()
    conn.close()

def eliminar_personal(personal_id, db_path='hospital_guard.db'):
    """Elimina un miembro del personal por su ID."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM personal WHERE id=?', (personal_id,))
    conn.commit()
    conn.close()

# Recursos

def agregar_recurso(datos, db_path='hospital_guard.db'):
    """Agrega un recurso al inventario."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO recursos (tipo, nombre, cantidad, estado) VALUES (?, ?, ?, ?)''', (
        datos['tipo'], datos['nombre'], datos['cantidad'], datos['estado']))
    conn.commit()
    conn.close()

def obtener_recursos(db_path='hospital_guard.db'):
    """Devuelve una lista de todos los recursos."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM recursos')
    recursos = c.fetchall()
    conn.close()
    return recursos

def actualizar_recurso(recurso_id, datos, db_path='hospital_guard.db'):
    """Actualiza los datos de un recurso."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''UPDATE recursos SET tipo=?, nombre=?, cantidad=?, estado=? WHERE id=?''', (
        datos['tipo'], datos['nombre'], datos['cantidad'], datos['estado'], recurso_id))
    conn.commit()
    conn.close()

def eliminar_recurso(recurso_id, db_path='hospital_guard.db'):
    """Elimina un recurso por su ID."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM recursos WHERE id=?', (recurso_id,))
    conn.commit()
    conn.close()

# Funciones utilitarias para estadísticas y consultas específicas

def consultas_en_espera(db_path='hospital_guard.db'):
    """Devuelve el número de consultas en espera."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM consultas WHERE estado = "En espera"')
    result = c.fetchone()[0]
    conn.close()
    return result

def consultas_hoy(db_path='hospital_guard.db'):
    """Devuelve el número de consultas del día actual."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM consultas WHERE date(fecha_consulta) = date("now")')
    result = c.fetchone()[0]
    conn.close()
    return result

def personal_activo(db_path='hospital_guard.db'):
    """Devuelve el número de personal activo."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM personal WHERE estado = "Activo"')
    result = c.fetchone()[0]
    conn.close()
    return result

def recursos_criticos(db_path='hospital_guard.db'):
    """Devuelve el número de recursos críticos (cantidad <= 5)."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM recursos WHERE cantidad <= 5')
    result = c.fetchone()[0]
    conn.close()
    return result

def consultas_recientes(db_path='hospital_guard.db'):
    """Devuelve las 10 consultas más recientes con datos de paciente."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT c.id, p.nombre || " " || p.apellido, c.fecha_consulta, c.motivo, c.prioridad, c.estado FROM consultas c JOIN pacientes p ON c.paciente_id = p.id ORDER BY c.fecha_consulta DESC LIMIT 10''')
    result = c.fetchall()
    conn.close()
    return result

def pacientes(db_path='hospital_guard.db'):
    """Devuelve todos los pacientes."""
    return obtener_pacientes(db_path)

def pacientes_filtrado(valor, db_path='hospital_guard.db'):
    """Devuelve pacientes filtrados por nombre, apellido o dni."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT * FROM pacientes WHERE nombre LIKE ? OR apellido LIKE ? OR dni LIKE ?''', (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
    result = c.fetchall()
    conn.close()
    return result

def consultas(db_path='hospital_guard.db'):
    """Devuelve todas las consultas con datos de paciente."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT c.id, p.nombre || " " || p.apellido, c.fecha_consulta, c.motivo, c.prioridad, c.medico, c.estado FROM consultas c JOIN pacientes p ON c.paciente_id = p.id ORDER BY c.fecha_consulta DESC''')
    result = c.fetchall()
    conn.close()
    return result

def consultas_filtrado(valor, db_path='hospital_guard.db'):
    """Devuelve consultas filtradas por paciente, motivo o médico."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT c.id, p.nombre || " " || p.apellido, c.fecha_consulta, c.motivo, c.prioridad, c.medico, c.estado FROM consultas c JOIN pacientes p ON c.paciente_id = p.id WHERE p.nombre LIKE ? OR p.apellido LIKE ? OR c.motivo LIKE ? OR c.medico LIKE ? ORDER BY c.fecha_consulta DESC''', (f'%{valor}%', f'%{valor}%', f'%{valor}%', f'%{valor}%'))
    result = c.fetchall()
    conn.close()
    return result

def consultas_en_espera_lista(db_path='hospital_guard.db'):
    """Devuelve la lista de consultas en espera para el triage."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT c.id, p.nombre || " " || p.apellido, c.motivo, c.prioridad, datetime(c.fecha_consulta) as tiempo_espera FROM consultas c JOIN pacientes p ON c.paciente_id = p.id WHERE c.estado = 'En espera' ORDER BY CASE c.prioridad WHEN 'Alta' THEN 1 WHEN 'Media' THEN 2 WHEN 'Baja' THEN 3 END, c.fecha_consulta''')
    result = c.fetchall()
    conn.close()
    return result

def personal(db_path='hospital_guard.db'):
    """Devuelve todo el personal."""
    return obtener_personal(db_path)

def personal_filtrado(valor, db_path='hospital_guard.db'):
    """Devuelve personal filtrado por nombre, apellido o matrícula."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT * FROM personal WHERE nombre LIKE ? OR apellido LIKE ? OR matricula LIKE ?''', (f'%{valor}%', f'%{valor}%', f'%{valor}%'))
    result = c.fetchall()
    conn.close()
    return result

def recursos(db_path='hospital_guard.db'):
    """Devuelve todos los recursos."""
    return obtener_recursos(db_path)

def recursos_filtrado(valor, db_path='hospital_guard.db'):
    """Devuelve recursos filtrados por tipo o nombre."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT * FROM recursos WHERE tipo LIKE ? OR nombre LIKE ?''', (f'%{valor}%', f'%{valor}%'))
    result = c.fetchall()
    conn.close()
    return result

def recursos_criticos_lista(db_path='hospital_guard.db'):
    """Devuelve la lista de recursos críticos (cantidad <= 5)."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM recursos WHERE cantidad <= 5')
    result = c.fetchall()
    conn.close()
    return result

def actualizar_estado_consulta(consulta_id, nuevo_estado, db_path='hospital_guard.db'):
    """Actualiza solo el estado de una consulta."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('UPDATE consultas SET estado=? WHERE id=?', (nuevo_estado, consulta_id))
    conn.commit()
    conn.close()

def registrar_usuario(usuario, password, db_path='hospital_guard.db'):
    """Registra un nuevo usuario con contraseña hasheada. Devuelve True si se registró, False si ya existe."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT id FROM usuarios WHERE usuario=?', (usuario,))
    if c.fetchone():
        conn.close()
        return False
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute('INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)', (usuario, password_hash))
    conn.commit()
    conn.close()
    return True

def verificar_usuario(usuario, password, db_path='hospital_guard.db'):
    """Verifica si el usuario y la contraseña (hasheada) coinciden."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT password_hash FROM usuarios WHERE usuario=?', (usuario,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return row[0] == password_hash 