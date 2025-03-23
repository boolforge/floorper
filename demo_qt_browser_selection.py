#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyQt6 Demo: Browser Selection with Reliable Checkbox Handling

This demonstrates how PyQt6 provides more reliable checkbox state handling
compared to Tkinter, focusing specifically on the browser selection issue.
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QCheckBox, QPushButton, QFrame, 
                           QGroupBox, QTextEdit, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class BrowserSelectionDemo(QMainWindow):
    """Demo window showing reliable browser selection with PyQt6"""
    
    def __init__(self):
        super().__init__()
        
        # Browser data - simplified version for demo
        self.browsers = {
            "firefox": {"name": "Firefox", "color": "#FF9500"},
            "chrome": {"name": "Google Chrome", "color": "#4285F4"},
            "edge": {"name": "Microsoft Edge", "color": "#0078D7"},
            "opera": {"name": "Opera", "color": "#FF1B2D"},
            "brave": {"name": "Brave", "color": "#FB542B"},
            "vivaldi": {"name": "Vivaldi", "color": "#EF3939"},
            "librewolf": {"name": "LibreWolf", "color": "#00ACFF"},
            "waterfox": {"name": "Waterfox", "color": "#00AEF0"},
            "pale_moon": {"name": "Pale Moon", "color": "#2A2A2E"},
            "basilisk": {"name": "Basilisk", "color": "#409A5C"},
            "chromium": {"name": "Chromium", "color": "#4587F3"},
            "opera_gx": {"name": "Opera GX", "color": "#FF1B2D"},
            "tor_browser": {"name": "Tor Browser", "color": "#7D4698"},
            "yandex": {"name": "Yandex Browser", "color": "#FFCC00"},
            "slimjet": {"name": "Slimjet", "color": "#5E5E5E"},
            "seamonkey": {"name": "SeaMonkey", "color": "#11A9F7"}
        }
        
        self.browser_checkboxes = {}
        self.log_text = None
        
        # Setup UI
        self.setWindowTitle("Browser Selection Demo (PyQt6)")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        
        # Auto-detect after short delay (let UI render first)
        QTimer.singleShot(500, self.set_default_browsers)
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Browser Selection Demo (PyQt6)")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "This demo shows how PyQt6 provides reliable checkbox state management.\n"
            "Notice how the checkboxes for Firefox and Chrome are always selected by default."
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # Browser selection
        browser_group = QGroupBox("Select Browsers")
        browser_layout = QVBoxLayout()
        
        # Create scrollable area for browsers
        browser_scroll = QScrollArea()
        browser_scroll.setWidgetResizable(True)
        browser_scroll_widget = QWidget()
        browser_scroll_layout = QVBoxLayout(browser_scroll_widget)
        browser_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        browser_scroll.setWidget(browser_scroll_widget)
        
        # Create browser checkboxes in 2 columns
        row_layout = QHBoxLayout()
        col_count = 0
        col_max = 2
        
        for browser_id, browser in self.browsers.items():
            # Create checkbox with colored border
            checkbox = QCheckBox(browser["name"])
            
            # Style the checkbox with CSS
            stylesheet = f"""
            QCheckBox {{
                padding: 5px;
                margin: 3px;
                border-left: 4px solid {browser["color"]};
                background-color: rgba(240, 240, 240, 0.5);
                border-radius: 3px;
            }}
            QCheckBox:hover {{
                background-color: rgba(220, 220, 220, 0.7);
            }}
            """
            checkbox.setStyleSheet(stylesheet)
            
            # Store checkbox
            self.browser_checkboxes[browser_id] = checkbox
            
            # Add to layout with columns
            if col_count == 0:
                row_layout = QHBoxLayout()
                browser_scroll_layout.addLayout(row_layout)
            
            row_layout.addWidget(checkbox)
            col_count = (col_count + 1) % col_max
        
        browser_layout.addWidget(browser_scroll)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Detect profiles button
        self.detect_button = QPushButton("Detect Profiles")
        self.detect_button.clicked.connect(self.on_detect_profiles_click)
        button_layout.addWidget(self.detect_button)
        
        # Reset button
        self.reset_button = QPushButton("Reset Selections")
        self.reset_button.clicked.connect(self.reset_selections)
        button_layout.addWidget(self.reset_button)
        
        browser_layout.addLayout(button_layout)
        browser_group.setLayout(browser_layout)
        main_layout.addWidget(browser_group)
        
        # Log area
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
    def log(self, message):
        """Add message to log."""
        if self.log_text:
            self.log_text.append(message)
            # Scroll to bottom
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
    def set_default_browsers(self):
        """Set default browser selection and verify it worked."""
        try:
            self.log("Setting default browsers...")
            
            # Simulate browser detection (would normally query the OS)
            # In a real implementation, this would be from detector.get_installed_browsers()
            detected = ["firefox", "chrome", "edge"]  # Simulated detected browsers
            
            # First approach: select detected browsers in UI
            self.log(f"Auto-detected browsers: {', '.join(detected)}")
            for browser_id in detected:
                if browser_id in self.browser_checkboxes:
                    self.browser_checkboxes[browser_id].setChecked(True)
                    self.log(f"Selected {browser_id} (UI approach)")
            
            # CRITICAL: Force Firefox and Chrome to be selected
            # This is the key improvement over Tkinter - reliable state management
            for critical_browser in ["firefox", "chrome"]:
                if critical_browser in self.browser_checkboxes:
                    checkbox = self.browser_checkboxes[critical_browser]
                    if not checkbox.isChecked():
                        checkbox.setChecked(True)
                        self.log(f"Force-selected {critical_browser} (failsafe)")
            
            # Verify selections - reliable with PyQt6
            selected = self.get_selected_browsers()
            
            if selected:
                self.log(f"Verified selection: {', '.join(selected)}")
            else:
                # This block should never execute with PyQt6, but included for completeness
                self.log("VERIFICATION FAILED! No browsers selected. Using emergency selection.")
                # Final fallback
                for browser_id in ["firefox", "chrome"]:
                    if browser_id in self.browser_checkboxes:
                        self.browser_checkboxes[browser_id].setChecked(True)
                        self.log(f"Emergency selection of {browser_id}")
                
                # Verify again after emergency selection
                selected = self.get_selected_browsers()
                self.log(f"After emergency: {', '.join(selected)}")
            
        except Exception as e:
            self.log(f"Error in default browser selection: {str(e)}")
            
    def get_selected_browsers(self):
        """Get list of selected browsers."""
        selected = []
        for browser_id, checkbox in self.browser_checkboxes.items():
            if checkbox.isChecked():
                selected.append(browser_id)
        return selected
    
    def on_detect_profiles_click(self):
        """Handler for detect profiles button click."""
        try:
            # Emergency browser selection check BEFORE calling detect_profiles
            selected = self.get_selected_browsers()
            
            # If nothing is selected, force select Firefox and Chrome immediately
            if not selected:
                self.log("BUTTON CLICK FIX: No browsers selected! Force-selecting Firefox and Chrome")
                for browser_id in ["firefox", "chrome"]:
                    if browser_id in self.browser_checkboxes:
                        self.browser_checkboxes[browser_id].setChecked(True)
                        self.log(f"Force-selected {browser_id}")
                
                # Update selected list after forced selection
                selected = self.get_selected_browsers()
            
            # Display what would happen in the real app
            self.log(f"Selected browsers: {', '.join(selected)}")
            self.log(f"In a real app, we would now detect profiles for these browsers")
            
            # Show message box to demonstrate reliable state
            QMessageBox.information(
                self,
                "Browser Selection",
                f"Selected browsers: {', '.join(selected)}\n\n"
                "With PyQt6, browser checkboxes maintain their state reliably!"
            )
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
    
    def reset_selections(self):
        """Reset all checkbox selections."""
        # Clear all checkboxes
        for checkbox in self.browser_checkboxes.values():
            checkbox.setChecked(False)
        
        self.log("All selections cleared. Try clicking 'Detect Profiles'")
        self.log("Notice how Firefox and Chrome will be auto-selected as a failsafe!")

def main():
    app = QApplication(sys.argv)
    window = BrowserSelectionDemo()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
