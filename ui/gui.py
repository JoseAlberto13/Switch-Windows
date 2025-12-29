import tkinter as tk
from typing import Callable


class WindowSwitcherGUI:
    """
    Interfaz gráfica para controlar el cambio automático de ventanas.
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
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.attributes("-topmost", always_on_top)

        self._on_start: Callable[[], None] = lambda: None
        self._on_stop: Callable[[], None] = lambda: None

        self._build_ui()

    def _build_ui(self) -> None:
        """Construye los elementos de la interfaz."""
        # Frame principal
        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        # Botones de control
        self.run_btn = tk.Button(
            frame,
            text="RUN",
            width=8,
            command=self._handle_start
        )
        self.run_btn.grid(row=0, column=0, padx=5, pady=5)

        self.stop_btn = tk.Button(
            frame,
            text="STOP",
            width=8,
            command=self._handle_stop
        )
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)

        # Label de estado
        self.status_label = tk.Label(self.root, text="Estado: STOPPED")
        self.status_label.pack(pady=5)

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
        status_text = "RUNNING" if is_running else "STOPPED"
        self.status_label.config(text=f"Estado: {status_text}")

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
