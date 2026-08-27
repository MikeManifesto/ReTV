#!/usr/bin/env python3
"""
TV Launcher – Clean theme with dark/light mode toggle.
Persistent settings (dark mode + grid/list view).
"""

import sys
import os
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QMessageBox, QLabel,
    QFrame, QProgressBar, QListView
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor

try:
    from channel_manager_gui import ChannelManager
    CHANNEL_MANAGER_AVAILABLE = True
except ImportError:
    CHANNEL_MANAGER_AVAILABLE = False

class TVLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TV Channel Launcher")
        self.setMinimumSize(900, 650)

        # Load settings
        self.settings_file = Path("settings.json")
        self.load_settings()

        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # --- Header ---
        self.header = QFrame()
        self.header.setObjectName("header")
        self.header.setStyleSheet("QFrame#header { border: none; background-color: #4a7a9a; }")
        self.setup_header()
        self.main_layout.addWidget(self.header)

        # --- Count bar ---
        self.count_frame = QFrame()
        self.count_frame.setStyleSheet("background-color: #f8f8f8; border: 1px solid #d0d0d0; padding: 4px 8px;")
        count_layout = QHBoxLayout(self.count_frame)
        count_layout.setContentsMargins(8, 4, 8, 4)
        self.count_label = QLabel("Channels: 0")
        self.count_label.setStyleSheet("color: #4a7a9a; font-weight: bold; font-size: 13px; background-color: transparent;")
        count_layout.addWidget(self.count_label)
        self.status_text = QLabel("Ready")
        self.status_text.setStyleSheet("color: #666666; font-size: 12px; background-color: transparent;")
        count_layout.addWidget(self.status_text, alignment=Qt.AlignRight)
        self.main_layout.addWidget(self.count_frame)

        # --- Channel list ---
        self.channel_list = QListWidget()
        self.channel_list.setFlow(QListView.TopToBottom)
        self.channel_list.setWrapping(False)
        self.channel_list.setIconSize(QSize(150, 150))
        self.main_layout.addWidget(self.channel_list)

        # --- Button frame ---
        self.button_frame = QFrame()
        self.button_frame.setStyleSheet("background-color: #f8f8f8; border: 1px solid #d0d0d0; padding: 6px;")
        button_layout = QHBoxLayout(self.button_frame)
        button_layout.setSpacing(8)

        self.manage_btn = QPushButton("Manage Channels")
        if CHANNEL_MANAGER_AVAILABLE:
            self.manage_btn.clicked.connect(self.open_channel_manager)
        else:
            self.manage_btn.setEnabled(False)
            self.manage_btn.setToolTip("Install channel_manager_gui.py")
        button_layout.addWidget(self.manage_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_channels)
        button_layout.addWidget(self.refresh_btn)

        self.launch_btn = QPushButton("Launch Selected")
        self.launch_btn.clicked.connect(self.launch_selected)
        button_layout.addWidget(self.launch_btn)

        self.toggle_view_btn = QPushButton("Grid View" if not self.is_grid_view else "List View")
        self.toggle_view_btn.clicked.connect(self.toggle_view)
        button_layout.addWidget(self.toggle_view_btn)

        self.dark_mode_btn = QPushButton("Dark Mode" if not self.is_dark_mode else "Light Mode")
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        button_layout.addWidget(self.dark_mode_btn)

        button_layout.addStretch()
        info_label = QLabel("Double-click a channel or select and click Launch")
        info_label.setStyleSheet("color: #888888; font-size: 10px; background-color: transparent;")
        button_layout.addWidget(info_label)

        self.main_layout.addWidget(self.button_frame)

        # --- Apply mode and view ---
        if self.is_dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

        self.load_channels()

        # Apply grid view if saved
        if self.is_grid_view:
            self.apply_grid_view()
            self.toggle_view_btn.setText("List View")
        else:
            self.apply_list_view()
            self.toggle_view_btn.setText("Grid View")

    def setup_header(self):
        """Set up the header with background image."""
        assets_path = Path("assets")
        bg_image_path = assets_path / "retvbckgrnd"
        bg_image = None
        for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            candidate = Path(f"{bg_image_path}{ext}")
            if candidate.exists():
                bg_image = candidate
                break
        if bg_image and bg_image.exists():
            pixmap = QPixmap(str(bg_image))
            if not pixmap.isNull():
                img_width = pixmap.width()
                img_height = pixmap.height()
                initial_width = self.width() if self.width() > 0 else 900
                new_height = int(initial_width * img_height / img_width)
                self.image_label = QLabel()
                self.image_label.setPixmap(pixmap.scaled(initial_width, new_height,
                                                         Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.image_label.setAlignment(Qt.AlignCenter)
                self.image_label.setStyleSheet("background-color: transparent; border: none;")
                header_layout = QVBoxLayout(self.header)
                header_layout.setContentsMargins(0, 0, 0, 0)
                header_layout.addWidget(self.image_label)
                self.header.setFixedHeight(new_height)
                self.header_pixmap = pixmap
                return
        # Fallback
        self.header.setStyleSheet("QFrame#header { background-color: #4a7a9a; border: none; min-height: 60px; }")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'header_pixmap') and hasattr(self, 'image_label'):
            img_width = self.header_pixmap.width()
            img_height = self.header_pixmap.height()
            new_width = self.width()
            new_height = int(new_width * img_height / img_width)
            if new_height > 0:
                self.image_label.setPixmap(self.header_pixmap.scaled(
                    new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.header.setFixedHeight(new_height)

    def load_settings(self):
        """Load settings from settings.json."""
        self.is_dark_mode = False
        self.is_grid_view = False
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.is_dark_mode = data.get('dark_mode', False)
                    self.is_grid_view = data.get('grid_view', False)
        except:
            pass

    def save_settings(self):
        """Save settings to settings.json."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump({
                    'dark_mode': self.is_dark_mode,
                    'grid_view': self.is_grid_view
                }, f)
        except:
            pass

    def apply_light_mode(self):
        self.is_dark_mode = False
        self.save_settings()
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QLabel { color: #333333; }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                color: #333333;
            }
            QListWidget::item { border-bottom: 1px solid #e8e8e8; color: #333333; }
            QListWidget::item:selected { background-color: #4a7a9a; color: #ffffff; }
            QListWidget::item:hover:!selected { background-color: #e8eef0; }
            QPushButton {
                background-color: #e8e8e8;
                color: #333333;
                border: 1px solid #c0c0c0;
            }
            QPushButton:hover { background-color: #d8d8d8; border: 1px solid #4a7a9a; }
            QPushButton:pressed { background-color: #c8c8c8; border: 1px solid #3a6a8a; }
            QPushButton:disabled { background-color: #f0f0f0; color: #aaaaaa; }
            QFrame { background-color: #f0f0f0; border: 1px solid #d0d0d0; }
            QFrame#header { border: none; }
            QProgressBar { border: 1px solid #c0c0c0; background-color: #ffffff; color: #333333; }
            QProgressBar::chunk { background-color: #4a7a9a; }
        """)
        self.count_frame.setStyleSheet("background-color: #f8f8f8; border: 1px solid #d0d0d0; padding: 4px 8px;")
        self.count_label.setStyleSheet("color: #4a7a9a; font-weight: bold; font-size: 13px; background-color: transparent;")
        self.status_text.setStyleSheet("color: #666666; font-size: 12px; background-color: transparent;")
        self.button_frame.setStyleSheet("background-color: #f8f8f8; border: 1px solid #d0d0d0; padding: 6px;")
        self.dark_mode_btn.setText("Dark Mode")

    def apply_dark_mode(self):
        self.is_dark_mode = True
        self.save_settings()
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #e0e0e0; }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                color: #e0e0e0;
            }
            QListWidget::item { border-bottom: 1px solid #3a3a3a; color: #e0e0e0; }
            QListWidget::item:selected { background-color: #4a7a9a; color: #ffffff; }
            QListWidget::item:hover:!selected { background-color: #3a3a3a; }
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
            }
            QPushButton:hover { background-color: #4a4a4a; border: 1px solid #4a7a9a; }
            QPushButton:pressed { background-color: #2a2a2a; border: 1px solid #3a6a8a; }
            QPushButton:disabled { background-color: #2a2a2a; color: #666666; }
            QFrame { background-color: #1e1e1e; border: 1px solid #3a3a3a; }
            QFrame#header { border: none; }
            QProgressBar { border: 1px solid #3a3a3a; background-color: #2d2d2d; color: #e0e0e0; }
            QProgressBar::chunk { background-color: #4a7a9a; }
        """)
        self.count_frame.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3a3a3a; padding: 4px 8px;")
        self.count_label.setStyleSheet("color: #4a7a9a; font-weight: bold; font-size: 13px; background-color: transparent;")
        self.status_text.setStyleSheet("color: #888888; font-size: 12px; background-color: transparent;")
        self.button_frame.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3a3a3a; padding: 6px;")
        self.dark_mode_btn.setText("Light Mode")

    def toggle_dark_mode(self):
        if self.is_dark_mode:
            self.apply_light_mode()
        else:
            self.apply_dark_mode()

    def load_channels(self):
        self.channel_list.clear()
        channels_path = Path("channels")
        if not channels_path.exists():
            self.count_label.setText("Channels: 0")
            self.status_text.setText("No channels folder found")
            return

        logos_path = Path("logos")
        found = 0
        for channel_dir in channels_path.iterdir():
            if not channel_dir.is_dir():
                continue
            channel_name = channel_dir.name
            found += 1

            item = QListWidgetItem()
            logo_file = None
            for ext in ['.png', '.jpg', '.jpeg', '.svg']:
                candidate = logos_path / f"{channel_name}{ext}"
                if candidate.exists():
                    logo_file = candidate
                    break
            if logo_file:
                pixmap = QPixmap(str(logo_file))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon = QIcon(scaled_pixmap)
                    item.setIcon(icon)
                    item.setSizeHint(QSize(160, 160))
                else:
                    item.setSizeHint(QSize(60, 40))
            else:
                item.setSizeHint(QSize(60, 40))
            item.setText(channel_name)
            item.setData(Qt.UserRole, channel_name)
            self.channel_list.addItem(item)

        self.count_label.setText(f"Channels: {found}")
        if found > 0:
            self.status_text.setText("Ready")
        else:
            self.status_text.setText("No channels found")
        self.channel_list.itemDoubleClicked.connect(self.launch_channel)

    def toggle_view(self):
        self.is_grid_view = not self.is_grid_view
        if self.is_grid_view:
            self.apply_grid_view()
            self.toggle_view_btn.setText("List View")
        else:
            self.apply_list_view()
            self.toggle_view_btn.setText("Grid View")
        self.save_settings()

    def apply_grid_view(self):
        self.channel_list.setFlow(QListView.LeftToRight)
        self.channel_list.setWrapping(True)
        self.channel_list.setIconSize(QSize(180, 180))
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            item.setSizeHint(QSize(200, 200))

    def apply_list_view(self):
        self.channel_list.setFlow(QListView.TopToBottom)
        self.channel_list.setWrapping(False)
        self.channel_list.setIconSize(QSize(150, 150))
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            item.setSizeHint(QSize(160, 160))

    def launch_selected(self):
        current = self.channel_list.currentItem()
        if current:
            self.launch_channel(current)

    def launch_channel(self, item):
        channel_name = item.data(Qt.UserRole)
        if not channel_name:
            return

        cmd = f"nohup python3 tv_emulator.py {channel_name} > /dev/null 2>&1 &"
        os.system(cmd)
        self.status_text.setText(f"Launching: {channel_name}")
        QMessageBox.information(self, "Channel Launched",
            f"Channel '{channel_name}' started.\nPress ESC in mpv to quit.\nUse 'pkill -f tv_emulator.py' to kill.")
        QTimer.singleShot(3000, lambda: self.status_text.setText("Ready"))

    def open_channel_manager(self):
        if CHANNEL_MANAGER_AVAILABLE:
            self.manager = ChannelManager(parent=None, dark_mode=self.is_dark_mode)
            self.manager.channels_updated.connect(self.load_channels)
            self.manager.show()
            self.manager.raise_()
        else:
            QMessageBox.warning(self, "Not Available", "Channel Manager is not installed.")


def main():
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.Text, QColor(51, 51, 51))
    palette.setColor(QPalette.Button, QColor(232, 232, 232))
    palette.setColor(QPalette.ButtonText, QColor(51, 51, 51))
    palette.setColor(QPalette.Highlight, QColor(74, 122, 154))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = TVLauncher()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
