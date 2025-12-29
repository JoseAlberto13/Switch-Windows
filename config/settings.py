# -------------------------
# Configuración de ventanas
# -------------------------
TARGETS = [
    "Google Chrome",
    "Visual Studio Code"
]

INTERVAL_MS = 60000  # 60 segundos entre cambios

# -------------------------
# Configuración de UI
# -------------------------
WINDOW_TITLE = "Window Switcher"
WINDOW_WIDTH = 200  # Más estrecha para layout vertical
WINDOW_HEIGHT = 120  # Más alta para acomodar botones verticales
WINDOW_ALWAYS_ON_TOP = True

# Colores de estado
STATUS_COLOR_RUNNING = "#28a745"  # Verde
STATUS_COLOR_STOPPED = "#dc3545"  # Rojo

# Fuente
STATUS_FONT = ("Segoe UI", 11, "bold")
BUTTON_FONT = ("Segoe UI", 10, "bold")

# -------------------------
# Configuración de sistema
# -------------------------
SUPPORTED_OS = ["Windows"]  # Por ahora solo Windows
