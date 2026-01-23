from config import settings
from utils.os_detect import get_os
from controllers.windows_controller import WindowsWindowController
from core.switcher_service import WindowSwitcherService
from ui.gui import WindowSwitcherGUI


class Application:
    """Aplicación principal que orquesta todos los componentes."""

    def __init__(self):
        self._validate_os()
        self._init_controller()
        self._init_service()
        self._init_ui()
        self._connect_components()

    def _validate_os(self) -> None:
        """Valida que el sistema operativo sea compatible."""
        os_name = get_os()
        if os_name not in settings.SUPPORTED_OS:
            raise RuntimeError(
                f"Sistema operativo '{os_name}' no soportado. "
                f"Sistemas soportados: {', '.join(settings.SUPPORTED_OS)}"
            )
        print(f"[OK] Sistema operativo detectado: {os_name}")

    def _init_controller(self) -> None:
        """Inicializa el controlador de ventanas según el OS."""
        self.controller = WindowsWindowController()
        print("[OK] Controlador de ventanas inicializado")

    def _init_service(self) -> None:
        """Inicializa el servicio de cambio de ventanas."""
        self.service = WindowSwitcherService(
            controller=self.controller,
            targets=settings.TARGETS,
            interval_ms=settings.INTERVAL_MS
        )
        print(f"[OK] Servicio inicializado con {len(settings.TARGETS)} ventanas objetivo")

    def _init_ui(self) -> None:
        """Inicializa la interfaz gráfica."""
        self.gui = WindowSwitcherGUI(
            title=settings.WINDOW_TITLE,
            width=settings.WINDOW_WIDTH,
            height=settings.WINDOW_HEIGHT,
            always_on_top=settings.WINDOW_ALWAYS_ON_TOP
        )
        print("[OK] Interfaz grafica inicializada")

    def _connect_components(self) -> None:
        """Conecta los componentes entre sí mediante callbacks."""
        # Conectar botones de UI con el servicio
        self.gui.set_start_callback(self._on_start)
        self.gui.set_stop_callback(self._on_stop)
        
        # Conectar gestión de targets
        self.gui.set_add_target_callback(self._on_add_target)
        self.gui.set_remove_target_callback(self._on_remove_target)
        self.gui.set_refresh_windows_callback(self._on_refresh_windows)

        # Conectar cambios de estado del servicio con la UI
        self.service.set_status_callback(self.gui.update_status)
        
        # Actualizar la lista inicial de targets en la GUI
        self.gui.update_targets_list(self.service.get_targets())
        
        print("[OK] Componentes conectados")

    def _on_start(self) -> None:
        """Inicia el servicio y programa el primer cambio."""
        self.service.start()
        self._schedule_next_switch()

    def _on_stop(self) -> None:
        """Detiene el servicio."""
        self.service.stop()

    def _schedule_next_switch(self) -> None:
        """Programa el siguiente cambio de ventana (llamada recursiva)."""
        if not self.service.is_running():
            return

        self.service.switch_to_next()
        self.gui.schedule_task(settings.INTERVAL_MS, self._schedule_next_switch)

    def _on_add_target(self, target: str) -> None:
        """Añade un nuevo target y actualiza la GUI."""
        if self.service.add_target(target):
            print(f"[INFO] Target añadido: {target}")
            self.gui.update_targets_list(self.service.get_targets())
        else:
            print(f"[WARN] El target ya existe: {target}")

    def _on_remove_target(self, target: str) -> None:
        """Elimina un target y actualiza la GUI."""
        if self.service.remove_target(target):
            print(f"[INFO] Target eliminado: {target}")
            self.gui.update_targets_list(self.service.get_targets())
        else:
            print(f"[WARN] El target no existe: {target}")

    def _on_refresh_windows(self) -> list:
        """Obtiene la lista actualizada de ventanas abiertas."""
        windows = self.controller.get_application_windows()
        print(f"[INFO] Ventanas disponibles actualizadas: {len(windows)} encontradas")
        return windows

    def run(self) -> None:
        """Inicia la aplicación."""
        print("\n" + "="*50)
        print("Window Switcher - Aplicacion iniciada")
        print("="*50 + "\n")
        self.gui.run()


def main():
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {e}")
        raise


if __name__ == "__main__":
    main()
