from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseWindowController(ABC):
    """
    Interfaz base para controladores de ventanas.
    Implementa el patrón Strategy para diferentes sistemas operativos.
    """

    @abstractmethod
    def list_windows(self) -> List[Dict]:
        """
        Lista todas las ventanas visibles del sistema.
        
        Returns:
            List[Dict]: Lista de diccionarios con información de ventanas.
                       Cada dict debe contener: hwnd, title, pid
        """
        pass

    @abstractmethod
    def find_window_by_title_contains(self, text: str) -> Optional[Dict]:
        """
        Busca una ventana cuyo título contenga el texto especificado.
        
        Args:
            text: Texto a buscar en el título de la ventana
            
        Returns:
            Optional[Dict]: Información de la ventana encontrada o None
        """
        pass

    @abstractmethod
    def activate_window(self, hwnd: int) -> bool:
        """
        Activa y trae al frente la ventana especificada.
        
        Args:
            hwnd: Handle de la ventana a activar
            
        Returns:
            bool: True si la activación fue exitosa, False en caso contrario
        """
        pass
