import sys
import os

def print_project_structure(startpath, exclude_dirs=None):
    """
    Imprime la estructura del proyecto excluyendo directorios específicos
    """
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'venv', '.pytest_cache', '.venv'}
    
    print("\nProject Structure:")
    print("─" * 50)
    
    for root, dirs, files in os.walk(startpath):
        # Excluir directorios no deseados
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * level
        print(f"{indent}├── {os.path.basename(root)}/")
        
        sub_indent = '│   ' * (level + 1)
        for file in sorted(files):
            if not file.startswith('.'):  # Excluir archivos ocultos
                print(f"{sub_indent}├── {file}")
    
    print("─" * 50)

# Obtener la ruta del proyecto (un nivel arriba de src)
src_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(src_path)

# Imprimir la estructura del proyecto
print_project_structure(project_root)

# Agregar el directorio src al PYTHONPATH
sys.path.append(src_path)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from utils.logger import logger
from ui.main_window import MainWindow

def main():
    try:
        logger.info("Starting application...")
        app = QApplication(sys.argv)
        
        # Establecer ícono de la aplicación
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'app_icon.svg')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        app.setStyle('Fusion')
        window = MainWindow()
        window.show()
        logger.info("Application started successfully")
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        raise

if __name__ == '__main__':
    main()
