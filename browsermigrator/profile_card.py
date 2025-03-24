#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Profile Card (Improved PyQt6 Version)
===============================================

Componente de tarjeta de perfil mejorado para la aplicación Floorper utilizando PyQt6.
Muestra información detallada sobre un perfil de navegador y permite su selección.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QPainterPath, QBrush, QPen, QFont

from .constants import BROWSERS, BROWSER_COLORS

class ProfileCard(QFrame):
    """
    Tarjeta que muestra información detallada sobre un perfil de navegador.
    Permite seleccionar el perfil para migración y realizar acciones específicas.
    """
    
    # Señales
    selection_changed = pyqtSignal(bool)  # Emitida cuando cambia la selección
    fix_requested = pyqtSignal(object)  # Emitida cuando se solicita arreglar el perfil
    
    def __init__(self, profile, parent=None):
        """
        Inicializa la tarjeta de perfil.
        
        Args:
            profile: Objeto de perfil con información del navegador
            parent: Widget padre
        """
        super().__init__(parent)
        
        # Guardar referencia al perfil
        self.profile = profile
        self.selected = False
        
        # Configurar estilo del marco
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Aplicar estilo con color del navegador
        self.apply_style()
        
        # Configurar layout
        self.setup_ui()
    
    def apply_style(self):
        """Aplica estilo visual a la tarjeta basado en el tipo de navegador."""
        # Obtener color del navegador
        browser_color = BROWSER_COLORS.get(
            self.profile.browser_type, 
            BROWSER_COLORS.get("default", "#5E5E5E")
        )
        
        # Aplicar estilo con borde de color
        self.setStyleSheet(f"""
            ProfileCard {{
                border: 1px solid #DDDDDD;
                border-left: 4px solid {browser_color};
                border-radius: 4px;
                background-color: white;
                margin: 2px;
            }}
            ProfileCard:hover {{
                background-color: #F5F5F5;
                border: 1px solid #BBBBBB;
                border-left: 4px solid {browser_color};
            }}
        """)
    
    def setup_ui(self):
        """Configura la interfaz de usuario de la tarjeta."""
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Icono del navegador
        icon_label = QLabel()
        icon_size = 48
        
        # Crear icono personalizado con color del navegador
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Dibujar icono redondeado
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Obtener color del navegador
        browser_color = BROWSER_COLORS.get(
            self.profile.browser_type, 
            BROWSER_COLORS.get("default", "#5E5E5E")
        )
        
        # Dibujar círculo con color del navegador
        painter.setBrush(QBrush(QColor(browser_color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, icon_size, icon_size)
        
        # Añadir inicial del navegador
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 20, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Obtener inicial del navegador
        browser_name = BROWSERS.get(self.profile.browser_type, {}).get("name", "?")
        initial = browser_name[0].upper() if browser_name else "?"
        
        painter.drawText(
            0, 0, icon_size, icon_size,
            Qt.AlignmentFlag.AlignCenter,
            initial
        )
        painter.end()
        
        icon_label.setPixmap(pixmap)
        main_layout.addWidget(icon_label)
        
        # Información del perfil
        info_layout = QVBoxLayout()
        
        # Nombre del perfil y navegador
        header_layout = QHBoxLayout()
        
        # Nombre del perfil
        name_label = QLabel(f"<b>{self.profile.name}</b>")
        name_label.setFont(QFont("Arial", 11))
        header_layout.addWidget(name_label)
        
        # Tipo de navegador
        browser_name = BROWSERS.get(self.profile.browser_type, {}).get("name", "Desconocido")
        browser_label = QLabel(f"({browser_name})")
        browser_label.setStyleSheet("color: #666666;")
        header_layout.addWidget(browser_label)
        
        # Espaciador
        header_layout.addStretch()
        
        info_layout.addLayout(header_layout)
        
        # Ruta del perfil
        path_text = str(self.profile.path)
        path_display = path_text
        
        # Truncar ruta si es muy larga
        if len(path_text) > 60:
            path_display = f"{path_text[:30]}...{path_text[-27:]}"
        
        path_label = QLabel(path_display)
        path_label.setToolTip(path_text)
        path_label.setStyleSheet("color: #666666; font-size: 9pt;")
        info_layout.addWidget(path_label)
        
        # Estadísticas del perfil
        stats_layout = QGridLayout()
        stats_layout.setContentsMargins(0, 5, 0, 0)
        stats_layout.setSpacing(10)
        
        # Iconos para estadísticas
        stat_icons = {
            "passwords": "🔑",
            "tabs": "📄",
            "windows": "🪟",
            "bookmarks": "⭐",
            "cookies": "🍪",
            "certificates": "🔒",
            "extensions": "🧩",
            "history": "📚",
            "forms": "📝",
            "permissions": "✅"
        }
        
        # Añadir estadísticas en una cuadrícula
        row, col = 0, 0
        max_cols = 3  # Número de estadísticas por fila
        
        for key, value in self.profile.stats.items():
            if value > 0:  # Solo mostrar estadísticas con valores positivos
                stat_text = f"{stat_icons.get(key.lower(), '•')} {key.title()}: {value}"
                stat_label = QLabel(stat_text)
                stat_label.setStyleSheet("color: #333333; font-size: 9pt;")
                stats_layout.addWidget(stat_label, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        info_layout.addLayout(stats_layout)
        info_layout.addStretch()
        
        # Añadir layout de información al layout principal
        main_layout.addLayout(info_layout, 1)  # Con factor de estiramiento
        
        # Panel de acciones
        action_layout = QVBoxLayout()
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(5)
        
        # Checkbox de selección
        self.checkbox = QCheckBox("Seleccionar")
        self.checkbox.setChecked(self.selected)
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        action_layout.addWidget(self.checkbox)
        
        # Botón de arreglar perfil (solo para Floorp)
        if self.profile.browser_type == "floorp":
            self.fix_button = QPushButton("Arreglar Perfil")
            self.fix_button.clicked.connect(self.on_fix_button_clicked)
            action_layout.addWidget(self.fix_button)
        
        # Espaciador
        action_layout.addStretch()
        
        # Añadir panel de acciones al layout principal
        main_layout.addLayout(action_layout)
    
    def on_checkbox_changed(self, state):
        """
        Maneja el cambio de estado del checkbox de selección.
        
        Args:
            state: Estado del checkbox
        """
        self.selected = (state == Qt.CheckState.Checked)
        self.selection_changed.emit(self.selected)
    
    def on_fix_button_clicked(self):
        """Maneja el clic en el botón de arreglar perfil."""
        self.fix_requested.emit(self.profile)
    
    def set_selected(self, selected: bool):
        """
        Establece el estado de selección de la tarjeta.
        
        Args:
            selected: Nuevo estado de selección
        """
        if self.selected != selected:
            self.selected = selected
            self.checkbox.setChecked(selected)
            self.selection_changed.emit(selected)
