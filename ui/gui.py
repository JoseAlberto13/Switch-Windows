import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Callable, List


class WindowSwitcherGUI:
    """
    Interfaz gráfica moderna para controlar el cambio automático de ventanas.
    Implementa el patrón MVC donde esta clase es la Vista.
    """

    def __init__(
        self,
        title: str,
        width: int,
        height: int,
        always_on_top: bool = True
    ):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            title: Título de la ventana
            width: Ancho de la ventana
            height: Alto de la ventana
            always_on_top: Si la ventana debe estar siempre visible
        """
        # Crear ventana principal con tema moderno
        self.root = ttk.Window(themename="flatly")
        self.root.title(title)
        
        # Guardar dimensiones
        self.expanded_width = width
        self.expanded_height = height
        self.compact_width = 200
        self.compact_height = 100
        
        # Iniciar en modo expandido
        self.is_compact = False
        self.root.geometry(f"{self.expanded_width}x{self.expanded_height}")
        self.root.resizable(True, True)
        
        # Establecer tamaño mínimo
        self.root.minsize(180, 100)
        
        if always_on_top:
            self.root.attributes("-topmost", True)

        # Callbacks
        self._on_start: Callable[[], None] = lambda: None
        self._on_stop: Callable[[], None] = lambda: None
        self._on_add_target: Callable[[str], None] = lambda x: None
        self._on_remove_target: Callable[[str], None] = lambda x: None
        self._on_refresh_windows: Callable[[], List[str]] = lambda: []
        
        # Estado inicial
        self._is_running = False

        self._build_ui()
        self._update_status_display()

    def _build_ui(self) -> None:
        """Construye los elementos de la interfaz con diseño responsivo."""
        # Frame principal con padding
        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # Configurar grid
        self.main_frame.columnconfigure(0, weight=1)
        
        # ===== SECCIÓN DE CONTROL (SIEMPRE VISIBLE) =====
        self.control_frame = ttk.Labelframe(self.main_frame, text="Control", padding=10)
        self.control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.control_frame.columnconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=1)
        self.control_frame.columnconfigure(2, weight=0)
        
        # Botón RUN
        self.run_btn = ttk.Button(
            self.control_frame,
            text="▶ RUN",
            bootstyle="success",
            command=self._handle_start
        )
        self.run_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Botón STOP
        self.stop_btn = ttk.Button(
            self.control_frame,
            text="⬛ STOP",
            bootstyle="danger",
            command=self._handle_stop
        )
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        # Indicador de estado
        self.status_indicator = ttk.Label(
            self.control_frame,
            text="⬛",
            font=("Segoe UI", 20),
            bootstyle="danger",
            width=3
        )
        # self.status_indicator.grid(row=0, column=2, sticky="ns")

        # ===== SECCIÓN DE SELECCIÓN DE VENTANAS (COLAPSABLE) =====
        self.selection_frame = ttk.Labelframe(self.main_frame, text="Seleccionar Ventana", padding=10)
        self.selection_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.selection_frame.columnconfigure(0, weight=1)
        
        # Frame para combobox y botones
        combo_frame = ttk.Frame(self.selection_frame)
        combo_frame.grid(row=0, column=0, sticky="ew")
        combo_frame.columnconfigure(0, weight=1)
        
        # Combobox para ventanas disponibles
        self.window_combo = ttk.Combobox(
            combo_frame,
            state="readonly",
            bootstyle="primary"
        )
        self.window_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Botón Añadir
        self.add_btn = ttk.Button(
            combo_frame,
            text="➕ Añadir",
            bootstyle="success-outline",
            command=self._handle_add_target,
            width= 10
        )
        self.add_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Botón Refrescar
        self.refresh_btn = ttk.Button(
            combo_frame,
            text="🔄 Actualizar",
            bootstyle="info-outline",
            command=self._handle_refresh_windows,
            width= 12
        )
        self.refresh_btn.grid(row=0, column=2)

        # ===== SECCIÓN DE TARGETS (COLAPSABLE) =====
        self.targets_frame = ttk.Labelframe(self.main_frame, text="Ventanas Objetivo", padding=10)
        self.targets_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 0))
        self.targets_frame.columnconfigure(0, weight=1)
        self.targets_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Listbox con scrollbar
        listbox_frame = ttk.Frame(self.targets_frame)
        listbox_frame.grid(row=0, column=0, sticky="nsew")
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame, orient=VERTICAL)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Listbox
        self.targets_listbox = ttk.Treeview(
            listbox_frame,
            columns=("target",),
            show="tree",
            height=6,
            yscrollcommand=scrollbar.set
        )
        self.targets_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.targets_listbox.yview)
        
        # Botón Eliminar
        self.remove_btn = ttk.Button(
            self.targets_frame,
            text="🗑️ Eliminar Seleccionado",
            bootstyle="danger-outline",
            command=self._handle_remove_target
        )
        self.remove_btn.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        # Cargar ventanas disponibles al inicio
        self.root.after(100, self._handle_refresh_windows)

    def _toggle_compact_mode(self, compact: bool) -> None:
        """
        Alterna entre modo compacto y expandido.
        
        Args:
            compact: True para modo compacto, False para expandido
        """
        if compact == self.is_compact:
            return
            
        self.is_compact = compact
        
        if compact:
            # Ocultar frames de selección y targets
            self.selection_frame.grid_remove()
            self.targets_frame.grid_remove()
            
            # Cambiar a tamaño compacto
            self.root.geometry(f"{self.compact_width}x{self.compact_height}")
        else:
            # Mostrar frames de selección y targets
            self.selection_frame.grid()
            self.targets_frame.grid()
            
            # Cambiar a tamaño expandido
            self.root.geometry(f"{self.expanded_width}x{self.expanded_height}")

    def set_start_callback(self, callback: Callable[[], None]) -> None:
        """
        Establece el callback para cuando se presiona el botón RUN.
        """
        self._on_start = callback

    def set_stop_callback(self, callback: Callable[[], None]) -> None:
        """
        Establece el callback para cuando se presiona el botón STOP.
        """
        self._on_stop = callback

    def set_add_target_callback(self, callback: Callable[[str], None]) -> None:
        """
        Establece el callback para añadir una ventana al target.
        """
        self._on_add_target = callback

    def set_remove_target_callback(self, callback: Callable[[str], None]) -> None:
        """
        Establece el callback para eliminar un target.
        """
        self._on_remove_target = callback

    def set_refresh_windows_callback(self, callback: Callable[[], List[str]]) -> None:
        """
        Establece el callback para refrescar la lista de ventanas disponibles.
        """
        self._on_refresh_windows = callback

    def update_status(self, is_running: bool) -> None:
        """
        Actualiza el estado visual de la interfaz.
        
        Args:
            is_running: True si está corriendo, False si está detenido
        """
        self._is_running = is_running
        self._update_status_display()
        
        # Cambiar a modo compacto cuando está corriendo
        self._toggle_compact_mode(is_running)

    def update_targets_list(self, targets: List[str]) -> None:
        """
        Actualiza la lista visual de targets.
        
        Args:
            targets: Lista de títulos de ventanas objetivo
        """
        # Limpiar listbox
        for item in self.targets_listbox.get_children():
            self.targets_listbox.delete(item)
        
        # Añadir targets
        for target in targets:
            self.targets_listbox.insert("", "end", text=target, values=(target,))

    def _update_status_display(self) -> None:
        """Actualiza la visualización del estado con colores dinámicos."""
        if self._is_running:
            self.status_indicator.config(
                text="▶",
                bootstyle="success"
            )
        else:
            self.status_indicator.config(
                text="⬛",
                bootstyle="danger"
            )

    def _handle_add_target(self) -> None:
        """Maneja el evento de añadir un target."""
        selected = self.window_combo.get()
        if selected:
            self._on_add_target(selected)

    def _handle_remove_target(self) -> None:
        """Maneja el evento de eliminar un target."""
        selection = self.targets_listbox.selection()
        if selection:
            item = selection[0]
            target = self.targets_listbox.item(item, "text")
            self._on_remove_target(target)

    def _handle_refresh_windows(self) -> None:
        """Maneja el evento de refrescar la lista de ventanas."""
        windows = self._on_refresh_windows()
        self.window_combo['values'] = windows
        if windows:
            self.window_combo.current(0)

    def focus(self) -> None:
        """Trae el foco a la ventana de la aplicación."""
        self.root.focus_force()

    def schedule_task(self, delay_ms: int, task: Callable[[], None]) -> None:
        """
        Programa una tarea para ejecutarse después de un delay.
        
        Args:
            delay_ms: Delay en milisegundos
            task: Función a ejecutar
        """
        self.root.after(delay_ms, task)

    def run(self) -> None:
        """Inicia el loop principal de la interfaz."""
        self.root.mainloop()

    def _handle_start(self) -> None:
        """Maneja el evento de inicio."""
        self.focus()
        self._on_start()

    def _handle_stop(self) -> None:
        """Maneja el evento de detención."""
        self._on_stop()
