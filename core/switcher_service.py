from typing import List, Callable, Optional
from controllers.base_controller import BaseWindowController


class WindowSwitcherService:
    """
    Servicio que gestiona el cambio automático entre ventanas.
    """

    def __init__(self, controller: BaseWindowController, targets: List[str], interval_ms: int):
        """
        Inicializa el servicio de cambio de ventanas.
        
        Args:
            controller: Controlador de ventanas específico del OS
            targets: Lista de títulos de ventanas objetivo
            interval_ms: Intervalo en milisegundos entre cambios
        """
        self.controller = controller
        self.targets = targets
        self.interval_ms = interval_ms
        self._running = False
        self._current_index = 0
        self._on_status_change: Optional[Callable[[bool], None]] = None

    def set_status_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Establece un callback para notificar cambios de estado.
        
        Args:
            callback: Función que recibe True cuando está corriendo, False cuando está detenido
        """
        self._on_status_change = callback

    def start(self) -> None:
        """Inicia el servicio de cambio de ventanas."""
        self._running = True
        self._notify_status_change()

    def stop(self) -> None:
        """Detiene el servicio de cambio de ventanas."""
        self._running = False
        self._notify_status_change()

    def is_running(self) -> bool:
        """Retorna True si el servicio está activo."""
        return self._running

    def switch_to_next(self) -> bool:
        """
        Cambia a la siguiente ventana en la lista de objetivos.
        
        Returns:
            bool: True si el cambio fue exitoso, False en caso contrario
        """
        if not self._running:
            return False

        target = self.targets[self._current_index]
        window = self.controller.find_window_by_title_contains(target)

        if window:
            try:
                print(f"Activando: {window['title']}")
                success = self.controller.activate_window(window["hwnd"])
                
                if success:
                    self._current_index = (self._current_index + 1) % len(self.targets)
                    return True
                else:
                    print(f"No se pudo activar la ventana: {window['title']}")
                    return False
                    
            except Exception as e:
                print(f"Error al activar ventana: {e}")
                return False
        else:
            print(f"No se encontró ventana con título que contenga: {target}")
            return False

    def reset_index(self) -> None:
        """Reinicia el índice de ventanas al inicio."""
        self._current_index = 0

    def _notify_status_change(self) -> None:
        """Notifica cambios de estado a través del callback."""
        if self._on_status_change:
            self._on_status_change(self._running)
