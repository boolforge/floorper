#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Main Window (Improved PyQt6 Version)
===============================================

Interfaz gráfica mejorada para la aplicación Floorper utilizando PyQt6.
Implementa una interfaz moderna, responsiva y multiplataforma para la migración
de perfiles de navegadores a Floorp.
"""

import os
import sys
import logging
import platform
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QCheckBox, QSplitter,
    QApplication, QTextEdit, QProgressBar, QGridLayout, QFileDialog,
    QMessageBox, QGroupBox, QTabWidget, QComboBox, QToolBar, QStatusBar,
    QToolButton, QMenu, QDialog, QDialogButtonBox, QLineEdit, QSpacerItem,
    QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QSize, QRect, QRectF, QTimer, pyqtSignal, QThread, QEvent,
    QObject, QUrl
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QPainterPath, 
    QBrush, QPen, QIcon, QAction, QDesktopServices, QFontMetrics
)

from .browser_detector import BrowserDetector
from .profile_card import ProfileCard
from .profile_migrator import ProfileMigrator
from .constants import BROWSERS, BROWSER_COLORS, APP_VERSION

class ThemeManager:
    """Gestiona los temas y estilos de la aplicación"""
    
    LIGHT_THEME = {
        "background": "#F5F5F5",
        "card_background": "#FFFFFF",
        "text": "#333333",
        "secondary_text": "#666666",
        "accent": "#0066CC",
        "button": "#0078D7",
        "button_hover": "#005BB5",
        "border": "#DDDDDD"
    }
    
    DARK_THEME = {
        "background": "#2D2D2D",
        "card_background": "#3D3D3D",
        "text": "#FFFFFF",
        "secondary_text": "#BBBBBB",
        "accent": "#0099FF",
        "button": "#0078D7",
        "button_hover": "#009BFF",
        "border": "#555555"
    }
    
    @staticmethod
    def apply_theme(app: QApplication, theme: str = "light") -> None:
        """
        Aplica un tema a toda la aplicación
        
        Args:
            app: Instancia de QApplication
            theme: Nombre del tema ('light' o 'dark')
        """
        if theme.lower() == "dark":
            colors = ThemeManager.DARK_THEME
        else:
            colors = ThemeManager.LIGHT_THEME
        
        # Crear paleta de colores
        palette = QPalette()
        
        # Colores de fondo
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["background"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors["card_background"]))
        
        # Colores de texto
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["text"]))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(colors["secondary_text"]))
        
        # Colores de botones
        palette.setColor(QPalette.ColorRole.Button, QColor(colors["button"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["accent"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        
        # Aplicar paleta
        app.setPalette(palette)
        
        # Estilo global
        stylesheet = f"""
        QMainWindow, QDialog {{
            background-color: {colors["background"]};
        }}
        
        QFrame, QGroupBox {{
            border: 1px solid {colors["border"]};
            border-radius: 4px;
            background-color: {colors["card_background"]};
        }}
        
        QPushButton {{
            background-color: {colors["button"]};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors["button_hover"]};
        }}
        
        QPushButton:disabled {{
            background-color: #AAAAAA;
            color: #DDDDDD;
        }}
        
        QCheckBox {{
            spacing: 8px;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {colors["border"]};
            border-radius: 4px;
            background-color: {colors["card_background"]};
        }}
        
        QTabBar::tab {{
            background-color: {colors["background"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 12px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors["card_background"]};
            border-bottom: none;
        }}
        
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QTextEdit {{
            border: 1px solid {colors["border"]};
            border-radius: 4px;
            background-color: {colors["card_background"]};
            color: {colors["text"]};
        }}
        
        QProgressBar {{
            border: 1px solid {colors["border"]};
            border-radius: 4px;
            background-color: {colors["card_background"]};
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors["accent"]};
            border-radius: 3px;
        }}
        """
        
        app.setStyleSheet(stylesheet)

class LogHandler(QObject):
    """Manejador de logs para la interfaz gráfica"""
    
    log_signal = pyqtSignal(str, str)  # (mensaje, nivel)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("floorper")
        
        # Configurar handler personalizado
        self.handler = QLogHandler(self)
        self.handler.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)
        
    def log(self, message: str, level: str = "info"):
        """
        Emite un mensaje de log
        
        Args:
            message: Mensaje a registrar
            level: Nivel de log ('info', 'warning', 'error', 'debug')
        """
        self.log_signal.emit(message, level)
        
        # También registrar en el logger de Python
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message)

class QLogHandler(logging.Handler):
    """Handler de logging para Qt"""
    
    def __init__(self, log_handler):
        super().__init__()
        self.log_handler = log_handler
        
    def emit(self, record):
        msg = self.format(record)
        level = record.levelname.lower()
        self.log_handler.log_signal.emit(msg, level)

class MigrationWorker(QThread):
    """Worker para realizar la migración en segundo plano"""
    
    progress_signal = pyqtSignal(int, int)  # (actual, total)
    complete_signal = pyqtSignal(bool, str)  # (éxito, mensaje)
    log_signal = pyqtSignal(str, str)  # (mensaje, nivel)
    
    def __init__(self, migrator, source_profiles, target_browser_id):
        super().__init__()
        self.migrator = migrator
        self.source_profiles = source_profiles
        self.target_browser_id = target_browser_id
        self.running = True
        
    def run(self):
        """Ejecuta la migración en segundo plano"""
        try:
            total = len(self.source_profiles)
            successful = 0
            
            for i, profile in enumerate(self.source_profiles):
                if not self.running:
                    break
                
                # Emitir progreso
                self.progress_signal.emit(i, total)
                
                # Registrar inicio
                self.log_signal.emit(
                    f"Migrando perfil: {profile.name} ({profile.browser_type})",
                    "info"
                )
                
                # Realizar migración
                success, message = self.migrator.migrate_profile(
                    profile, self.target_browser_id
                )
                
                # Registrar resultado
                if success:
                    self.log_signal.emit(
                        f"Migración exitosa: {profile.name} - {message}",
                        "info"
                    )
                    successful += 1
                else:
                    self.log_signal.emit(
                        f"Error en migración: {profile.name} - {message}",
                        "error"
                    )
                
                # Actualizar progreso
                self.progress_signal.emit(i + 1, total)
            
            # Emitir resultado final
            if self.running:
                if successful > 0:
                    self.complete_signal.emit(
                        True,
                        f"Migración completada: {successful} de {total} perfiles migrados exitosamente"
                    )
                else:
                    self.complete_signal.emit(
                        False,
                        f"Migración fallida: No se pudo migrar ningún perfil"
                    )
        
        except Exception as e:
            self.log_signal.emit(f"Error en migración: {str(e)}", "error")
            self.complete_signal.emit(False, f"Error en migración: {str(e)}")
    
    def stop(self):
        """Detiene la migración"""
        self.running = False

class AboutDialog(QDialog):
    """Diálogo de información sobre la aplicación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Acerca de Floorper {APP_VERSION}")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(80, 80)
        logo_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Dibujar logo
        painter = QPainter(logo_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#0066CC")))
        painter.setPen(Qt.PenStyle.NoPen)
        
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, 80.0, 80.0, 16.0, 16.0)
        painter.drawPath(path)
        
        # Añadir texto al logo
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 32, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            QRect(0, 0, 80, 80),
            Qt.AlignmentFlag.AlignCenter,
            "FP"
        )
        painter.end()
        
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Título
        title_label = QLabel(f"Floorper {APP_VERSION}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(
            "Herramienta universal de migración de perfiles de navegadores a Floorp"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Información del sistema
        system_group = QGroupBox("Información del Sistema")
        system_layout = QVBoxLayout()
        
        system_info = [
            f"Sistema: {platform.system()} {platform.release()}",
            f"Versión de Python: {platform.python_version()}",
            f"Arquitectura: {platform.machine()}",
            f"Plataforma: {sys.platform}"
        ]
        
        for info in system_info:
            info_label = QLabel(info)
            system_layout.addWidget(info_label)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

class SettingsDialog(QDialog):
    """Diálogo de configuración de la aplicación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Tema
        theme_group = QGroupBox("Tema")
        theme_layout = QHBoxLayout()
        
        theme_label = QLabel("Tema de la aplicación:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Claro", "Oscuro", "Sistema"])
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Navegadores
        browser_group = QGroupBox("Navegadores")
        browser_layout = QVBoxLayout()
        
        browser_label = QLabel("Navegadores críticos (siempre seleccionados):")
        self.firefox_check = QCheckBox("Firefox")
        self.chrome_check = QCheckBox("Chrome")
        self.edge_check = QCheckBox("Edge")
        
        self.firefox_check.setChecked(True)
        self.chrome_check.setChecked(True)
        
        browser_layout.addWidget(browser_label)
        browser_layout.addWidget(self.firefox_check)
        browser_layout.addWidget(self.chrome_check)
        browser_layout.addWidget(self.edge_check)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        # Opciones de migración
        migration_group = QGroupBox("Opciones de Migración")
        migration_layout = QVBoxLayout()
        
        self.backup_check = QCheckBox("Crear copia de seguridad antes de migrar")
        self.merge_check = QCheckBox("Fusionar con perfil existente (si existe)")
        
        self.backup_check.setChecked(True)
        self.merge_check.setChecked(True)
        
        migration_layout.addWidget(self.backup_check)
        migration_layout.addWidget(self.merge_check)
        
        migration_group.setLayout(migration_layout)
        layout.addWidget(migration_group)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

class FloorperWindow(QMainWindow):
    """
    Ventana principal mejorada para la aplicación Floorper.
    Implementa una interfaz moderna y responsiva utilizando PyQt6.
    """
    
    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()
        
        # Configurar logging
        self.log_handler = LogHandler()
        self.log_handler.log_signal.connect(self.on_log)
        
        # Inicializar detector y migrador
        self.browser_detector = BrowserDetector()
        self.profile_migrator = ProfileMigrator()
        
        # Inicializar variables de estado
        self.selected_browsers = {}
        self.detected_profiles = {}
        self.selected_profiles = {}
        self.migration_worker = None
        self.critical_browsers = ["firefox", "chrome"]
        
        # Configurar la interfaz
        self.setup_ui()
        
        # Detectar navegadores automáticamente
        QTimer.singleShot(100, self.refresh_browsers)
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Propiedades de la ventana
        self.setWindowTitle(f"Floorper {APP_VERSION} - Migración de perfiles a Floorp")
        self.setMinimumSize(1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Barra de herramientas
        self.setup_toolbar()
        
        # Cabecera con logo y título
        header_layout = QHBoxLayout()
        
        # Crear logo
        logo_size = 48
        pixmap = QPixmap(logo_size, logo_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Dibujar logo redondeado
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#0066CC")))
        painter.setPen(Qt.PenStyle.NoPen)
        
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, float(logo_size), float(logo_size), 12.0, 12.0)
        painter.drawPath(path)
        
        # Añadir texto "FP" al logo
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 20, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            QRect(0, 0, logo_size, logo_size),
            Qt.AlignmentFlag.AlignCenter,
            "FP"
        )
        painter.end()
        
        # Añadir logo a la cabecera
        logo_label = QLabel()
        logo_label.setPixmap(pixmap)
        header_layout.addWidget(logo_label)
        
        # Añadir título a la cabecera
        title_layout = QVBoxLayout()
        
        title_label = QLabel("Floorper")
        title_font = QFont("Arial", 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Herramienta universal de migración de perfiles a Floorp")
        subtitle_font = QFont("Arial", 10)
        subtitle_label.setFont(subtitle_font)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        
        # Añadir espaciador para empujar todo a la izquierda
        header_layout.addStretch()
        
        # Añadir cabecera al layout principal
        main_layout.addLayout(header_layout)
        
        # Crear splitter para selección de navegadores y visualización de perfiles
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel de selección de navegadores
        browser_panel = QFrame()
        browser_panel.setFrameShape(QFrame.Shape.StyledPanel)
        browser_panel.setMinimumWidth(250)
        browser_panel.setMaximumWidth(350)
        
        browser_layout = QVBoxLayout(browser_panel)
        browser_layout.setContentsMargins(10, 10, 10, 10)
        browser_layout.setSpacing(5)
        
        # Etiqueta de selección de navegadores
        browser_select_label = QLabel("Seleccionar Navegadores Origen")
        browser_select_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        browser_layout.addWidget(browser_select_label)
        
        # Área de desplazamiento para checkboxes de navegadores
        browser_scroll = QScrollArea()
        browser_scroll.setWidgetResizable(True)
        browser_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        browser_scroll_content = QWidget()
        browser_scroll_layout = QVBoxLayout(browser_scroll_content)
        browser_scroll_layout.setContentsMargins(0, 0, 0, 0)
        browser_scroll_layout.setSpacing(5)
        browser_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Añadir checkboxes de navegadores
        self.browser_checkboxes = {}
        for browser_id, browser_info in BROWSERS.items():
            if browser_id == "floorp":  # Omitir Floorp ya que es el destino
                continue
                
            checkbox = QCheckBox(f" {browser_info['name']}")
            checkbox.setObjectName(browser_id)
            checkbox.stateChanged.connect(self.on_browser_selection_changed)
            
            # Estilizar checkbox con color del navegador
            color = BROWSER_COLORS.get(browser_id, BROWSER_COLORS["default"])
            stylesheet = f"""
            QCheckBox {{
                padding: 5px;
                margin: 3px;
                border-left: 4px solid {color};
                background-color: rgba(240, 240, 240, 0.5);
                border-radius: 3px;
            }}
            QCheckBox:hover {{
                background-color: rgba(220, 220, 220, 0.7);
            }}
            """
            checkbox.setStyleSheet(stylesheet)
            
            # Seleccionar Firefox y Chrome por defecto
            if browser_id in self.critical_browsers:
                checkbox.setChecked(True)
            
            self.browser_checkboxes[browser_id] = checkbox
            browser_scroll_layout.addWidget(checkbox)
        
        browser_scroll_layout.addStretch()
        browser_scroll.setWidget(browser_scroll_content)
        browser_layout.addWidget(browser_scroll)
        
        # Botones de acción para navegadores
        browser_buttons_layout = QHBoxLayout()
        
        # Botón de actualizar navegadores
        refresh_button = QPushButton("Actualizar")
        refresh_button.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_button.clicked.connect(self.refresh_browsers)
        browser_buttons_layout.addWidget(refresh_button)
        
        # Botón de detectar perfiles
        detect_button = QPushButton("Detectar Perfiles")
        detect_button.setIcon(QIcon.fromTheme("system-search"))
        detect_button.clicked.connect(self.on_detect_profiles_click)
        browser_buttons_layout.addWidget(detect_button)
        
        browser_layout.addLayout(browser_buttons_layout)
        
        # Añadir panel de navegadores al splitter
        splitter.addWidget(browser_panel)
        
        # Panel de visualización de perfiles
        profile_panel = QFrame()
        profile_panel.setFrameShape(QFrame.Shape.StyledPanel)
        
        profile_layout = QVBoxLayout(profile_panel)
        profile_layout.setContentsMargins(10, 10, 10, 10)
        profile_layout.setSpacing(10)
        
        # Etiqueta de perfiles detectados
        profile_header_layout = QHBoxLayout()
        
        profile_label = QLabel("Perfiles Detectados")
        profile_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        profile_header_layout.addWidget(profile_label)
        
        # Contador de perfiles
        self.profile_count_label = QLabel("(0 perfiles)")
        profile_header_layout.addWidget(self.profile_count_label)
        
        profile_header_layout.addStretch()
        
        # Filtro de perfiles
        filter_label = QLabel("Filtrar:")
        profile_header_layout.addWidget(filter_label)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Buscar perfiles...")
        self.filter_input.textChanged.connect(self.filter_profiles)
        profile_header_layout.addWidget(self.filter_input)
        
        profile_layout.addLayout(profile_header_layout)
        
        # Área de desplazamiento para tarjetas de perfiles
        self.profile_scroll = QScrollArea()
        self.profile_scroll.setWidgetResizable(True)
        self.profile_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.profile_scroll_content = QWidget()
        self.profile_scroll_layout = QVBoxLayout(self.profile_scroll_content)
        self.profile_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.profile_scroll_layout.setSpacing(10)
        self.profile_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.profile_scroll.setWidget(self.profile_scroll_content)
        profile_layout.addWidget(self.profile_scroll)
        
        # Botones de acción para perfiles
        profile_buttons_layout = QHBoxLayout()
        
        # Botón de seleccionar todos
        self.select_all_button = QPushButton("Seleccionar Todos")
        self.select_all_button.setIcon(QIcon.fromTheme("edit-select-all"))
        self.select_all_button.clicked.connect(self.on_select_all_click)
        self.select_all_button.setEnabled(False)
        profile_buttons_layout.addWidget(self.select_all_button)
        
        # Botón de abrir carpeta
        self.open_folder_button = QPushButton("Abrir Carpeta")
        self.open_folder_button.setIcon(QIcon.fromTheme("folder-open"))
        self.open_folder_button.clicked.connect(self.on_open_folder_click)
        profile_buttons_layout.addWidget(self.open_folder_button)
        
        # Botón de migrar
        self.migrate_button = QPushButton("Migrar a Floorp")
        self.migrate_button.setIcon(QIcon.fromTheme("go-next"))
        self.migrate_button.clicked.connect(self.on_migrate_click)
        self.migrate_button.setEnabled(False)
        profile_buttons_layout.addWidget(self.migrate_button)
        
        profile_layout.addLayout(profile_buttons_layout)
        
        # Añadir panel de perfiles al splitter
        splitter.addWidget(profile_panel)
        
        # Establecer tamaños iniciales del splitter
        splitter.setSizes([1, 3])
        
        # Añadir splitter al layout principal
        main_layout.addWidget(splitter, 1)
        
        # Añadir barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Añadir registro de actividad
        log_label = QLabel("Registro de Actividad")
        log_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        main_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        main_layout.addWidget(self.log_text)
        
        # Barra de estado
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Listo")
    
    def setup_toolbar(self):
        """Configura la barra de herramientas."""
        toolbar = QToolBar("Barra de Herramientas Principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Acción de actualizar
        refresh_action = QAction(QIcon.fromTheme("view-refresh"), "Actualizar", self)
        refresh_action.triggered.connect(self.refresh_browsers)
        toolbar.addAction(refresh_action)
        
        # Acción de detectar perfiles
        detect_action = QAction(QIcon.fromTheme("system-search"), "Detectar Perfiles", self)
        detect_action.triggered.connect(self.on_detect_profiles_click)
        toolbar.addAction(detect_action)
        
        toolbar.addSeparator()
        
        # Acción de migrar
        migrate_action = QAction(QIcon.fromTheme("go-next"), "Migrar a Floorp", self)
        migrate_action.triggered.connect(self.on_migrate_click)
        toolbar.addAction(migrate_action)
        
        toolbar.addSeparator()
        
        # Acción de configuración
        settings_action = QAction(QIcon.fromTheme("preferences-system"), "Configuración", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
        
        # Acción de ayuda
        help_action = QAction(QIcon.fromTheme("help-browser"), "Ayuda", self)
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)
        
        # Acción de acerca de
        about_action = QAction(QIcon.fromTheme("help-about"), "Acerca de", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def log(self, message: str, level: str = "info"):
        """
        Añade un mensaje al registro de actividad.
        
        Args:
            message: Mensaje a registrar
            level: Nivel de log ('info', 'warning', 'error', 'debug')
        """
        self.log_handler.log(message, level)
    
    def on_log(self, message: str, level: str):
        """
        Maneja los mensajes de log recibidos.
        
        Args:
            message: Mensaje de log
            level: Nivel de log
        """
        # Formatear mensaje con color según nivel
        timestamp = QApplication.instance().translate("Time", "")
        
        if level == "error":
            formatted = f'<span style="color:red">{timestamp} ERROR: {message}</span>'
        elif level == "warning":
            formatted = f'<span style="color:orange">{timestamp} AVISO: {message}</span>'
        elif level == "debug":
            formatted = f'<span style="color:gray">{timestamp} DEBUG: {message}</span>'
        else:
            formatted = f'{timestamp} {message}'
        
        # Añadir al widget de texto
        self.log_text.append(formatted)
        
        # Desplazar al final
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Actualizar barra de estado
        self.statusBar.showMessage(message)
    
    def on_browser_selection_changed(self):
        """Maneja el cambio de selección de navegadores."""
        # Verificar navegadores críticos
        for browser_id in self.critical_browsers:
            if browser_id in self.browser_checkboxes:
                checkbox = self.browser_checkboxes[browser_id]
                if not checkbox.isChecked():
                    # Forzar selección de navegadores críticos
                    checkbox.setChecked(True)
                    self.log(
                        f"Navegador crítico {browser_id} seleccionado automáticamente",
                        "info"
                    )
        
        # Actualizar lista de navegadores seleccionados
        self.selected_browsers = {}
        for browser_id, checkbox in self.browser_checkboxes.items():
            if checkbox.isChecked():
                self.selected_browsers[browser_id] = BROWSERS[browser_id]
        
        # Actualizar estado de botones
        self.update_button_states()
    
    def refresh_browsers(self):
        """Actualiza la lista de navegadores detectados."""
        try:
            self.log("Detectando navegadores instalados...", "info")
            
            # Detectar navegadores instalados
            detected_browsers = self.browser_detector.detect_browsers()
            
            # Actualizar checkboxes
            for browser_id, checkbox in self.browser_checkboxes.items():
                if browser_id in detected_browsers:
                    checkbox.setChecked(True)
                    self.log(f"Navegador detectado: {BROWSERS[browser_id]['name']}", "info")
            
            # Verificar navegadores críticos
            for browser_id in self.critical_browsers:
                if browser_id in self.browser_checkboxes:
                    checkbox = self.browser_checkboxes[browser_id]
                    if not checkbox.isChecked():
                        # Forzar selección de navegadores críticos
                        checkbox.setChecked(True)
                        self.log(
                            f"Navegador crítico {browser_id} seleccionado automáticamente",
                            "info"
                        )
            
            # Actualizar lista de navegadores seleccionados
            self.selected_browsers = {}
            for browser_id, checkbox in self.browser_checkboxes.items():
                if checkbox.isChecked():
                    self.selected_browsers[browser_id] = BROWSERS[browser_id]
            
            # Actualizar estado de botones
            self.update_button_states()
            
            self.log(f"Detección completada: {len(detected_browsers)} navegadores encontrados", "info")
            
        except Exception as e:
            self.log(f"Error al detectar navegadores: {str(e)}", "error")
    
    def on_detect_profiles_click(self):
        """Maneja el clic en el botón de detectar perfiles."""
        # Verificar que haya navegadores seleccionados
        if not self.selected_browsers:
            QMessageBox.warning(
                self,
                "Sin navegadores seleccionados",
                "Debe seleccionar al menos un navegador para detectar perfiles."
            )
            return
        
        # Detectar perfiles
        self.detect_profiles()
    
    def detect_profiles(self):
        """Detecta perfiles de los navegadores seleccionados."""
        try:
            self.log("Detectando perfiles de navegadores...", "info")
            
            # Limpiar perfiles anteriores
            self.clear_profile_display()
            self.detected_profiles = {}
            self.selected_profiles = {}
            
            # Detectar perfiles para cada navegador seleccionado
            total_profiles = 0
            for browser_id in self.selected_browsers:
                try:
                    profiles = self.browser_detector.detect_profiles(browser_id)
                    if profiles:
                        self.detected_profiles[browser_id] = profiles
                        total_profiles += len(profiles)
                        self.log(
                            f"Detectados {len(profiles)} perfiles para {BROWSERS[browser_id]['name']}",
                            "info"
                        )
                except Exception as e:
                    self.log(
                        f"Error al detectar perfiles para {browser_id}: {str(e)}",
                        "error"
                    )
            
            # Mostrar perfiles detectados
            self.display_detected_profiles()
            
            # Actualizar contador de perfiles
            self.profile_count_label.setText(f"({total_profiles} perfiles)")
            
            # Actualizar estado de botones
            self.update_button_states()
            
            self.log(f"Detección completada: {total_profiles} perfiles encontrados", "info")
            
        except Exception as e:
            self.log(f"Error al detectar perfiles: {str(e)}", "error")
    
    def clear_profile_display(self):
        """Limpia la visualización de perfiles."""
        # Eliminar todas las tarjetas de perfil
        while self.profile_scroll_layout.count():
            item = self.profile_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Limpiar lista de tarjetas
        self.profile_cards = []
    
    def display_detected_profiles(self):
        """Muestra los perfiles detectados."""
        # Limpiar visualización actual
        self.clear_profile_display()
        
        # Mostrar perfiles por navegador
        for browser_id, profiles in self.detected_profiles.items():
            # Crear grupo para el navegador
            browser_group = QGroupBox(BROWSERS[browser_id]['name'])
            browser_layout = QVBoxLayout(browser_group)
            
            # Añadir perfiles al grupo
            for profile in profiles:
                # Crear tarjeta de perfil
                card = ProfileCard(profile)
                card.selection_changed.connect(
                    lambda selected, p=profile: self.on_profile_selected(p, selected)
                )
                card.fix_requested.connect(self.on_profile_fix)
                
                # Añadir tarjeta al layout
                browser_layout.addWidget(card)
                
                # Guardar referencia a la tarjeta
                self.profile_cards.append(card)
            
            # Añadir grupo al layout principal
            self.profile_scroll_layout.addWidget(browser_group)
        
        # Añadir espaciador al final
        self.profile_scroll_layout.addStretch()
        
        # Habilitar botones si hay perfiles
        self.select_all_button.setEnabled(bool(self.profile_cards))
    
    def filter_profiles(self, text: str):
        """
        Filtra los perfiles mostrados según el texto de búsqueda.
        
        Args:
            text: Texto de búsqueda
        """
        text = text.lower()
        
        # Recorrer todas las tarjetas de perfil
        for i in range(self.profile_scroll_layout.count()):
            item = self.profile_scroll_layout.itemAt(i)
            widget = item.widget()
            
            if isinstance(widget, QGroupBox):
                # Es un grupo de navegador
                show_group = False
                
                # Verificar si algún perfil del grupo coincide
                for j in range(widget.layout().count()):
                    child_item = widget.layout().itemAt(j)
                    child_widget = child_item.widget()
                    
                    if isinstance(child_widget, ProfileCard):
                        # Verificar si el perfil coincide con el filtro
                        profile = child_widget.profile
                        matches = (
                            text in profile.name.lower() or
                            text in profile.browser_type.lower() or
                            text in str(profile.path).lower()
                        )
                        
                        # Mostrar u ocultar el perfil
                        child_widget.setVisible(matches)
                        
                        # Si al menos un perfil coincide, mostrar el grupo
                        if matches:
                            show_group = True
                
                # Mostrar u ocultar el grupo
                widget.setVisible(show_group)
    
    def on_profile_selected(self, profile, selected: bool):
        """
        Maneja la selección de un perfil.
        
        Args:
            profile: Perfil seleccionado
            selected: Estado de selección
        """
        # Actualizar lista de perfiles seleccionados
        if selected:
            self.selected_profiles[profile.path] = profile
        elif profile.path in self.selected_profiles:
            del self.selected_profiles[profile.path]
        
        # Actualizar estado de botones
        self.update_button_states()
    
    def on_profile_fix(self, profile):
        """
        Maneja la solicitud de arreglar un perfil.
        
        Args:
            profile: Perfil a arreglar
        """
        # Abrir carpeta del perfil
        path = str(profile.path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        self.log(f"Abriendo carpeta del perfil: {path}", "info")
    
    def on_select_all_click(self):
        """Maneja el clic en el botón de seleccionar todos."""
        # Verificar si hay perfiles para seleccionar
        if not self.profile_cards:
            return
        
        # Determinar si seleccionar o deseleccionar todos
        select_all = len(self.selected_profiles) < len(self.profile_cards)
        
        # Actualizar selección de todas las tarjetas
        for card in self.profile_cards:
            card.set_selected(select_all)
        
        # Actualizar texto del botón
        if select_all:
            self.select_all_button.setText("Deseleccionar Todos")
            self.log("Todos los perfiles seleccionados", "info")
        else:
            self.select_all_button.setText("Seleccionar Todos")
            self.log("Todos los perfiles deseleccionados", "info")
    
    def on_migrate_click(self):
        """Maneja el clic en el botón de migrar."""
        # Verificar que haya perfiles seleccionados
        if not self.selected_profiles:
            QMessageBox.warning(
                self,
                "Sin perfiles seleccionados",
                "Debe seleccionar al menos un perfil para migrar."
            )
            return
        
        # Confirmar migración
        profiles_count = len(self.selected_profiles)
        result = QMessageBox.question(
            self,
            "Confirmar Migración",
            f"¿Está seguro de que desea migrar {profiles_count} perfiles a Floorp?\n\n"
            "Este proceso puede tardar varios minutos dependiendo del tamaño de los perfiles.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result != QMessageBox.StandardButton.Yes:
            return
        
        # Iniciar migración
        self.start_migration()
    
    def start_migration(self):
        """Inicia el proceso de migración."""
        try:
            # Preparar lista de perfiles a migrar
            profiles_to_migrate = list(self.selected_profiles.values())
            
            # Mostrar barra de progreso
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(profiles_to_migrate))
            
            # Deshabilitar botones durante la migración
            self.migrate_button.setEnabled(False)
            self.select_all_button.setEnabled(False)
            
            # Crear worker para migración en segundo plano
            self.migration_worker = MigrationWorker(
                self.profile_migrator,
                profiles_to_migrate,
                "floorp"
            )
            
            # Conectar señales
            self.migration_worker.progress_signal.connect(self.update_migration_progress)
            self.migration_worker.complete_signal.connect(self.on_migration_complete)
            self.migration_worker.log_signal.connect(self.log)
            
            # Iniciar worker
            self.migration_worker.start()
            
            self.log("Iniciando migración de perfiles a Floorp...", "info")
            
        except Exception as e:
            self.log(f"Error al iniciar migración: {str(e)}", "error")
            self.progress_bar.setVisible(False)
            self.update_button_states()
    
    def update_migration_progress(self, current: int, total: int):
        """
        Actualiza el progreso de la migración.
        
        Args:
            current: Índice actual
            total: Total de perfiles
        """
        # Actualizar barra de progreso
        self.progress_bar.setValue(current)
        self.progress_bar.setMaximum(total)
        
        # Actualizar barra de estado
        progress_percent = int(current / total * 100) if total > 0 else 0
        self.statusBar.showMessage(f"Migrando perfiles: {current}/{total} ({progress_percent}%)")
    
    def on_migration_complete(self, success: bool, message: str):
        """
        Maneja la finalización de la migración.
        
        Args:
            success: Indica si la migración fue exitosa
            message: Mensaje de resultado
        """
        # Ocultar barra de progreso
        self.progress_bar.setVisible(False)
        
        # Registrar resultado
        if success:
            self.log(message, "info")
            
            # Mostrar mensaje de éxito
            QMessageBox.information(
                self,
                "Migración Completada",
                message + "\n\n"
                "Los perfiles han sido migrados exitosamente a Floorp."
            )
        else:
            self.log(message, "error")
            
            # Mostrar mensaje de error
            QMessageBox.critical(
                self,
                "Error en Migración",
                message + "\n\n"
                "Ocurrió un error durante la migración de perfiles."
            )
        
        # Limpiar worker
        self.migration_worker = None
        
        # Actualizar estado de botones
        self.update_button_states()
    
    def on_open_folder_click(self):
        """Maneja el clic en el botón de abrir carpeta."""
        # Abrir diálogo para seleccionar carpeta
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar Carpeta de Perfiles",
            str(Path.home())
        )
        
        if folder:
            # Abrir carpeta seleccionada
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
            self.log(f"Abriendo carpeta: {folder}", "info")
    
    def update_button_states(self):
        """Actualiza el estado de los botones según la selección actual."""
        # Botón de migrar
        self.migrate_button.setEnabled(bool(self.selected_profiles))
        
        # Botón de seleccionar todos
        self.select_all_button.setEnabled(bool(self.profile_cards))
        
        # Actualizar texto del botón de seleccionar todos
        if self.profile_cards and len(self.selected_profiles) == len(self.profile_cards):
            self.select_all_button.setText("Deseleccionar Todos")
        else:
            self.select_all_button.setText("Seleccionar Todos")
    
    def show_settings(self):
        """Muestra el diálogo de configuración."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Aplicar configuración
            self.log("Configuración actualizada", "info")
    
    def show_help(self):
        """Muestra la ayuda de la aplicación."""
        # Abrir URL de ayuda
        QDesktopServices.openUrl(QUrl("https://github.com/boolforge/floorper"))
        self.log("Abriendo documentación de ayuda", "info")
    
    def show_about(self):
        """Muestra el diálogo de acerca de."""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def closeEvent(self, event):
        """
        Maneja el evento de cierre de la ventana.
        
        Args:
            event: Evento de cierre
        """
        # Verificar si hay una migración en curso
        if self.migration_worker and self.migration_worker.isRunning():
            # Preguntar si desea cancelar la migración
            result = QMessageBox.question(
                self,
                "Migración en Curso",
                "Hay una migración en curso. ¿Desea cancelarla y salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if result == QMessageBox.StandardButton.Yes:
                # Detener migración
                self.migration_worker.stop()
                self.migration_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    """Función principal para iniciar la aplicación."""
    app = QApplication(sys.argv)
    app.setApplicationName("Floorper")
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Floorper")
    
    # Aplicar tema
    ThemeManager.apply_theme(app, "light")
    
    # Crear y mostrar ventana principal
    window = FloorperWindow()
    window.show()
    
    # Iniciar bucle de eventos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
