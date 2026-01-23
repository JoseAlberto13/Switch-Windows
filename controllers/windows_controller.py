
import time
import win32gui
import win32process
import win32con
import win32api
from typing import List, Dict, Optional

from .base_controller import BaseWindowController


class WindowsWindowController(BaseWindowController):

    def list_windows(self) -> List[Dict]:
        """
        Lista todas las ventanas visibles del sistema Windows.
        
        Returns:
            List[Dict]: Lista de ventanas con hwnd, title y pid
        """
        windows = []

        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                    windows.append({"hwnd": hwnd, "title": title, "pid": pid})

        win32gui.EnumWindows(enum_handler, None)
        return windows

    def find_window_by_title_contains(self, text: str) -> Optional[Dict]:
        """
        Busca una ventana cuyo título contenga el texto especificado.
        
        Args:
            text: Texto a buscar (case-insensitive)
            
        Returns:
            Optional[Dict]: Primera ventana encontrada o None
        """
        text = text.lower()
        for w in self.list_windows():
            if text in w["title"].lower():
                return w
        return None

    def activate_window(self, hwnd: int) -> bool:
        """
        Activa y trae al frente la ventana especificada.
        Implementa múltiples estrategias para garantizar la activación.
        
        Args:
            hwnd: Handle de la ventana a activar
            
        Returns:
            bool: True si la ventana fue activada exitosamente
        """
        if not win32gui.IsWindow(hwnd):
            return False

        # 1) Si está minimizada, restaurar
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # 2) Intento normal
        win32gui.BringWindowToTop(hwnd)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.05)

        # 3) Verificación
        if win32gui.GetForegroundWindow() == hwnd:
            return True

        # 4) Fallback: AttachThreadInput (cuando Windows bloquea el foco)
        try:
            fg = win32gui.GetForegroundWindow()
            current_thread = win32api.GetCurrentThreadId()
            fg_thread = win32process.GetWindowThreadProcessId(fg)[0]
            target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]

            # Unimos entradas de hilos temporalmente
            win32process.AttachThreadInput(current_thread, fg_thread, True)
            win32process.AttachThreadInput(current_thread, target_thread, True)

            win32gui.BringWindowToTop(hwnd)
            win32gui.SetForegroundWindow(hwnd)

            win32process.AttachThreadInput(current_thread, fg_thread, False)
            win32process.AttachThreadInput(current_thread, target_thread, False)

        except Exception:
            return False

        return win32gui.GetForegroundWindow() == hwnd

    def get_application_windows(self) -> List[str]:
        """
        Obtiene una lista de títulos de ventanas de aplicaciones abiertas.
        Filtra ventanas del sistema y duplicados.
        """
        windows = self.list_windows()
        
        # Filtrar ventanas del sistema y obtener títulos únicos
        app_titles = set()
        for window in windows:
            title = window["title"].strip()
            # Filtrar ventanas vacías o del sistema
            if title and len(title) > 1:
                # Excluir ventanas comunes del sistema
                excluded = [
                    "Configuración",
                    "Experiencia de entrada de Windows",
                    "Program Manager",
                    "Settings",
                    "Microsoft Text Input Application",
                    "MSCTFIME UI",
                    "Default IME"
                ]
                if not any(exc in title for exc in excluded):
                    app_titles.add(title)
        
        return sorted(list(app_titles))
