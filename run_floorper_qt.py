#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Lanzador de GUI PyQt6
================================

Script principal para iniciar la versión mejorada de Floorper con interfaz PyQt6.
Proporciona una experiencia de usuario moderna, responsiva y multiplataforma.
"""

import sys
import os
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('floorper.log'),
        logging.StreamHandler()
    ]
)

# Asegurar que el directorio del script está en el path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from PyQt6.QtWidgets import QApplication
    from browsermigrator.main_window_improved import FloorperWindow
    from browsermigrator.constants import APP_VERSION
except ImportError as e:
    print(f"Error al importar dependencias: {e}")
    print("Asegúrese de tener instalado PyQt6 (pip install PyQt6)")
    sys.exit(1)

def main():
    """Función principal para iniciar la aplicación."""
    try:
        # Crear aplicación Qt
        app = QApplication(sys.argv)
        app.setApplicationName("Floorper")
        app.setApplicationVersion(APP_VERSION)
        app.setOrganizationName("Floorper")
        
        # Crear y mostrar ventana principal
        window = FloorperWindow()
        window.show()
        
        # Iniciar bucle de eventos
        sys.exit(app.exec())
        
    except Exception as e:
        logging.error(f"Error al iniciar la aplicación: {e}", exc_info=True)
        print(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
