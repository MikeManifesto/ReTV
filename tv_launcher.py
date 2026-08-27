#!/usr/bin/env python3
"""
TV Launcher – Clean theme with dark/light mode toggle.
Settings page with dark mode toggle.
No selection effects – items are not selectable.
"""

import sys
import os
import json
import subprocess
import re
import webbrowser
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QMessageBox, QLabel,
    QFrame, QProgressBar, QListView, QTabWidget, QLineEdit,
    QDialog, QCheckBox
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor

try:
    from channel_manager_gui import ChannelManager
    CHANNEL_MANAGER_AVAILABLE = True
except ImportError:
    CHANNEL_MANAGER_AVAILABLE = False


# ---------------------------------------------------------------------------
# Settings Dialog
# ---------------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 200)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.dark_mode_check = QCheckBox("Dark Mode")
        self.dark_mode_check.setChecked(parent.is_dark_mode if parent else False)
        self.dark_mode_check.stateChanged.connect(self.toggle_dark_mode)
        self.dark_mode_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        layout.addWidget(self.dark_mode_check)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(30)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        if parent and parent.is_dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def toggle_dark_mode(self, state):
        if self.parent:
            if state == Qt.Checked:
                self.parent.apply_dark_mode()
            else:
                self.parent.apply_light_mode()

    def apply_light_mode(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333333;
            }
            QCheckBox {
                color: #333333;
            }
            QPushButton {
                background-color: #e8e8e8;
                color: #333333;
                border: 1px solid #c0c0c0;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
                border: 1px solid #4a7a9a;
            }
        """)

    def apply_dark_mode(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #e0e0e0;
            }
            QCheckBox {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #4a7a9a;
            }
        """)


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class TVLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TV Channel Launcher")
        self.setMinimumSize(900, 650)

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

        # --- Status bar (with controls) ---
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet("background-color: #f8f8f8; border: 1px solid #d0d0d0; padding: 4px 8px;")
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(8, 4, 8, 4)

        self.count_label = QLabel("Channels: 0")
        self.count_label.setStyleSheet("color: #4a7a9a; font-weight: bold; font-size: 13px; background-color: transparent;")
        status_layout.addWidget(self.count_label)

        status_layout.addStretch()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
                border: 1px solid #4a7a9a;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_channels)
        status_layout.addWidget(self.refresh_btn)

        self.toggle_view_btn = QPushButton("Grid View" if not self.is_grid_view else "List View")
        self.toggle_view_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
                border: 1px solid #4a7a9a;
            }
        """)
        self.toggle_view_btn.clicked.connect(self.toggle_view)
        status_layout.addWidget(self.toggle_view_btn)

        self.main_layout.addWidget(self.status_frame)

        # --- Tabs ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
            }
            QTabBar::tab {
                padding: 6px 12px;
                background-color: #e0e0e0;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #f8f8f8;
                border-bottom: 1px solid #f8f8f8;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
        """)
        self.main_layout.addWidget(self.tab_widget)

        # ---- Channels Tab ----
        channels_tab = QWidget()
        channels_layout = QVBoxLayout(channels_tab)
        channels_layout.setContentsMargins(0, 0, 0, 0)

        self.channel_list = QListWidget()
        self.channel_list.setFlow(QListView.TopToBottom)
        self.channel_list.setWrapping(False)
        self.channel_list.setIconSize(QSize(150, 150))
        # No selection – no visual feedback
        self.channel_list.setSelectionMode(QListWidget.NoSelection)
        self.channel_list.setFocusPolicy(Qt.NoFocus)  # also remove focus rectangle
        channels_layout.addWidget(self.channel_list)

        # Button frame
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

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_btn)

        button_layout.addStretch()

        channels_layout.addWidget(self.button_frame)

        self.tab_widget.addTab(channels_tab, "Channels")

        # ---- Twitch Tab ----
        twitch_tab = QWidget()
        twitch_layout = QVBoxLayout(twitch_tab)
        twitch_layout.setContentsMargins(10, 10, 10, 10)
        twitch_layout.setSpacing(8)

        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        self.twitch_input = QLineEdit()
        self.twitch_input.setPlaceholderText("Enter Twitch channel name or URL (e.g., twitch.tv/username)")
        self.twitch_input.setMinimumHeight(30)
        add_row.addWidget(self.twitch_input)

        self.add_twitch_btn = QPushButton("Add Channel")
        self.add_twitch_btn.setMinimumHeight(30)
        self.add_twitch_btn.clicked.connect(self.add_twitch_channel)
        add_row.addWidget(self.add_twitch_btn)

        twitch_layout.addLayout(add_row)

        self.twitch_list = QListWidget()
        self.twitch_list.setMinimumHeight(200)
        self.twitch_list.itemDoubleClicked.connect(self.launch_twitch_stream)
        twitch_layout.addWidget(self.twitch_list)

        self.tab_widget.addTab(twitch_tab, "Twitch")

        # --- Apply mode and view ---
        if self.is_dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

        self.load_channels()
        self.load_twitch_channels()

        if self.is_grid_view:
            self.apply_grid_view()
            self.toggle_view_btn.setText("List View")
        else:
            self.apply_list_view()
            self.toggle_view_btn.setText("Grid View")

    # -------------------------------------------------------------------------
    # Header setup
    # -------------------------------------------------------------------------
    def setup_header(self):
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

    # -------------------------------------------------------------------------
    # Settings
    # -------------------------------------------------------------------------
    def load_settings(self):
        self.is_dark_mode = False
        self.is_grid_view = False
        self.twitch_channels = []
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.is_dark_mode = data.get('dark_mode', False)
                    self.is_grid_view = data.get('grid_view', False)
                    self.twitch_channels = data.get('twitch_channels', [])
        except:
            pass

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump({
                    'dark_mode': self.is_dark_mode,
                    'grid_view': self.is_grid_view,
                    'twitch_channels': self.twitch_channels
                }, f)
        except:
            pass

    # -------------------------------------------------------------------------
    # Dark/Light mode
    # -------------------------------------------------------------------------
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
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border: none;
            }
            QListWidget::item:hover {
                background-color: #e8eef0;
            }
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
            QTabWidget::pane {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                color: #333333;
                padding: 6px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #f8f8f8;
                border-bottom: 1px solid #f8f8f8;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            QLineEdit { background-color: #ffffff; border: 1px solid #d0d0d0; color: #333333; }
            QCheckBox { color: #333333; }
        """)
        self.status_frame.setStyleSheet("background-color: #f8f8f8; border: 1px solid #d0d0d0; padding: 4px 8px;")
        self.count_label.setStyleSheet("color: #4a7a9a; font-weight: bold; font-size: 13px; background-color: transparent;")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
                border: 1px solid #4a7a9a;
            }
        """)
        self.toggle_view_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
                border: 1px solid #4a7a9a;
            }
        """)
        self.button_frame.setStyleSheet("background-color: #f8f8f8; border: 1px solid #d0d0d0; padding: 6px;")

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
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border: none;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
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
            QTabWidget::pane {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                border: 1px solid #3a3a3a;
                border-bottom: none;
                color: #e0e0e0;
                padding: 6px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                border-bottom: 1px solid #2d2d2d;
            }
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
            QLineEdit { background-color: #2d2d2d; border: 1px solid #3a3a3a; color: #e0e0e0; }
            QCheckBox { color: #e0e0e0; }
        """)
        self.status_frame.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3a3a3a; padding: 4px 8px;")
        self.count_label.setStyleSheet("color: #4a7a9a; font-weight: bold; font-size: 13px; background-color: transparent;")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #4a7a9a;
            }
        """)
        self.toggle_view_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #4a7a9a;
            }
        """)
        self.button_frame.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3a3a3a; padding: 6px;")

    def toggle_dark_mode(self):
        if self.is_dark_mode:
            self.apply_light_mode()
        else:
            self.apply_dark_mode()

    # -------------------------------------------------------------------------
    # Channels Tab
    # -------------------------------------------------------------------------
    def load_channels(self):
        self.channel_list.clear()
        channels_path = Path("channels")
        if not channels_path.exists():
            self.count_label.setText("Channels: 0")
            return

        logos_path = Path("logos")
        found = 0
        for channel_dir in channels_path.iterdir():
            if not channel_dir.is_dir():
                continue
            channel_name = channel_dir.name
            found += 1

            item = QListWidgetItem()
            item.setData(Qt.UserRole, channel_name)  # store name
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
            # Set text based on current view mode
            if self.is_grid_view:
                item.setText("")
            else:
                item.setText(channel_name)
                font = item.font()
                font.setBold(True)
                font.setPointSize(14)
                item.setFont(font)
            self.channel_list.addItem(item)

        self.count_label.setText(f"Channels: {found}")

        # Connect double-click signal
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
        # Update item texts and font for all items
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            channel_name = item.data(Qt.UserRole)
            if self.is_grid_view:
                item.setText("")
            else:
                item.setText(channel_name)
                font = item.font()
                font.setBold(True)
                font.setPointSize(14)
                item.setFont(font)

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

    def launch_channel(self, item):
        channel_name = item.data(Qt.UserRole)
        if not channel_name:
            return

        cmd = f"nohup python3 tv_emulator.py {channel_name} > /dev/null 2>&1 &"
        os.system(cmd)
        # No visual feedback, no selection

    def open_channel_manager(self):
        if CHANNEL_MANAGER_AVAILABLE:
            self.manager = ChannelManager(parent=None, dark_mode=self.is_dark_mode)
            self.manager.channels_updated.connect(self.load_channels)
            self.manager.show()
            self.manager.raise_()
        else:
            QMessageBox.warning(self, "Not Available", "Channel Manager is not installed.")

    def open_settings(self):
        settings = SettingsDialog(self)
        settings.exec_()

    # -------------------------------------------------------------------------
    # Twitch Tab
    # -------------------------------------------------------------------------
    def add_twitch_channel(self):
        text = self.twitch_input.text().strip()
        if not text:
            return
        if "twitch.tv/" in text:
            match = re.search(r'twitch\.tv/([^/?]+)', text)
            if match:
                channel_name = match.group(1)
            else:
                channel_name = text
        else:
            channel_name = text
        channel_name = channel_name.strip().lower()
        if not channel_name:
            return
        if channel_name in self.twitch_channels:
            QMessageBox.information(self, "Already Added", f"'{channel_name}' is already in your list.")
            return
        self.twitch_channels.append(channel_name)
        self.save_settings()
        self.load_twitch_channels()
        self.twitch_input.clear()

    def load_twitch_channels(self):
        self.twitch_list.clear()
        for channel in self.twitch_channels:
            item = QListWidgetItem(channel)
            self.twitch_list.addItem(item)

    def launch_twitch_stream(self, item):
        channel = item.text()
        try:
            result = subprocess.run(
                ["streamlink", f"twitch.tv/{channel}", "best", "--stream-url"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                QMessageBox.warning(self, "Stream Error", f"Could not fetch stream for '{channel}'.\n{result.stderr}")
                return
            stream_url = result.stdout.strip()
            if not stream_url:
                QMessageBox.warning(self, "Stream Error", f"No stream available for '{channel}'.")
                return
            subprocess.Popen(["mpv", "--fullscreen", stream_url])
            self.open_chat_window(channel)
        except FileNotFoundError:
            QMessageBox.warning(self, "Missing Dependency",
                "streamlink is not installed.\nInstall it with:\n"
                "  sudo pacman -S streamlink  (Arch)\n"
                "  sudo apt install streamlink  (Debian/Ubuntu)\n"
                "  sudo dnf install streamlink  (Fedora)")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def open_chat_window(self, channel):
        webbrowser.open(f"https://www.twitch.tv/{channel}/chat")


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
