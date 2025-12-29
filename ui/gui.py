import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Callable


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
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(True, True)  # Permitir redimensionar
        
        # Establecer tamaño mínimo para que no se haga demasiado pequeña
        self.root.minsize(180, 100)
        
        if always_on_top:
            self.root.attributes("-topmost", True)

        self._on_start: Callable[[], None] = lambda: None
        self._on_stop: Callable[[], None] = lambda: None
        
        # Estado inicial
        self._is_running = False

        self._build_ui()
        self._update_status_display()

    def _build_ui(self) -> None:
        """Construye los elementos de la interfaz con diseño responsivo y vertical."""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Configurar grid para que sea responsivo
        main_frame.columnconfigure(0, weight=1)  # Columna de botones
        main_frame.columnconfigure(1, weight=0)  # Columna del indicador
        main_frame.rowconfigure(0, weight=1)     # Fila del botón RUN
        main_frame.rowconfigure(1, weight=1)     # Fila del botón STOP

        # Frame izquierdo para botones (vertical)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8))
        
        # Configurar grid del frame de botones
        button_frame.rowconfigure(0, weight=1)
        button_frame.rowconfigure(1, weight=1)
        button_frame.columnconfigure(0, weight=1)

        # Botón RUN (arriba, verde)
        self.run_btn = ttk.Button(
            button_frame,
            text="▶ RUN",
            bootstyle="success",
            command=self._handle_start
        )
        self.run_btn.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

        # Botón STOP (abajo, rojo)
        self.stop_btn = ttk.Button(
            button_frame,
            text="⬛ STOP",
            bootstyle="danger",
            command=self._handle_stop
        )
        self.stop_btn.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

        # Indicador circular de estado (derecha)
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=0, column=1, rowspan=2, sticky="ns")
        
        # Label circular con el icono de estado
        self.status_indicator = ttk.Label(
            status_frame,
            text="⬛",
            font=("Segoe UI", 24),
            bootstyle="danger",
            anchor=CENTER,
            width=3
        )
        self.status_indicator.pack(expand=YES, fill=BOTH)

    def set_start_callback(self, callback: Callable[[], None]) -> None:
        """
        Establece el callback para cuando se presiona el botón RUN.
        
        Args:
            callback: Función a ejecutar cuando se inicia
        """
        self._on_start = callback

    def set_stop_callback(self, callback: Callable[[], None]) -> None:
        """
        Establece el callback para cuando se presiona el botón STOP.
        
        Args:
            callback: Función a ejecutar cuando se detiene
        """
        self._on_stop = callback

    def update_status(self, is_running: bool) -> None:
        """
        Actualiza el estado visual de la interfaz.
        
        Args:
            is_running: True si está corriendo, False si está detenido
        """
        self._is_running = is_running
        self._update_status_display()

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
