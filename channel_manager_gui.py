#!/usr/bin/env python3
"""
Channel Manager GUI – Clean layout, no overlapping.
Inherits dark/light mode from launcher.
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QGridLayout,
    QListWidget, QListWidgetItem, QWidget, QTabWidget,
    QTextEdit, QFrame, QProgressBar, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPalette, QColor, QPixmap, QIcon

try:
    from create_channel import create_channel
    CREATOR_AVAILABLE = True
except ImportError:
    CREATOR_AVAILABLE = False


class ChannelManager(QDialog):
    channels_updated = pyqtSignal()

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Channel Manager")
        self.setMinimumSize(750, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.is_dark_mode = dark_mode

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Header ---
        self.header = QFrame()
        self.header.setObjectName("header")
        self.header.setStyleSheet("QFrame#header { border: none; background-color: #4a7a9a; }")
        self.setup_header()
        layout.addWidget(self.header)

        # --- Tabs ---
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tabs)

        # ---- Create Channel Tab ----
        create_tab = QWidget()
        create_layout = QVBoxLayout(create_tab)
        create_layout.setSpacing(12)
        create_layout.setContentsMargins(15, 15, 15, 15)
        create_tab.setLayout(create_layout)

        form_group = QGroupBox("Create New Channel")
        form_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        grid = QGridLayout(form_group)
        grid.setSpacing(10)
        grid.setVerticalSpacing(8)
        grid.setContentsMargins(15, 15, 15, 15)

        # Row 0: Channel Name
        label1 = QLabel("Channel Name:")
        label1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label1.setMinimumWidth(100)
        grid.addWidget(label1, 0, 0)

        self.channel_name_input = QLineEdit()
        self.channel_name_input.setPlaceholderText("e.g., nickelodeon")
        self.channel_name_input.setMinimumHeight(32)
        grid.addWidget(self.channel_name_input, 0, 1)

        # Row 1: Block Name
        label2 = QLabel("Block Name:")
        label2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label2.setMinimumWidth(100)
        grid.addWidget(label2, 1, 0)

        self.block_name_input = QLineEdit()
        self.block_name_input.setPlaceholderText("e.g., primetime (default: default)")
        self.block_name_input.setMinimumHeight(32)
        grid.addWidget(self.block_name_input, 1, 1)

        # Row 2: Show Name
        label3 = QLabel("Show Name:")
        label3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label3.setMinimumWidth(100)
        grid.addWidget(label3, 2, 0)

        self.show_name_input = QLineEdit()
        self.show_name_input.setPlaceholderText("e.g., spongebob (default: show1)")
        self.show_name_input.setMinimumHeight(32)
        grid.addWidget(self.show_name_input, 2, 1)

        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        create_layout.addWidget(form_group)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.create_btn = QPushButton("Create Channel")
        self.create_btn.setMinimumHeight(36)
        self.create_btn.setMinimumWidth(150)
        self.create_btn.clicked.connect(self.create_channel)
        self.create_btn.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                padding: 8px 20px;
                background-color: #4a7a9a;
                color: #ffffff;
                border: 1px solid #3a6a8a;
            }
            QPushButton:hover {
                background-color: #5a8aaa;
                border: 1px solid #4a7a9a;
            }
        """)
        btn_row.addWidget(self.create_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(0)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setMinimumWidth(100)
        btn_row.addWidget(self.progress_bar)
        btn_row.addStretch()
        create_layout.addLayout(btn_row)

        self.create_status = QTextEdit()
        self.create_status.setReadOnly(True)
        self.create_status.setMaximumHeight(100)
        self.create_status.setMinimumHeight(50)
        create_layout.addWidget(self.create_status)

        if not CREATOR_AVAILABLE:
            self.create_status.append("WARNING: create_channel.py not found.")
            self.create_btn.setEnabled(False)

        self.tabs.addTab(create_tab, "Create Channel")

        # ---- View Channels Tab ----
        view_tab = QWidget()
        view_layout = QVBoxLayout(view_tab)
        view_layout.setSpacing(8)
        view_layout.setContentsMargins(10, 10, 10, 10)
        view_tab.setLayout(view_layout)

        refresh_btn = QPushButton("Refresh List")
        refresh_btn.setMinimumHeight(30)
        refresh_btn.clicked.connect(self.refresh_channel_list)
        view_layout.addWidget(refresh_btn)

        self.channel_view_list = QListWidget()
        self.channel_view_list.setIconSize(QSize(75, 75))
        self.channel_view_list.setMinimumHeight(150)
        self.channel_view_list.itemClicked.connect(self.show_channel_info)
        view_layout.addWidget(self.channel_view_list)

        info_group = QGroupBox("Channel Info")
        info_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        info_layout = QVBoxLayout(info_group)
        self.channel_info = QTextEdit()
        self.channel_info.setReadOnly(True)
        self.channel_info.setMaximumHeight(150)
        self.channel_info.setMinimumHeight(80)
        info_layout.addWidget(self.channel_info)
        view_layout.addWidget(info_group)

        self.tabs.addTab(view_tab, "View Channels")

        # --- Apply mode ---
        if self.is_dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

        self.refresh_channel_list()

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
                initial_width = self.width() if self.width() > 0 else 750
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

    def apply_light_mode(self):
        self.setStyleSheet("""
            QDialog { background-color: #f0f0f0; }
            QLabel { color: #333333; }
            QGroupBox { color: #4a7a9a; border: 1px solid #d0d0d0; }
            QGroupBox::title { color: #4a7a9a; }
            QLineEdit { background-color: #ffffff; color: #333333; border: 1px solid #d0d0d0; }
            QLineEdit:focus { border: 1px solid #4a7a9a; }
            QListWidget { background-color: #ffffff; color: #333333; border: 1px solid #d0d0d0; }
            QListWidget::item { border-bottom: 1px solid #e8e8e8; color: #333333; }
            QListWidget::item:selected { background-color: #4a7a9a; color: #ffffff; }
            QListWidget::item:hover:!selected { background-color: #e8eef0; }
            QPushButton { background-color: #e8e8e8; color: #333333; border: 1px solid #c0c0c0; }
            QPushButton:hover { background-color: #d8d8d8; border: 1px solid #4a7a9a; }
            QPushButton:pressed { background-color: #c8c8c8; border: 1px solid #3a6a8a; }
            QPushButton:disabled { background-color: #f0f0f0; color: #aaaaaa; }
            QTabWidget::pane { background-color: #ffffff; border: 1px solid #d0d0d0; }
            QTabBar::tab { background-color: #e8e8e8; color: #333333; border: 1px solid #d0d0d0; }
            QTabBar::tab:selected { background-color: #ffffff; color: #4a7a9a; }
            QTabBar::tab:hover { background-color: #d8d8d8; }
            QTextEdit { background-color: #ffffff; color: #333333; border: 1px solid #d0d0d0; }
            QFrame { background-color: #f0f0f0; border: 1px solid #d0d0d0; }
            QFrame#header { border: none; background-color: #4a7a9a; }
            QProgressBar { border: 1px solid #c0c0c0; background-color: #ffffff; color: #333333; }
            QProgressBar::chunk { background-color: #4a7a9a; }
        """)

    def apply_dark_mode(self):
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; }
            QLabel { color: #e0e0e0; }
            QGroupBox { color: #4a7a9a; border: 1px solid #3a3a3a; }
            QGroupBox::title { color: #4a7a9a; }
            QLineEdit { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #3a3a3a; }
            QLineEdit:focus { border: 1px solid #4a7a9a; }
            QListWidget { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #3a3a3a; }
            QListWidget::item { border-bottom: 1px solid #3a3a3a; color: #e0e0e0; }
            QListWidget::item:selected { background-color: #4a7a9a; color: #ffffff; }
            QListWidget::item:hover:!selected { background-color: #3a3a3a; }
            QPushButton { background-color: #3a3a3a; color: #e0e0e0; border: 1px solid #4a4a4a; }
            QPushButton:hover { background-color: #4a4a4a; border: 1px solid #4a7a9a; }
            QPushButton:pressed { background-color: #2a2a2a; border: 1px solid #3a6a8a; }
            QPushButton:disabled { background-color: #2a2a2a; color: #666666; }
            QTabWidget::pane { background-color: #2d2d2d; border: 1px solid #3a3a3a; }
            QTabBar::tab { background-color: #3a3a3a; color: #e0e0e0; border: 1px solid #3a3a3a; }
            QTabBar::tab:selected { background-color: #2d2d2d; color: #4a7a9a; }
            QTabBar::tab:hover { background-color: #4a4a4a; }
            QTextEdit { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #3a3a3a; }
            QFrame { background-color: #1e1e1e; border: 1px solid #3a3a3a; }
            QFrame#header { border: none; background-color: #4a7a9a; }
            QProgressBar { border: 1px solid #3a3a3a; background-color: #2d2d2d; color: #e0e0e0; }
            QProgressBar::chunk { background-color: #4a7a9a; }
        """)

    def refresh_channel_list(self):
        self.channel_view_list.clear()
        channels_path = Path("channels")
        if not channels_path.exists():
            self.channel_info.setText("No channels folder found.")
            return

        logos_path = Path("logos")
        for channel_dir in channels_path.iterdir():
            if not channel_dir.is_dir():
                continue
            channel_name = channel_dir.name
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
                    scaled_pixmap = pixmap.scaled(75, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon = QIcon(scaled_pixmap)
                    item.setIcon(icon)
                    item.setSizeHint(QSize(85, 85))
                else:
                    item.setSizeHint(QSize(60, 40))
            else:
                item.setSizeHint(QSize(60, 40))
            item.setText(channel_name)
            self.channel_view_list.addItem(item)

        if self.channel_view_list.count() == 0:
            self.channel_info.setText("No channels found.")
        else:
            self.channel_view_list.setCurrentRow(0)
            self.show_channel_info(self.channel_view_list.item(0))

    def create_channel(self):
        if not CREATOR_AVAILABLE:
            QMessageBox.warning(self, "Error", "create_channel.py not found.")
            return

        channel_name = self.channel_name_input.text().strip()
        if not channel_name:
            QMessageBox.warning(self, "Error", "Channel name is required.")
            return

        block_name = self.block_name_input.text().strip()
        if not block_name:
            block_name = "default"

        show_name = self.show_name_input.text().strip()
        if not show_name:
            show_name = "show1"

        self.create_status.clear()
        self.create_status.append(f"Creating channel '{channel_name}'...")
        self.create_btn.setEnabled(False)
        self.progress_bar.setVisible(True)

        success = create_channel(channel_name, block_name, show_name)

        self.progress_bar.setVisible(False)
        self.create_btn.setEnabled(True)

        if success:
            self.create_status.append("\nChannel created successfully!")
            self.channel_name_input.clear()
            self.block_name_input.clear()
            self.show_name_input.clear()
            self.refresh_channel_list()
            self.channels_updated.emit()
        else:
            self.create_status.append("\nFailed to create channel.")

    def show_channel_info(self, item):
        channel_name = item.text()
        channel_path = Path("channels") / channel_name

        info = f"CHANNEL: {channel_name}\n"
        info += "=" * 50 + "\n\n"

        blocks_path = channel_path / "blocks"
        if blocks_path.exists():
            info += "BLOCKS:\n"
            for block_dir in blocks_path.iterdir():
                if block_dir.is_dir():
                    info += f"  - {block_dir.name}\n"
                    schedule_file = block_dir / "schedule.json"
                    if schedule_file.exists():
                        info += f"    schedule.json found\n"
                    order_file = block_dir / "order.json"
                    if order_file.exists():
                        info += f"    order.json found\n"
                    shows_path = block_dir / "shows"
                    if shows_path.exists():
                        shows = [d.name for d in shows_path.iterdir() if d.is_dir()]
                        if shows:
                            info += f"    SHOWS: {', '.join(shows)}\n"
        else:
            info += "No blocks found.\n"

        self.channel_info.setText(info)


def main():
    from PyQt5.QtWidgets import QApplication
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

    window = ChannelManager()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
