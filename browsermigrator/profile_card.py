#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BrowserMigrator - Profile Card Component
========================================

Responsive card UI component for displaying profile information.
"""

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                           QCheckBox, QPushButton, QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, pyqtSlot
from PyQt6.QtGui import (QFont, QColor, QPixmap, QPainter, QPainterPath, 
                         QBrush, QPen, QIcon)

from .constants import BROWSER_COLORS

class ProfileCard(QFrame):
    """Card widget to display profile information with modern design"""
    
    # Signal when selection changes
    selection_changed = pyqtSignal(bool)
    
    # Signal when fix button is clicked
    fix_requested = pyqtSignal(object)  # Passes profile object
    
    def __init__(self, profile, parent=None):
        super().__init__(parent)
        self.profile = profile
        
        # Set up styling
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        self.setMinimumHeight(100)
        self.setMaximumHeight(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Top row with browser icon, name, and checkbox
        top_row = QHBoxLayout()
        
        # Browser icon
        browser_id = self.profile.get("browser_id", "unknown")
        browser_name = self.profile.get("browser_name", browser_id)
        profile_name = self.profile.get("name", "Unknown Profile")
        
        # Create browser icon
        icon_size = 40
        icon_frame = QFrame()
        icon_frame.setFixedSize(icon_size, icon_size)
        
        # Draw browser icon with initial
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Draw rounded square for browser
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(BROWSER_COLORS.get(profile.browser_type, BROWSER_COLORS["default"]))))
        painter.setPen(Qt.PenStyle.NoPen)
        
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, float(icon_size), float(icon_size), 8.0, 8.0)
        painter.drawPath(path)
        
        # Add initial letter of browser as text
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        
        initial = browser_name[0].upper() if browser_name else "?"
        painter.drawText(
            0, 0, icon_size, icon_size,
            Qt.AlignmentFlag.AlignCenter,
            initial
        )
        painter.end()
        
        # Create label with icon
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(icon_size, icon_size)
        top_row.addWidget(icon_label)
        
        # Profile name and info
        info_layout = QVBoxLayout()
        
        # Profile name
        name_label = QLabel(profile_name)
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        info_layout.addWidget(name_label)
        
        # Full path (with smaller font)
        path_label = QLabel(str(self.profile.path))
        path_label.setFont(QFont("Arial", 8))
        path_label.setWordWrap(True)
        path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addWidget(path_label)
        
        top_row.addLayout(info_layout, 1)
        
        # Checkbox for selection
        self.checkbox = QCheckBox("Select")
        self.checkbox.stateChanged.connect(self._on_selection_changed)
        top_row.addWidget(self.checkbox)
        
        layout.addLayout(top_row)
        
        # Button to open folder
        self.fix_button = QPushButton("Open Folder")
        self.fix_button.setFont(QFont("Arial", 8))
        self.fix_button.clicked.connect(self._on_fix_clicked)
        
        # Bottom layout with stats and fix button
        bottom_layout = QHBoxLayout()
        
        # Stats grid
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setHorizontalSpacing(15)
        stats_layout.setVerticalSpacing(2)
        
        # Add stats if available
        row = 0
        col = 0
        max_cols = 5
        
        stats = self.profile.stats if hasattr(self.profile, 'stats') else {}
        
        if stats.get("bookmarks"):
            self.add_stat(stats_layout, row, col, "Bookmarks", stats.get("bookmarks", 0), "🔖")
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        if stats.get("passwords"):
            self.add_stat(stats_layout, row, col, "Passwords", stats.get("passwords", 0), "🔑")
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        if stats.get("cookies"):
            self.add_stat(stats_layout, row, col, "Cookies", stats.get("cookies", 0), "🍪")
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        if stats.get("history"):
            self.add_stat(stats_layout, row, col, "History", stats.get("history", 0), "🕒")
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        if stats.get("extensions"):
            self.add_stat(stats_layout, row, col, "Extensions", stats.get("extensions", 0), "🧩")
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        bottom_layout.addWidget(stats_frame, 1)
        bottom_layout.addWidget(self.fix_button)
        
        layout.addLayout(bottom_layout)
    
    def add_stat(self, layout, row, col, name, value, icon):
        """Add a stat to the stats grid."""
        if value:
            label = QLabel(f"{icon} {name}: {value}")
            label.setFont(QFont("Arial", 8))
            layout.addWidget(label, row, col)
    
    @pyqtSlot(int)
    def _on_selection_changed(self, state):
        """Handle checkbox state change"""
        # Emit signal when selection changes
        self.selection_changed.emit(state == Qt.CheckState.Checked)
    
    @pyqtSlot()
    def _on_fix_clicked(self):
        """Handle fix button click."""
        # Emit signal when fix button is clicked
        self.fix_requested.emit(self.profile)
    
    def is_selected(self):
        """Return whether this profile is selected"""
        return self.checkbox.isChecked()
    
    def set_selected(self, selected):
        """Set the selection state"""
        self.checkbox.setChecked(selected)
