# Sistema de Guardia Hospitalaria

Aplicación de escritorio para la gestión integral de guardias hospitalarias.

## ¿Qué hace la app?

- Permite registrar y gestionar pacientes.
- Permite registrar y gestionar consultas médicas, con sistema de triage y sugerencia automática de prioridad.
- Permite gestionar el personal y sus turnos.
- Permite llevar el inventario de recursos médicos y recibir alertas de stock crítico.
- Incluye sistema de login y registro de usuarios con contraseñas seguras.
- Permite cambiar el estado de las consultas: En espera, Atendida, Cancelada.
- Permite eliminar consultas.
- Muestra estadísticas y reportes gráficos de la actividad.

## Tecnologías utilizadas

- **Lenguaje principal:** Python 3.12+
- **Interfaz gráfica:** Tkinter, ttkbootstrap
- **Librerías adicionales:**
  - [tkcalendar](https://github.com/j4321/tkcalendar) (selección de fechas)
  - [Pillow](https://python-pillow.org/) (imágenes)
  - [matplotlib](https://matplotlib.org/) (gráficos)
- **Base de datos:** SQLite (archivo local `.db`)

## Instalación

1. **Clona el repositorio:**
   ```sh
   git clone https://github.com/guidodeona/Sistema-Guardia-Hospitalaria.git
   cd Sistema-Guardia-Hospitalaria
   ```

2. **Instala las dependencias:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación:**
   ```sh
   python main.py
   ```

## Ejemplo de uso

1. Inicia la aplicación con `python main.py`.
2. Regístrate como usuario o inicia sesión.
3. Usa el menú para agregar pacientes, registrar consultas, gestionar personal y recursos.
4. Cambia el estado de las consultas según corresponda.
5. Consulta las estadísticas y reportes desde el menú "Reportes".

## Estructura del proyecto

- `main.py`: Interfaz principal y lógica de la aplicación.
- `db.py`: Funciones de acceso y gestión de la base de datos.
- `requirements.txt`: Lista de dependencias necesarias.

## Autor

- Guido de Oña
