from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap

class App:
    def __init__(self, central_widget):
        self.central_widget = central_widget
        self.drag_position = QPoint()
        self.active_button = None
        self.current_section = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title Bar
        self.title_bar = QFrame()
        self.title_bar.setStyleSheet("background-color: #1DB954;")
        self.title_bar.setFixedHeight(40)
        self.title_bar_layout = QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Music Recommendation System")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        self.title_bar_layout.addWidget(title_label)
        self.title_bar_layout.addStretch()

        self.minimize_button = QPushButton("−")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("""
            QPushButton { background-color: #2A2A2A; color: #FFFFFF; border-radius: 5px; font-size: 14px; }
            QPushButton:hover { background-color: #17a34a; }
        """)
        self.title_bar_layout.addWidget(self.minimize_button)

        self.toggle_size_button = QPushButton("⬜")
        self.toggle_size_button.setFixedSize(30, 30)
        self.toggle_size_button.setStyleSheet("""
            QPushButton { background-color: #2A2A2A; color: #FFFFFF; border-radius: 5px; font-size: 14px; }
            QPushButton:hover { background-color: #17a34a; }
        """)
        self.title_bar_layout.addWidget(self.toggle_size_button)

        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton { background-color: #2A2A2A; color: #FFFFFF; border-radius: 5px; font-size: 14px; }
            QPushButton:hover { background-color: #ff5555; }
        """)
        self.title_bar_layout.addWidget(self.close_button)

        main_layout.addWidget(self.title_bar)

        # Main Content with Sidebar
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSpacing(5)

        sidebar_title = QLabel("Menu")
        sidebar_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; padding: 10px;")
        sidebar.addWidget(sidebar_title)

        self.recommend_button = QPushButton("Recommendations")
        self.recommend_button.setStyleSheet("""
            QPushButton { font-size: 14px; color: #FFFFFF; background-color: #1DB954; padding: 10px; border: none; }
            QPushButton:hover { background-color: #17a34a; }
            QPushButton:default { background-color: #1DB954; }
        """)
        self.recommend_button.clicked.connect(lambda: self.set_active_button(self.recommend_button))
        sidebar.addWidget(self.recommend_button)

        self.catalog_button = QPushButton("Catalog")
        self.catalog_button.setStyleSheet("""
            QPushButton { font-size: 14px; color: #FFFFFF; background-color: #2A2A2A; padding: 10px; border: none; }
            QPushButton:hover { background-color: #333; }
        """)
        self.catalog_button.clicked.connect(lambda: self.set_active_button(self.catalog_button))
        sidebar.addWidget(self.catalog_button)

        self.trends_button = QPushButton("Trends")
        self.trends_button.setStyleSheet("""
            QPushButton { font-size: 14px; color: #FFFFFF; background-color: #2A2A2A; padding: 10px; border: none; }
            QPushButton:hover { background-color: #333; }
        """)
        self.trends_button.clicked.connect(lambda: self.set_active_button(self.trends_button))
        sidebar.addWidget(self.trends_button)

        self.playlist_button = QPushButton("Playlist")
        self.playlist_button.setStyleSheet("""
            QPushButton { font-size: 14px; color: #FFFFFF; background-color: #2A2A2A; padding: 10px; border: none; }
            QPushButton:hover { background-color: #333; }
        """)
        self.playlist_button.clicked.connect(lambda: self.set_active_button(self.playlist_button))
        sidebar.addWidget(self.playlist_button)

        sidebar.addStretch()

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("background-color: #121212;")
        content_layout.addWidget(sidebar_widget)

        # Main Content Area
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setStyleSheet("""
            QScrollArea { border: 2px solid #1DB954; border-radius: 5px; background-color: #2A2A2A; }
            QScrollBar:vertical { width: 10px; background: #333; }
            QScrollBar::handle:vertical { background: #1DB954; border-radius: 5px; min-height: 20px; }
        """)
        self.content_container = QWidget()
        self.content_grid = QGridLayout(self.content_container)
        self.content_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_grid.setSpacing(15)
        self.content_area.setWidget(self.content_container)
        content_layout.addWidget(self.content_area)

        main_layout.addLayout(content_layout)

        self.central_widget.setStyleSheet("background-color: #121212;")
        self.title_bar.mousePressEvent = self.start_drag
        self.title_bar.mouseMoveEvent = self.drag_window

    def start_drag(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.central_widget.mapToGlobal(self.central_widget.rect().topLeft())

    def drag_window(self, event):
        if not self.drag_position.isNull():
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.central_widget.window().move(new_pos)

    def clear_content(self):
        for i in reversed(range(self.content_grid.count())):
            widget = self.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def set_active_button(self, button):
        if self.active_button:
            self.active_button.setStyleSheet(self.active_button.styleSheet().replace("#1DB954", "#2A2A2A"))
        self.active_button = button
        button.setStyleSheet(button.styleSheet().replace("#2A2A2A", "#1DB954"))

    def get_content_width(self):
        return self.content_area.width() - 30  # Subtract padding

    def set_current_section(self, section):
        self.current_section = section

    def resizeEvent(self, event):
        if self.current_section:
            self.current_section()