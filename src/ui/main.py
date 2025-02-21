from PyQt6.QtWidgets import QApplication
import sys
from .styles import styles  # Asegúrate de importar el archivo de estilos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(styles)  # Aplicar el estilo global
    # ... resto del código para iniciar la aplicación ... 