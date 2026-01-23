import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Callable, List


class WindowSwitcherGUI:
    """Interfaz gráfica para controlar el cambio automático de ventanas."""

    def __init__(self, title: str, width: int, height: int, always_on_top: bool = True):
        # Crear ventana principal
        self.root = ttk.Window(themename="flatly")
        self.root.title(title)
        
        # Dimensiones
        self.expanded_width = width
        self.expanded_height = height
        self.compact_width = 200
        self.compact_height = 100
        
        self.is_compact = False
        self.root.geometry(f"{self.expanded_width}x{self.expanded_height}")
        self.root.resizable(True, True)
        self.root.minsize(180, 100)
        
        if always_on_top:
            self.root.attributes("-topmost", True)

        # Callbacks
        self._on_start: Callable[[], None] = lambda: None
        self._on_stop: Callable[[], None] = lambda: None
        self._on_add_target: Callable[[str], None] = lambda x: None
        self._on_remove_target: Callable[[str], None] = lambda x: None
        self._on_refresh_windows: Callable[[], List[str]] = lambda: []
        
        self._is_running = False

        self._build_ui()
        self._update_status_display()

    def _build_ui(self) -> None:
        """Construye la interfaz gráfica."""
        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill=BOTH, expand=YES)
        self.main_frame.columnconfigure(0, weight=1)
        
        # Sección de Control
        self.control_frame = ttk.Labelframe(self.main_frame, text="Control", padding=10)
        self.control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.control_frame.columnconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=1)
        self.control_frame.columnconfigure(2, weight=0)
        
        self.run_btn = ttk.Button(
            self.control_frame,
            text="▶ RUN",
            bootstyle="success",
            command=self._handle_start
        )
        self.run_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.stop_btn = ttk.Button(
            self.control_frame,
            text="⬛ STOP",
            bootstyle="danger",
            command=self._handle_stop
        )
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        self.status_indicator = ttk.Label(
            self.control_frame,
            text="⬛",
            font=("Segoe UI", 20),
            bootstyle="danger",
            width=3
        )
        self.status_indicator.grid(row=0, column=2, sticky="ns")

        # Sección de Selección de Ventanas
        self.selection_frame = ttk.Labelframe(self.main_frame, text="Seleccionar Ventana", padding=10)
        self.selection_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.selection_frame.columnconfigure(0, weight=1)
        
        combo_frame = ttk.Frame(self.selection_frame)
        combo_frame.grid(row=0, column=0, sticky="ew")
        combo_frame.columnconfigure(0, weight=1)
        
        self.window_combo = ttk.Combobox(combo_frame, state="readonly", bootstyle="primary")
        self.window_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.add_btn = ttk.Button(
            combo_frame,
            text="➕ Añadir",
            bootstyle="success-outline",
            command=self._handle_add_target,
            width=10
        )
        self.add_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.refresh_btn = ttk.Button(
            combo_frame,
            text="🔄",
            bootstyle="info-outline",
            command=self._handle_refresh_windows,
            width=4
        )
        self.refresh_btn.grid(row=0, column=2)

        # Sección de Targets
        self.targets_frame = ttk.Labelframe(self.main_frame, text="Ventanas Objetivo", padding=10)
        self.targets_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 0))
        self.targets_frame.columnconfigure(0, weight=1)
        self.targets_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        listbox_frame = ttk.Frame(self.targets_frame)
        listbox_frame.grid(row=0, column=0, sticky="nsew")
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=VERTICAL)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.targets_listbox = ttk.Treeview(
            listbox_frame,
            columns=("target",),
            show="tree",
            height=6,
            yscrollcommand=scrollbar.set
        )
        self.targets_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.targets_listbox.yview)
        
        self.remove_btn = ttk.Button(
            self.targets_frame,
            text="🗑️ Eliminar Seleccionado",
            bootstyle="danger-outline",
            command=self._handle_remove_target
        )
        self.remove_btn.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        # Auto-cargar ventanas disponibles
        self.root.after(100, self._handle_refresh_windows)

    def _toggle_compact_mode(self, compact: bool) -> None:
        """Alterna entre modo compacto y expandido."""
        if compact == self.is_compact:
            return
            
        self.is_compact = compact
        
        if compact:
            self.selection_frame.grid_remove()
            self.targets_frame.grid_remove()
            self.root.geometry(f"{self.compact_width}x{self.compact_height}")
        else:
            self.selection_frame.grid()
            self.targets_frame.grid()
            self.root.geometry(f"{self.expanded_width}x{self.expanded_height}")

    def set_start_callback(self, callback: Callable[[], None]) -> None:
        """Establece callback para el botón RUN."""
        self._on_start = callback

    def set_stop_callback(self, callback: Callable[[], None]) -> None:
        """Establece callback para el botón STOP."""
        self._on_stop = callback

    def set_add_target_callback(self, callback: Callable[[str], None]) -> None:
        """Establece callback para añadir un target."""
        self._on_add_target = callback

    def set_remove_target_callback(self, callback: Callable[[str], None]) -> None:
        """Establece callback para eliminar un target."""
        self._on_remove_target = callback

    def set_refresh_windows_callback(self, callback: Callable[[], List[str]]) -> None:
        """Establece callback para refrescar la lista de ventanas."""
        self._on_refresh_windows = callback

    def update_status(self, is_running: bool) -> None:
        """Actualiza el estado visual y cambia a modo compacto si está corriendo."""
        self._is_running = is_running
        self._update_status_display()
        self._toggle_compact_mode(is_running)

    def update_targets_list(self, targets: List[str]) -> None:
        """Actualiza la lista visual de targets."""
        for item in self.targets_listbox.get_children():
            self.targets_listbox.delete(item)
        
        for target in targets:
            self.targets_listbox.insert("", "end", text=target, values=(target,))

    def _update_status_display(self) -> None:
        """Actualiza el indicador de estado."""
        if self._is_running:
            self.status_indicator.config(text="▶", bootstyle="success")
        else:
            self.status_indicator.config(text="⬛", bootstyle="danger")

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
        """Programa una tarea para ejecutarse después de un delay."""
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
