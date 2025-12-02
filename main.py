import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkcalendar import Calendar, DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from datetime import datetime
import db  # Nuevo módulo para la base de datos
import hashlib

class HospitalGuardApp:
    """
    Aplicación principal de guardia hospitalaria.
    Gestiona la interfaz gráfica y utiliza el módulo db para la lógica de datos.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Guardia Hospitalaria")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configurar tema y estilos
        self.style = tb.Style(theme="cosmo")
        
        # Configurar colores y estilos personalizados
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'accent': '#e74c3c',
            'background': '#ecf0f1',
            'text': '#2c3e50'
        }
        
        db.init_db()  # Inicializa la base de datos
        
        # Crear el menú principal
        self.create_menu()
        
        # Frame principal con diseño moderno
        self.main_frame = tb.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar la página de inicio
        self.show_home()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Inicio", command=self.show_home)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Pacientes
        pacientes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pacientes", menu=pacientes_menu)
        pacientes_menu.add_command(label="Nuevo Paciente", command=self.show_registro_paciente)
        pacientes_menu.add_command(label="Lista de Pacientes", command=self.show_lista_pacientes)
        
        # Menú Consultas
        consultas_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Consultas", menu=consultas_menu)
        consultas_menu.add_command(label="Nueva Consulta", command=self.show_nueva_consulta)
        consultas_menu.add_command(label="Triage", command=self.show_triage)
        consultas_menu.add_command(label="Lista de Consultas", command=self.show_lista_consultas)
        
        # Menú Personal
        personal_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Personal", menu=personal_menu)
        personal_menu.add_command(label="Gestionar Personal", command=self.show_gestion_personal)
        personal_menu.add_command(label="Turnos", command=self.show_turnos)
        
        # Menú Recursos
        recursos_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Recursos", menu=recursos_menu)
        recursos_menu.add_command(label="Inventario", command=self.show_inventario)
        recursos_menu.add_command(label="Alertas", command=self.show_alertas)
        
        # Menú Reportes
        reportes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reportes", menu=reportes_menu)
        reportes_menu.add_command(label="Estadísticas", command=self.show_estadisticas)

    def show_home(self):
        self.clear_main_frame()
        # Título con estilo moderno
        title_frame = tb.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(title_frame, text="Sistema de Guardia Hospitalaria", font=('Helvetica', 28, 'bold'), foreground=self.colors['primary']).pack()
        
        # Frame para estadísticas rápidas
        stats_frame = tb.LabelFrame(self.main_frame, text="Estado Actual", padding="20")
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Obtener estadísticas
        en_espera = db.consultas_en_espera()
        consultas_hoy = db.consultas_hoy()
        personal_activo = db.personal_activo()
        recursos_criticos = db.recursos_criticos()
        
        # Mostrar estadísticas en tarjetas
        stats_grid = tb.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, pady=10)
        self.create_stat_card(stats_grid, "Pacientes en Espera", en_espera, "👥", 0)
        self.create_stat_card(stats_grid, "Consultas del Día", consultas_hoy, "📋", 1)
        self.create_stat_card(stats_grid, "Personal Activo", personal_activo, "👨‍⚕️", 2)
        self.create_stat_card(stats_grid, "Recursos Críticos", recursos_criticos, "⚠️", 3, color=self.colors['accent'] if recursos_criticos > 0 else self.colors['secondary'])
        
        # Alertas visuales
        if recursos_criticos > 0 or en_espera > 0:
            alert_frame = tb.Frame(self.main_frame)
            alert_frame.pack(fill=tk.X, pady=10)
            msg = ""
            if recursos_criticos > 0:
                msg += f"⚠️ Hay {recursos_criticos} recursos críticos. "
            if en_espera > 0:
                msg += f"🚨 Hay {en_espera} pacientes en espera."
            ttk.Label(alert_frame, text=msg, font=('Helvetica', 14, 'bold'), foreground=self.colors['accent']).pack()
        
        # Accesos rápidos
        actions_frame = tb.LabelFrame(self.main_frame, text="Accesos Rápidos", padding="20")
        actions_frame.pack(fill=tk.X, pady=10)
        actions_grid = tb.Frame(actions_frame)
        actions_grid.pack(fill=tk.X, pady=10)
        self.create_action_button(actions_grid, "Nuevo Paciente", "👤", self.show_registro_paciente, 0)
        self.create_action_button(actions_grid, "Nueva Consulta", "📝", self.show_nueva_consulta, 1)
        self.create_action_button(actions_grid, "Triage", "🚨", self.show_triage, 2)
        self.create_action_button(actions_grid, "Inventario", "📦", self.show_inventario, 3)
        self.create_action_button(actions_grid, "Agregar Recurso", "➕", self.abrir_modal_nuevo_recurso, 4)
        self.create_action_button(actions_grid, "Agregar Personal", "➕", self.abrir_modal_nuevo_personal, 5)
        
        # Frame para últimas consultas
        recent_frame = tb.LabelFrame(self.main_frame, text="Últimas Consultas", padding="20")
        recent_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        columns = ('ID', 'Paciente', 'Fecha', 'Motivo', 'Prioridad', 'Estado')
        tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=6)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        consultas = db.consultas_recientes()
        for row in consultas:
            tree.insert('', tk.END, values=row)
        
        # Frame para gráficos
        stats_graph_frame = tb.LabelFrame(self.main_frame, text="Gráficos", padding="20")
        stats_graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.grafico_consultas_por_prioridad(ax1)
        self.grafico_recursos_por_estado(ax2)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=stats_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_stat_card(self, parent, title, value, icon, column, color=None):
        card = tb.Frame(parent, padding="10", style='Card.TFrame')
        card.grid(row=0, column=column, padx=10, sticky='nsew')
        ttk.Label(card, text=icon, font=('Helvetica', 24)).pack()
        ttk.Label(card, text=str(value), font=('Helvetica', 20, 'bold'), foreground=color if color else self.colors['primary']).pack()
        ttk.Label(card, text=title).pack()

    def create_action_button(self, parent, text, icon, command, column):
        btn = tb.Button(parent, text=f"{icon}\n{text}", command=command, width=15)
        btn.grid(row=0, column=column, padx=10, pady=5)

    def show_registro_paciente(self):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Registro de Paciente", font=('Helvetica', 20, 'bold'), foreground=self.colors['primary']).pack(pady=10)
        button_frame_top = tb.Frame(self.main_frame)
        button_frame_top.pack(pady=(0, 10))
        def guardar_paciente():
            if not all([entries['nombre'].get(), entries['apellido'].get(), entries['dni'].get()]):
                messagebox.showwarning("Campos obligatorios", "Por favor complete Nombre, Apellido y DNI.")
                return
            try:
                edad = entries['edad'].get()
                if not edad or not edad.isdigit() or int(edad) <= 0:
                    messagebox.showwarning("Edad inválida", "Por favor ingrese una edad válida (solo números enteros positivos).")
                    return
                datos = {
                    'nombre': entries['nombre'].get(),
                    'apellido': entries['apellido'].get(),
                    'dni': entries['dni'].get(),
                    'edad': int(edad),
                    'genero': entries['genero'].get(),
                    'telefono': entries['telefono'].get(),
                    'email': entries['email'].get(),
                    'direccion': entries['direccion'].get(),
                    'obra_social': entries['obra_social'].get(),
                    'numero_afiliado': entries['numero_afiliado'].get()
                }
                db.agregar_paciente(datos)
                messagebox.showinfo("Éxito", "Paciente registrado correctamente")
                self.show_home()
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar el paciente: {str(e)}")
        tb.Button(button_frame_top, text="Guardar", bootstyle=tb.SUCCESS, command=guardar_paciente).pack(side=tk.LEFT, padx=10)
        tb.Button(button_frame_top, text="Cancelar", bootstyle=tb.SECONDARY, command=self.show_home).pack(side=tk.LEFT, padx=10)
        # Usar solo widgets de tkinter/ttk para el formulario de registro de paciente
        form_frame = ttk.Frame(self.main_frame, padding=30, style='TFrame')
        form_frame.pack(fill=tk.NONE, expand=False, pady=30)
        fields = [
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("DNI:", "dni"),
            ("Edad:", "edad"),
            ("Género:", "genero"),
            ("Teléfono:", "telefono"),
            ("Email:", "email"),
            ("Dirección:", "direccion"),
            ("Obra Social:", "obra_social"),
            ("Número de Afiliado:", "numero_afiliado")
        ]
        entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label, font=("Helvetica", 11), foreground="#2c3e50").grid(row=i, column=0, sticky=tk.W, pady=8, padx=(0, 10))
            if field == "genero":
                var = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=var, width=27, font=("Helvetica", 10))
                combo['values'] = ['Masculino', 'Femenino', 'Otro']
                combo.grid(row=i, column=1, pady=8, sticky=tk.W)
                entries[field] = var
            else:
                entry = ttk.Entry(form_frame, width=30, font=("Helvetica", 10), foreground="#495057")
                entry.grid(row=i, column=1, pady=8, sticky=tk.W)
                # Placeholder visual (texto tenue)
                entry.insert(0, label.replace(":", ""))
                entry.config(foreground="#b0b0b0")
                def on_focus_in(e, entry=entry, label=label):
                    if entry.get() == label.replace(":", ""):
                        entry.delete(0, tk.END)
                        entry.config(foreground="#495057")
                def on_focus_out(e, entry=entry, label=label):
                    if not entry.get():
                        entry.insert(0, label.replace(":", ""))
                        entry.config(foreground="#b0b0b0")
                entry.bind("<FocusIn>", on_focus_in)
                entry.bind("<FocusOut>", on_focus_out)
                entries[field] = entry
        # Botones abajo
        button_frame_bottom = ttk.Frame(self.main_frame)
        button_frame_bottom.pack(pady=20)
        ttk.Button(button_frame_bottom, text="Guardar", command=guardar_paciente).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame_bottom, text="Cancelar", command=self.show_home).pack(side=tk.LEFT, padx=10)

    def show_nueva_consulta(self):
        self.clear_main_frame()
        ttk.Label(self.main_frame, 
                text="Nueva Consulta",
                font=('Helvetica', 20, 'bold'),
                foreground=self.colors['primary']).pack(pady=10)
        form_frame = tk.Frame(self.main_frame, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(form_frame, text="Paciente:").grid(row=0, column=0, sticky=tk.W, pady=5)
        pacientes = db.pacientes()
        paciente_var = tk.StringVar()
        paciente_combo = ttk.Combobox(form_frame, textvariable=paciente_var, width=30)
        paciente_combo['values'] = [f"{p[0]} - {p[1]} {p[2]} (DNI: {p[3]})" for p in pacientes]
        paciente_combo.grid(row=0, column=1, pady=5)
        ttk.Label(form_frame, text="Motivo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        motivo_entry = ttk.Entry(form_frame, width=30)
        motivo_entry.grid(row=1, column=1, pady=5)
        ttk.Label(form_frame, text="Prioridad:").grid(row=2, column=0, sticky=tk.W, pady=5)
        prioridad_var = tk.StringVar()
        prioridad_combo = ttk.Combobox(form_frame, textvariable=prioridad_var, width=27)
        prioridad_combo['values'] = ['Alta', 'Media', 'Baja']
        prioridad_combo.grid(row=2, column=1, pady=5)
        ttk.Label(form_frame, text="Médico:").grid(row=3, column=0, sticky=tk.W, pady=5)
        medico_var = tk.StringVar()
        medico_combo = ttk.Combobox(form_frame, textvariable=medico_var, width=27)
        medico_combo['values'] = ['Dr. García', 'Dra. Martínez', 'Dr. Rodríguez']
        medico_combo.grid(row=3, column=1, pady=5)
        def actualizar_prioridad(*args):
            # Obtener edad del paciente seleccionado
            edad = ''
            if paciente_var.get():
                paciente_id = paciente_var.get().split(' - ')[0]
                for p in pacientes:
                    if str(p[0]) == paciente_id:
                        edad = p[4]  # La edad está en la columna 4
                        break
            sugerida = self.sugerir_prioridad(motivo_entry.get(), edad)
            prioridad_var.set(sugerida)
        motivo_entry.bind('<KeyRelease>', actualizar_prioridad)
        paciente_combo.bind('<<ComboboxSelected>>', actualizar_prioridad)
        # Inicializar prioridad sugerida
        actualizar_prioridad()
        def guardar_consulta():
            if not all([paciente_var.get(), motivo_entry.get(), prioridad_var.get(), medico_var.get()]):
                messagebox.showwarning("Advertencia", "Por favor complete todos los campos")
                return
            try:
                paciente_id = paciente_var.get().split(' - ')[0]
                datos = {
                    'paciente_id': paciente_id,
                    'fecha_consulta': datetime.now(),
                    'motivo': motivo_entry.get(),
                    'prioridad': prioridad_var.get(),
                    'medico': medico_var.get(),
                    'estado': 'En espera'
                }
                db.agregar_consulta(datos)
                messagebox.showinfo("Éxito", "Consulta registrada correctamente")
                self.show_home()
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar la consulta: {str(e)}")
        button_frame = tb.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        tb.Button(button_frame, text="Guardar", command=guardar_consulta).pack(side=tk.LEFT, padx=5)
        tb.Button(button_frame, text="Cancelar", command=self.show_home).pack(side=tk.LEFT, padx=5)

    def sugerir_prioridad(self, motivo, edad):
        motivo = motivo.lower()
        try:
            edad = int(edad)
        except:
            edad = None
        sintomas_alta = [
            'dolor de pecho', 'dificultad para respirar', 'convulsión', 'convulsiones', 'pérdida de conciencia', 'hemorragia',
            'accidente', 'quemadura grave', 'parálisis', 'traumatismo', 'shock', 'inconsciente', 'infarto', 'ictus', 'ataque cardíaco',
            'sangrado abundante', 'fractura expuesta', 'ahogo', 'paro cardíaco', 'dolor abdominal intenso', 'quemadura extensa', 'herida profunda'
        ]
        sintomas_media = [
            'fiebre alta', 'vómitos persistentes', 'fractura', 'caída', 'dolor moderado', 'infección', 'diarrea', 'dolor abdominal',
            'herida', 'dolor lumbar', 'mareo', 'tos persistente', 'dolor de oído', 'dolor de garganta', 'dolor de cabeza fuerte', 'bronquitis', 'asma', 'alergia', 'dolor articular'
        ]
        for sintoma in sintomas_alta:
            if sintoma in motivo:
                return 'Alta'
        if edad is not None and (edad < 5 or edad > 70):
            for sintoma in sintomas_media:
                if sintoma in motivo:
                    return 'Media'
        for sintoma in sintomas_media:
            if sintoma in motivo:
                return 'Media'
        return 'Baja'

    def show_triage(self):
        self.clear_main_frame()
        
        # Título
        ttk.Label(self.main_frame, 
                text="Sistema de Triage",
                font=('Helvetica', 20, 'bold'),
                foreground=self.colors['primary']).pack(pady=10)
        
        # Frame para la lista de pacientes en espera
        wait_frame = ttk.LabelFrame(self.main_frame, text="Pacientes en Espera", padding="20")
        wait_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear tabla
        columns = ('ID', 'Paciente', 'Motivo', 'Prioridad', 'Tiempo de Espera', 'Acciones')
        tree = ttk.Treeview(wait_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(wait_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar pacientes en espera
        consultas = db.consultas_en_espera_lista()
        
        for row in consultas:
            tree.insert('', tk.END, values=row)
        
        # Botones de acción
        action_frame = tb.Frame(self.main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        tb.Button(action_frame, text="Actualizar Lista", command=self.show_triage).pack(side=tk.LEFT, padx=5)
        tb.Button(action_frame, text="Volver al Inicio", command=self.show_home).pack(side=tk.LEFT, padx=5)

    def show_estadisticas(self):
        self.clear_main_frame()
        
        # Título
        ttk.Label(self.main_frame, 
                text="Estadísticas",
                font=('Helvetica', 20, 'bold'),
                foreground=self.colors['primary']).pack(pady=10)
        
        # Frame para gráficos
        stats_frame = tb.Frame(self.main_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Crear figura para matplotlib
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        self.grafico_consultas_por_prioridad(ax1)
        self.grafico_recursos_por_estado(ax2)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Crear canvas
        canvas = FigureCanvasTkAgg(fig, master=stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Botón para volver
        tb.Button(self.main_frame, text="Volver al Inicio", command=self.show_home).pack(pady=10)

    def show_lista_pacientes(self, page=1, page_size=50):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Lista de Pacientes", font=('Helvetica', 22, 'bold'), foreground=self.colors['primary']).pack(pady=(10, 0))
        actions_frame = tb.Frame(self.main_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        tb.Button(actions_frame, text="➕ Agregar", bootstyle=tb.SUCCESS, command=self.abrir_modal_nuevo_paciente).pack(side=tk.LEFT, padx=5)
        tb.Button(actions_frame, text="🔍 Buscar", bootstyle=tb.INFO, command=self.abrir_modal_buscar_paciente).pack(side=tk.LEFT, padx=5)
        tb.Button(actions_frame, text="✏️ Editar", bootstyle=tb.WARNING, command=lambda: self.abrir_modal_editar_paciente(self.get_selected_paciente(tree))).pack(side=tk.LEFT, padx=5)
        tb.Button(actions_frame, text="🗑️ Eliminar", bootstyle=tb.DANGER, command=lambda: self.eliminar_paciente(self.get_selected_paciente(tree))).pack(side=tk.LEFT, padx=5)
        columns = ("ID", "Nombre", "Apellido", "DNI", "Edad", "Género", "Teléfono", "Email", "Dirección", "Obra Social", "N° Afiliado")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), foreground=self.colors['primary'])
        style.configure("Treeview", font=("Helvetica", 10), rowheight=28)
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15, bootstyle=tb.INFO)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        # Paginación
        pacientes = db.pacientes()
        total = len(pacientes)
        start = (page-1)*page_size
        end = start+page_size
        pacientes_pagina = pacientes[start:end]
        for i in tree.get_children():
            tree.delete(i)
        for row in pacientes_pagina:
            tree.insert('', tk.END, values=row)
        pag_frame = tb.Frame(self.main_frame)
        pag_frame.pack(pady=10)
        def go_prev():
            if page > 1:
                self.show_lista_pacientes(page-1, page_size)
        def go_next():
            if end < total:
                self.show_lista_pacientes(page+1, page_size)
        tb.Button(pag_frame, text="Anterior", bootstyle=tb.SECONDARY, command=go_prev, state=tk.NORMAL if page > 1 else tk.DISABLED).pack(side=tk.LEFT, padx=5)
        ttk.Label(pag_frame, text=f"Página {page} de {((total-1)//page_size)+1}").pack(side=tk.LEFT, padx=10)
        tb.Button(pag_frame, text="Siguiente", bootstyle=tb.SECONDARY, command=go_next, state=tk.NORMAL if end < total else tk.DISABLED).pack(side=tk.LEFT, padx=5)
        tb.Button(self.main_frame, text="Volver", bootstyle=tb.SECONDARY, command=self.show_home).pack(pady=10)

    def get_selected_paciente(self, tree):
        selected = tree.selection()
        if selected:
            return tree.item(selected[0])['values']
        return None

    def abrir_modal_nuevo_paciente(self):
        self.abrir_modal_paciente("Nuevo Paciente")

    def abrir_modal_editar_paciente(self, paciente):
        if not paciente:
            messagebox.showwarning("Selecciona un paciente", "Por favor selecciona un paciente para editar.")
            return
        self.abrir_modal_paciente("Editar Paciente", paciente)

    def abrir_modal_paciente(self, titulo, paciente=None):
        modal = tk.Toplevel(self.root)
        modal.title(titulo)
        modal.geometry("500x600")
        modal.transient(self.root)
        modal.grab_set()
        fields = [
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("DNI:", "dni"),
            ("Edad:", "edad"),
            ("Género:", "genero"),
            ("Teléfono:", "telefono"),
            ("Email:", "email"),
            ("Dirección:", "direccion"),
            ("Obra Social:", "obra_social"),
            ("Número de Afiliado:", "numero_afiliado")
        ]
        entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(modal, text=label).grid(row=i, column=0, sticky=tk.W, pady=7, padx=10)
            if field == "genero":
                var = tk.StringVar()
                combo = ttk.Combobox(modal, textvariable=var, width=27)
                combo['values'] = ['Masculino', 'Femenino', 'Otro']
                combo.grid(row=i, column=1, pady=7)
                entries[field] = var
            else:
                entry = ttk.Entry(modal, width=30)
                entry.grid(row=i, column=1, pady=7)
                entries[field] = entry
        # Si es edición, rellenar datos
        if paciente:
            for idx, (_, field) in enumerate(fields):
                if field == "genero":
                    entries[field].set(paciente[5])
                else:
                    entries[field].insert(0, paciente[idx+1])
        def guardar():
            edad = entries['edad'].get()
            if not edad or not edad.isdigit() or int(edad) <= 0:
                messagebox.showwarning("Edad inválida", "Por favor ingrese una edad válida (solo números enteros positivos).")
                return
            datos = {
                'nombre': entries['nombre'].get(),
                'apellido': entries['apellido'].get(),
                'dni': entries['dni'].get(),
                'edad': int(edad),
                'genero': entries['genero'].get(),
                'telefono': entries['telefono'].get(),
                'email': entries['email'].get(),
                'direccion': entries['direccion'].get(),
                'obra_social': entries['obra_social'].get(),
                'numero_afiliado': entries['numero_afiliado'].get()
            }
            if not all([datos['nombre'], datos['apellido'], datos['dni']]):
                messagebox.showwarning("Campos obligatorios", "Nombre, Apellido y DNI son obligatorios.")
                return
            db.actualizar_paciente(paciente[0], datos)
            messagebox.showinfo("Éxito", "Paciente guardado correctamente.")
            modal.destroy()
            self.show_lista_pacientes()
        ttk.Button(modal, text="Guardar", command=guardar).grid(row=len(fields), column=0, pady=20, padx=10)
        ttk.Button(modal, text="Cancelar", command=modal.destroy).grid(row=len(fields), column=1, pady=20, padx=10)

    def eliminar_paciente(self, paciente):
        if not paciente:
            messagebox.showwarning("Selecciona un paciente", "Por favor selecciona un paciente para eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar a {paciente[1]} {paciente[2]}?"):
            db.eliminar_paciente(paciente[0])
            messagebox.showinfo("Éxito", "Paciente eliminado correctamente.")
            self.show_lista_pacientes()

    def abrir_modal_buscar_paciente(self):
        modal = tk.Toplevel(self.root)
        modal.title("Buscar Paciente")
        modal.geometry("400x200")
        modal.transient(self.root)
        modal.grab_set()
        ttk.Label(modal, text="Buscar por Nombre, Apellido o DNI:").pack(pady=10)
        search_var = tk.StringVar()
        entry = ttk.Entry(modal, textvariable=search_var, width=30)
        entry.pack(pady=10)
        def buscar():
            valor = search_var.get()
            if not valor:
                messagebox.showwarning("Campo vacío", "Ingrese un valor para buscar.")
                return
            self.show_lista_pacientes_filtrado(valor)
            modal.destroy()
        tb.Button(modal, text="Buscar", bootstyle=tb.INFO, command=buscar).pack(pady=10)
        tb.Button(modal, text="Cancelar", bootstyle=tb.SECONDARY, command=modal.destroy).pack()

    def show_lista_pacientes_filtrado(self, valor, page=1, page_size=50):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text=f"Resultados de búsqueda: '{valor}'", font=('Helvetica', 22, 'bold'), foreground=self.colors['primary']).pack(pady=(10, 0))
        actions_frame = tb.Frame(self.main_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        tb.Button(actions_frame, text="Volver a lista completa", bootstyle=tb.SECONDARY, command=self.show_lista_pacientes).pack(side=tk.LEFT, padx=5)
        columns = ("ID", "Nombre", "Apellido", "DNI", "Edad", "Género", "Teléfono", "Email", "Dirección", "Obra Social", "N° Afiliado")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), foreground=self.colors['primary'])
        style.configure("Treeview", font=("Helvetica", 10), rowheight=28)
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15, bootstyle=tb.INFO)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        pacientes = db.pacientes_filtrado(valor)
        total = len(pacientes)
        start = (page-1)*page_size
        end = start+page_size
        pacientes_pagina = pacientes[start:end]
        for i in tree.get_children():
            tree.delete(i)
        for row in pacientes_pagina:
            tree.insert('', tk.END, values=row)
        pag_frame = tb.Frame(self.main_frame)
        pag_frame.pack(pady=10)
        def go_prev():
            if page > 1:
                self.show_lista_pacientes_filtrado(valor, page-1, page_size)
        def go_next():
            if end < total:
                self.show_lista_pacientes_filtrado(valor, page+1, page_size)
        tb.Button(pag_frame, text="Anterior", bootstyle=tb.SECONDARY, command=go_prev, state=tk.NORMAL if page > 1 else tk.DISABLED).pack(side=tk.LEFT, padx=5)
        ttk.Label(pag_frame, text=f"Página {page} de {((total-1)//page_size)+1}").pack(side=tk.LEFT, padx=10)
        tb.Button(pag_frame, text="Siguiente", bootstyle=tb.SECONDARY, command=go_next, state=tk.NORMAL if end < total else tk.DISABLED).pack(side=tk.LEFT, padx=5)
        tb.Button(self.main_frame, text="Volver", bootstyle=tb.SECONDARY, command=self.show_home).pack(pady=10)

    def show_gestion_personal(self):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Gestión de Personal", font=('Helvetica', 22, 'bold'), foreground=self.colors['primary']).pack(pady=(10, 0))
        
        # Frame de acciones
        actions_frame = tb.Frame(self.main_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        
        tb.Button(actions_frame, text="➕ Agregar", bootstyle=tb.SUCCESS, command=self.abrir_modal_nuevo_personal).pack(side=tk.LEFT, padx=5)
        tb.Button(actions_frame, text="🔍 Buscar", bootstyle=tb.INFO, command=self.abrir_modal_buscar_personal).pack(side=tk.LEFT, padx=5)
        tb.Button(actions_frame, text="✏️ Editar", bootstyle=tb.WARNING, command=lambda: self.abrir_modal_editar_personal(self.get_selected_personal(tree))).pack(side=tk.LEFT, padx=5)
        tb.Button(actions_frame, text="🗑️ Eliminar", bootstyle=tb.DANGER, command=lambda: self.eliminar_personal(self.get_selected_personal(tree))).pack(side=tk.LEFT, padx=5)
        
        # Tabla de personal
        columns = ("ID", "Nombre", "Apellido", "Especialidad", "Matrícula", "Turno", "Estado")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), foreground=self.colors['primary'])
        style.configure("Treeview", font=("Helvetica", 10), rowheight=28)
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15, bootstyle=tb.INFO)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.cargar_personal_en_tabla(tree)
        
        tb.Button(self.main_frame, text="Volver", bootstyle=tb.SECONDARY, command=self.show_home).pack(pady=10)

    def cargar_personal_en_tabla(self, tree):
        for i in tree.get_children():
            tree.delete(i)
        personal = db.personal()
        for row in personal:
            tree.insert('', tk.END, values=row)

    def get_selected_personal(self, tree):
        selected = tree.selection()
        if selected:
            return tree.item(selected[0])['values']
        return None

    def abrir_modal_nuevo_personal(self):
        self.abrir_modal_personal("Nuevo Personal")

    def abrir_modal_editar_personal(self, personal):
        if not personal:
            messagebox.showwarning("Selecciona un personal", "Por favor selecciona un personal para editar.")
            return
        self.abrir_modal_personal("Editar Personal", personal)

    def abrir_modal_personal(self, titulo, personal=None):
        modal = tk.Toplevel(self.root)
        modal.title(titulo)
        modal.geometry("500x500")
        modal.transient(self.root)
        modal.grab_set()
        
        fields = [
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Especialidad:", "especialidad"),
            ("Matrícula:", "matricula"),
            ("Turno:", "turno"),
            ("Estado:", "estado")
        ]
        entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(modal, text=label).grid(row=i, column=0, sticky=tk.W, pady=7, padx=10)
            if field == "turno":
                var = tk.StringVar()
                combo = ttk.Combobox(modal, textvariable=var, width=27)
                combo['values'] = ['Mañana', 'Tarde', 'Noche']
                combo.grid(row=i, column=1, pady=7)
                entries[field] = var
            elif field == "estado":
                var = tk.StringVar()
                combo = ttk.Combobox(modal, textvariable=var, width=27)
                combo['values'] = ['Activo', 'Inactivo']
                combo.grid(row=i, column=1, pady=7)
                entries[field] = var
            else:
                entry = ttk.Entry(modal, width=30)
                entry.grid(row=i, column=1, pady=7)
                entries[field] = entry
        # Si es edición, rellenar datos
        if personal:
            for idx, (_, field) in enumerate(fields):
                if field in ["turno", "estado"]:
                    entries[field].set(personal[idx+1])
                else:
                    entries[field].insert(0, personal[idx+1])
        def guardar():
            datos = {
                'nombre': entries['nombre'].get(),
                'apellido': entries['apellido'].get(),
                'especialidad': entries['especialidad'].get(),
                'matricula': entries['matricula'].get(),
                'turno': entries['turno'].get(),
                'estado': entries['estado'].get()
            }
            if not all([datos['nombre'], datos['apellido'], datos['matricula']] ):
                messagebox.showwarning("Campos obligatorios", "Nombre, Apellido y Matrícula son obligatorios.")
                return
            db.actualizar_personal(personal[0], datos)
            messagebox.showinfo("Éxito", "Personal guardado correctamente.")
            modal.destroy()
            self.show_gestion_personal()
        tb.Button(modal, text="Guardar", bootstyle=tb.SUCCESS, command=guardar).grid(row=len(fields), column=0, pady=20, padx=10)
        tb.Button(modal, text="Cancelar", bootstyle=tb.SECONDARY, command=modal.destroy).grid(row=len(fields), column=1, pady=20, padx=10)

    def eliminar_personal(self, personal):
        if not personal:
            messagebox.showwarning("Selecciona un personal", "Por favor selecciona un personal para eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar a {personal[1]} {personal[2]}?"):
            db.eliminar_personal(personal[0])
            messagebox.showinfo("Éxito", "Personal eliminado correctamente.")
            self.show_gestion_personal()

    def abrir_modal_buscar_personal(self):
        modal = tk.Toplevel(self.root)
        modal.title("Buscar Personal")
        modal.geometry("400x200")
        modal.transient(self.root)
        modal.grab_set()
        ttk.Label(modal, text="Buscar por Nombre, Apellido o Matrícula:").pack(pady=10)
        search_var = tk.StringVar()
        entry = ttk.Entry(modal, textvariable=search_var, width=30)
        entry.pack(pady=10)
        def buscar():
            valor = search_var.get()
            if not valor:
                messagebox.showwarning("Campo vacío", "Ingrese un valor para buscar.")
                return
            self.show_gestion_personal_filtrado(valor)
            modal.destroy()
        tb.Button(modal, text="Buscar", bootstyle=tb.INFO, command=buscar).pack(pady=10)
        tb.Button(modal, text="Cancelar", bootstyle=tb.SECONDARY, command=modal.destroy).pack()

    def show_gestion_personal_filtrado(self, valor):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text=f"Resultados de búsqueda: '{valor}'", font=('Helvetica', 22, 'bold'), foreground=self.colors['primary']).pack(pady=(10, 0))
        actions_frame = tb.Frame(self.main_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        tb.Button(actions_frame, text="Volver a lista completa", bootstyle=tb.SECONDARY, command=self.show_gestion_personal).pack(side=tk.LEFT, padx=5)
        columns = ("ID", "Nombre", "Apellido", "Especialidad", "Matrícula", "Turno", "Estado")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), foreground=self.colors['primary'])
        style.configure("Treeview", font=("Helvetica", 10), rowheight=28)
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15, bootstyle=tb.INFO)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        personal = db.personal_filtrado(valor)
        for row in personal:
            tree.insert('', tk.END, values=row)
        tb.Button(self.main_frame, text="Volver", bootstyle=tb.SECONDARY, command=self.show_home).pack(pady=10)

    def show_turnos(self):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Turnos del Personal", font=('Helvetica', 20, 'bold'), foreground=self.colors['primary']).pack(pady=10)
        
        columns = ("ID", "Nombre", "Apellido", "Turno", "Estado")
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill=tk.BOTH, expand=True)
        
        personal = db.personal()
        for row in personal:
            tree.insert('', tk.END, values=row)
        
        tb.Button(self.main_frame, text="Volver", command=self.show_home).pack(pady=10)

    def show_inventario(self):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Inventario de Recursos", font=('Helvetica', 22, 'bold'), foreground=self.colors['primary']).pack(pady=(10, 0))
        
        # Frame de acciones
        actions_frame = tb.Frame(self.main_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        
        tb.Button(actions_frame, text="➕ Agregar", bootstyle=tb.SUCCESS, command=self.abrir_modal_nuevo_recurso).pack(side=tk.LEFT, padx=5)
        tb.Button(actions_frame, text="🔍 Buscar", bootstyle=tb.INFO, command=self.abrir_modal_buscar_recurso).pack(side=tk.LEFT, padx=5)
        tb.Button(actions_frame, text="✏️ Editar", bootstyle=tb.WARNING, command=lambda: self.abrir_modal_editar_recurso(self.get_selected_recurso(tree))).pack(side=tk.LEFT, padx=5)
        tb.Button(actions_frame, text="🗑️ Eliminar", bootstyle=tb.DANGER, command=lambda: self.eliminar_recurso(self.get_selected_recurso(tree))).pack(side=tk.LEFT, padx=5)
        
        # Tabla de recursos
        columns = ("ID", "Tipo", "Nombre", "Cantidad", "Estado")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), foreground=self.colors['primary'])
        style.configure("Treeview", font=("Helvetica", 10), rowheight=28)
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15, bootstyle=tb.INFO)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.cargar_recursos_en_tabla(tree)
        
        tb.Button(self.main_frame, text="Volver", bootstyle=tb.SECONDARY, command=self.show_home).pack(pady=10)

    def cargar_recursos_en_tabla(self, tree):
        for i in tree.get_children():
            tree.delete(i)
        recursos = db.recursos()
        for row in recursos:
            tags = ()
            if row[3] is not None and row[3] <= 5:
                tags = ('critico',)
            tree.insert('', tk.END, values=row, tags=tags)
        tree.tag_configure('critico', background='#ffcccc')

    def get_selected_recurso(self, tree):
        selected = tree.selection()
        if selected:
            return tree.item(selected[0])['values']
        return None

    def abrir_modal_nuevo_recurso(self):
        self.abrir_modal_recurso("Nuevo Recurso")

    def abrir_modal_editar_recurso(self, recurso):
        if not recurso:
            messagebox.showwarning("Selecciona un recurso", "Por favor selecciona un recurso para editar.")
            return
        self.abrir_modal_recurso("Editar Recurso", recurso)

    def abrir_modal_recurso(self, titulo, recurso=None):
        modal = tk.Toplevel(self.root)
        modal.title(titulo)
        modal.geometry("400x400")
        modal.transient(self.root)
        modal.grab_set()
        
        fields = [
            ("Tipo:", "tipo"),
            ("Nombre:", "nombre"),
            ("Cantidad:", "cantidad"),
            ("Estado:", "estado")
        ]
        entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(modal, text=label).grid(row=i, column=0, sticky=tk.W, pady=7, padx=10)
            if field == "estado":
                var = tk.StringVar()
                combo = ttk.Combobox(modal, textvariable=var, width=27)
                combo['values'] = ['Disponible', 'En uso', 'En reparación', 'Bajo stock']
                combo.grid(row=i, column=1, pady=7)
                entries[field] = var
            else:
                entry = ttk.Entry(modal, width=30)
                entry.grid(row=i, column=1, pady=7)
                entries[field] = entry
        # Si es edición, rellenar datos
        if recurso:
            for idx, (_, field) in enumerate(fields):
                if field == "estado":
                    entries[field].set(recurso[idx+1])
                else:
                    entries[field].insert(0, recurso[idx+1])
        def guardar():
            datos = {
                'tipo': entries['tipo'].get(),
                'nombre': entries['nombre'].get(),
                'cantidad': entries['cantidad'].get(),
                'estado': entries['estado'].get()
            }
            if not all([datos['tipo'], datos['nombre'], datos['cantidad']] ):
                messagebox.showwarning("Campos obligatorios", "Tipo, Nombre y Cantidad son obligatorios.")
                return
            try:
                cantidad_int = int(datos['cantidad'])
            except ValueError:
                messagebox.showwarning("Cantidad inválida", "La cantidad debe ser un número entero.")
                return
            db.actualizar_recurso(recurso[0], datos)
            messagebox.showinfo("Éxito", "Recurso guardado correctamente.")
            modal.destroy()
            self.show_inventario()
        tb.Button(modal, text="Guardar", bootstyle=tb.SUCCESS, command=guardar).grid(row=len(fields), column=0, pady=20, padx=10)
        tb.Button(modal, text="Cancelar", bootstyle=tb.SECONDARY, command=modal.destroy).grid(row=len(fields), column=1, pady=20, padx=10)

    def eliminar_recurso(self, recurso):
        if not recurso:
            messagebox.showwarning("Selecciona un recurso", "Por favor selecciona un recurso para eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar el recurso '{recurso[2]}'?"):
            db.eliminar_recurso(recurso[0])
            messagebox.showinfo("Éxito", "Recurso eliminado correctamente.")
            self.show_inventario()

    def abrir_modal_buscar_recurso(self):
        modal = tk.Toplevel(self.root)
        modal.title("Buscar Recurso")
        modal.geometry("400x200")
        modal.transient(self.root)
        modal.grab_set()
        ttk.Label(modal, text="Buscar por Tipo o Nombre:").pack(pady=10)
        search_var = tk.StringVar()
        entry = ttk.Entry(modal, textvariable=search_var, width=30)
        entry.pack(pady=10)
        def buscar():
            valor = search_var.get()
            if not valor:
                messagebox.showwarning("Campo vacío", "Ingrese un valor para buscar.")
                return
            self.show_inventario_filtrado(valor)
            modal.destroy()
        tb.Button(modal, text="Buscar", bootstyle=tb.INFO, command=buscar).pack(pady=10)
        tb.Button(modal, text="Cancelar", bootstyle=tb.SECONDARY, command=modal.destroy).pack()

    def show_inventario_filtrado(self, valor):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text=f"Resultados de búsqueda: '{valor}'", font=('Helvetica', 22, 'bold'), foreground=self.colors['primary']).pack(pady=(10, 0))
        actions_frame = tb.Frame(self.main_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        tb.Button(actions_frame, text="Volver a lista completa", bootstyle=tb.SECONDARY, command=self.show_inventario).pack(side=tk.LEFT, padx=5)
        columns = ("ID", "Tipo", "Nombre", "Cantidad", "Estado")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), foreground=self.colors['primary'])
        style.configure("Treeview", font=("Helvetica", 10), rowheight=28)
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15, bootstyle=tb.INFO)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        recursos = db.recursos_filtrado(valor)
        for row in recursos:
            tags = ()
            if row[3] is not None and row[3] <= 5:
                tags = ('critico',)
            tree.insert('', tk.END, values=row, tags=tags)
        tree.tag_configure('critico', background='#ffcccc')
        tb.Button(self.main_frame, text="Volver", bootstyle=tb.SECONDARY, command=self.show_home).pack(pady=10)

    def show_alertas(self):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Alertas de Recursos", font=('Helvetica', 22, 'bold'), foreground=self.colors['accent']).pack(pady=(10, 0))
        columns = ("ID", "Tipo", "Nombre", "Cantidad", "Estado")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), foreground=self.colors['accent'])
        style.configure("Treeview", font=("Helvetica", 10), rowheight=28)
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15, bootstyle=tb.DANGER)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        recursos = db.recursos_criticos_lista()
        for row in recursos:
            tree.insert('', tk.END, values=row)
        tb.Button(self.main_frame, text="Volver", bootstyle=tb.SECONDARY, command=self.show_home).pack(pady=10)

    def show_lista_consultas(self, page=1, page_size=50):
        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Lista de Consultas", font=('Helvetica', 22, 'bold'), foreground=self.colors['primary']).pack(pady=(10, 0))
        columns = ("ID", "Paciente", "Fecha", "Motivo", "Prioridad", "Médico", "Estado")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), foreground=self.colors['primary'])
        style.configure("Treeview", font=("Helvetica", 10), rowheight=28)
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        consultas = db.consultas()
        total = len(consultas)
        start = (page-1)*page_size
        end = start+page_size
        consultas_pagina = consultas[start:end]
        for row in consultas_pagina:
            tree.insert('', tk.END, values=row)

        # --- Botón para marcar como atendido ---
        def cambiar_estado(nuevo_estado):
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selecciona una consulta", "Por favor selecciona una consulta.")
                return
            consulta = tree.item(selected[0])['values']
            db.actualizar_estado_consulta(consulta[0], nuevo_estado)
            messagebox.showinfo("Éxito", f"Consulta marcada como {nuevo_estado}.")
            self.show_lista_consultas(page, page_size)

        def eliminar_consulta():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selecciona una consulta", "Por favor selecciona una consulta para eliminar.")
                return
            consulta = tree.item(selected[0])['values']
            if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar la consulta de {consulta[1]}?"):
                db.eliminar_consulta(consulta[0])
                messagebox.showinfo("Eliminado", "Consulta eliminada correctamente.")
                self.show_lista_consultas(page, page_size)

        btn_frame = tb.Frame(self.main_frame)
        btn_frame.pack(pady=5)
        tb.Button(btn_frame, text="Marcar como Atendido", bootstyle=tb.INFO, command=lambda: cambiar_estado("Atendido")).pack(side=tk.LEFT, padx=5)
        tb.Button(btn_frame, text="En Espera", bootstyle=tb.INFO, command=lambda: cambiar_estado("En espera")).pack(side=tk.LEFT, padx=5)
        tb.Button(btn_frame, text="Cancelada", bootstyle=tb.WARNING, command=lambda: cambiar_estado("Cancelada")).pack(side=tk.LEFT, padx=5)
        tb.Button(btn_frame, text="Eliminar", bootstyle=tb.DANGER, command=eliminar_consulta).pack(side=tk.LEFT, padx=5)

        # Paginación y volver (igual que antes)
        pag_frame = tb.Frame(self.main_frame)
        pag_frame.pack(pady=10)
        def go_prev():
            if page > 1:
                self.show_lista_consultas(page-1, page_size)
        def go_next():
            if end < total:
                self.show_lista_consultas(page+1, page_size)
        tb.Button(pag_frame, text="Anterior", bootstyle=tb.SECONDARY, command=go_prev, state=tk.NORMAL if page > 1 else tk.DISABLED).pack(side=tk.LEFT, padx=5)
        ttk.Label(pag_frame, text=f"Página {page} de {((total-1)//page_size)+1}").pack(side=tk.LEFT, padx=10)
        tb.Button(pag_frame, text="Siguiente", bootstyle=tb.SECONDARY, command=go_next, state=tk.NORMAL if end < total else tk.DISABLED).pack(side=tk.LEFT, padx=5)
        tb.Button(self.main_frame, text="Volver", bootstyle=tb.SECONDARY, command=self.show_home).pack(pady=10)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def grafico_consultas_por_prioridad(self, ax):
        """Dibuja un gráfico de barras de consultas por prioridad en el eje ax."""
        prioridades = db.obtener_estadisticas_prioridad()
        prioridades_labels = [p[0] for p in prioridades]
        cantidades = [p[1] for p in prioridades]
        ax.clear()
        ax.bar(prioridades_labels, cantidades, color='#3498db')
        ax.set_title('Consultas por Prioridad')
        ax.set_ylabel('Cantidad')

    def grafico_recursos_por_estado(self, ax):
        """Dibuja un gráfico de torta de recursos por estado en el eje ax."""
        recursos_estado = db.obtener_estadisticas_recursos_estado()
        labels = [r[0] for r in recursos_estado]
        sizes = [r[1] for r in recursos_estado]
        colors = ['#2ecc71','#e67e22','#e74c3c','#95a5a6']
        ax.clear()
        if sizes:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(sizes)])
        ax.set_title('Recursos por Estado')

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Login - Sistema de Guardia Hospitalaria")
        self.root.geometry("400x350")
        self.style = tb.Style(theme="cosmo")
        
        # Frame principal centrado
        self.frame = tb.Frame(self.root, padding=30)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título
        tb.Label(self.frame, text="Iniciar Sesión", font=('Helvetica', 18, 'bold'), bootstyle="primary").pack(pady=(0, 20))
        
        # Usuario
        tb.Label(self.frame, text="Usuario:", bootstyle="secondary").pack(fill=tk.X, pady=(0, 5))
        self.user_entry = tb.Entry(self.frame, width=30)
        self.user_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Contraseña
        tb.Label(self.frame, text="Contraseña:", bootstyle="secondary").pack(fill=tk.X, pady=(0, 5))
        self.pass_entry = tb.Entry(self.frame, width=30, show='*')
        self.pass_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Botones
        tb.Button(self.frame, text="Ingresar", bootstyle="success", command=self.login, width=20).pack(pady=5)
        tb.Button(self.frame, text="Registrarse", bootstyle="outline-primary", command=self.registro, width=20).pack(pady=5)

    def login(self):
        usuario = self.user_entry.get()
        password = self.pass_entry.get()
        if db.verificar_usuario(usuario, password):
            self.frame.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def registro(self):
        usuario = self.user_entry.get()
        password = self.pass_entry.get()
        if not usuario or not password:
            messagebox.showwarning("Campos vacíos", "Ingrese usuario y contraseña")
            return
        if db.registrar_usuario(usuario, password):
            messagebox.showinfo("Éxito", "Usuario registrado. Ahora puede iniciar sesión.")
        else:
            messagebox.showerror("Error", "El usuario ya existe")

if __name__ == "__main__":
    import db
    db.init_db()  # Inicializa la base de datos y todas las tablas antes de cualquier operación
    root = tk.Tk()
    def start_app():
        app = HospitalGuardApp(root)
    LoginWindow(root, start_app)
    root.mainloop()
