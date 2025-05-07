from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap
import sys

class App:
    def __init__(self, central_widget):
        self.central_widget = central_widget
        self.drag_position = QPoint()
        self.active_button = None
        self.is_dark_mode = True  # Start in dark mode
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Apply initial dark mode stylesheet
        self.apply_stylesheet()

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

        # Dark Mode Toggle Button
        self.theme_toggle_button = QPushButton("🌙")
        self.theme_toggle_button.setFixedSize(30, 30)
        self.theme_toggle_button.setStyleSheet("""
            QPushButton { 
                background-color: %s; 
                color: %s; 
                border-radius: 5px; 
                font-size: 14px; 
            }
            QPushButton:hover { 
                background-color: #17a34a; 
            }
        """ % (self.get_theme_colors()['bg-secondary'], self.get_theme_colors()['text-primary']))
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        self.title_bar_layout.addWidget(self.theme_toggle_button)

        self.minimize_button = QPushButton("−")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("""
            QPushButton { 
                background-color: %s; 
                color: %s; 
                border-radius: 5px; 
                font-size: 14px; 
            }
            QPushButton:hover { 
                background-color: #17a34a; 
            }
        """ % (self.get_theme_colors()['bg-secondary'], self.get_theme_colors()['text-primary']))
        self.title_bar_layout.addWidget(self.minimize_button)

        self.toggle_size_button = QPushButton("⬜")
        self.toggle_size_button.setFixedSize(30, 30)
        self.toggle_size_button.setStyleSheet("""
            QPushButton { 
                background-color: %s; 
                color: %s; 
                border-radius: 5px; 
                font-size: 14px; 
            }
            QPushButton:hover { 
                background-color: #17a34a; 
            }
        """ % (self.get_theme_colors()['bg-secondary'], self.get_theme_colors()['text-primary']))
        self.title_bar_layout.addWidget(self.toggle_size_button)

        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton { 
                background-color: %s; 
                color: %s; 
                border-radius: 5px; 
                font-size: 14px; 
            }
            QPushButton:hover { 
                background-color: #ff5555; 
            }
        """ % (self.get_theme_colors()['bg-secondary'], self.get_theme_colors()['text-primary']))
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

        self.sidebar_title = QLabel("Menu")
        self.sidebar_title.setStyleSheet("font-size: 18px; font-weight: bold; color: %s;" % self.get_theme_colors()['text-primary'])
        sidebar.addWidget(self.sidebar_title)

        # Recommendations Button with Icon
        self.recommend_button = QPushButton("🎵 Recommendations")
        self.recommend_button.setStyleSheet("""
            QPushButton { 
                font-size: 14px; 
                color: %s; 
                background-color: %s; 
                padding: 10px; 
                border: none; 
                text-align: left; 
            }
            QPushButton:hover { 
                background-color: #333; 
            }
            QPushButton[active="true"] { 
                background-color: #1DB954; 
                color: %s; 
            }
        """ % (self.get_theme_colors()['text-primary'], self.get_theme_colors()['bg-secondary'], self.get_theme_colors()['text-primary']))
        self.recommend_button.setProperty("active", False)
        self.recommend_button.clicked.connect(lambda: self.set_active_button(self.recommend_button))
        sidebar.addWidget(self.recommend_button)

        # Catalog Button with Icon
        self.catalog_button = QPushButton("📚 Catalog")
        self.catalog_button.setStyleSheet("""
            QPushButton { 
                font-size: 14px; 
                color: %s; 
                background-color: %s; 
                padding: 10px; 
                border: none; 
                text-align: left; 
            }
            QPushButton:hover { 
                background-color: #333; 
            }
            QPushButton[active="true"] { 
                background-color: #1DB954; 
                color: %s; 
            }
        """ % (self.get_theme_colors()['text-primary'], self.get_theme_colors()['bg-secondary'], self.get_theme_colors()['text-primary']))
        self.catalog_button.setProperty("active", False)
        self.catalog_button.clicked.connect(lambda: self.set_active_button(self.catalog_button))
        sidebar.addWidget(self.catalog_button)

        # Trends Button with Icon
        self.trends_button = QPushButton("📈 Trends")
        self.trends_button.setStyleSheet("""
            QPushButton { 
                font-size: 14px; 
                color: %s; 
                background-color: %s; 
                padding: 10px; 
                border: none; 
                text-align: left; 
            }
            QPushButton:hover { 
                background-color: #333; 
            }
            QPushButton[active="true"] { 
                background-color: #1DB954; 
                color: %s; 
            }
        """ % (self.get_theme_colors()['text-primary'], self.get_theme_colors()['bg-secondary'], self.get_theme_colors()['text-primary']))
        self.trends_button.setProperty("active", False)
        self.trends_button.clicked.connect(lambda: self.set_active_button(self.trends_button))
        sidebar.addWidget(self.trends_button)

        # Playlist Button with Icon
        self.playlist_button = QPushButton("🎧 Playlist")
        self.playlist_button.setStyleSheet("""
            QPushButton { 
                font-size: 14px; 
                color: %s; 
                background-color: %s; 
                padding: 10px; 
                border: none; 
                text-align: left; 
            }
            QPushButton:hover { 
                background-color: #333; 
            }
            QPushButton[active="true"] { 
                background-color: #1DB954; 
                color: %s; 
            }
        """ % (self.get_theme_colors()['text-primary'], self.get_theme_colors()['bg-secondary'], self.get_theme_colors()['text-primary']))
        self.playlist_button.setProperty("active", False)
        self.playlist_button.clicked.connect(lambda: self.set_active_button(self.playlist_button))
        sidebar.addWidget(self.playlist_button)

        sidebar.addStretch()

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(sidebar)
        self.sidebar_widget.setFixedWidth(200)
        self.sidebar_widget.setStyleSheet("background-color: %s;" % self.get_theme_colors()['bg-secondary'])
        content_layout.addWidget(self.sidebar_widget)

        # Main Content Area
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setStyleSheet("""
            QScrollArea { 
                border: 2px solid #1DB954; 
                border-radius: 5px; 
                background-color: %s; 
            }
            QScrollBar:vertical { 
                width: 10px; 
                background: %s; 
            }
            QScrollBar::handle:vertical { 
                background: #1DB954; 
                border-radius: 5px; 
                min-height: 20px; 
            }
        """ % (self.get_theme_colors()['bg-secondary'], self.get_theme_colors()['scrollbar-bg']))
        self.content_container = QWidget()
        self.content_grid = QGridLayout(self.content_container)
        self.content_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_grid.setSpacing(15)
        self.content_area.setWidget(self.content_container)
        content_layout.addWidget(self.content_area)

        main_layout.addLayout(content_layout)

        self.title_bar.mousePressEvent = self.start_drag
        self.title_bar.mouseMoveEvent = self.drag_window

    def get_theme_colors(self):
        if self.is_dark_mode:
            return {
                'bg-primary': '#121212',
                'bg-secondary': '#2A2A2A',
                'text-primary': '#FFFFFF',
                'accent': '#1DB954',
                'accent-hover': '#17a34a',
                'scrollbar-bg': '#333',
                'scrollbar-handle': '#1DB954',
                'border': '#1DB954'
            }
        else:
            return {
                'bg-primary': '#FFFFFF',
                'bg-secondary': '#F5F5F5',
                'text-primary': '#000000',
                'accent': '#1DB954',
                'accent-hover': '#17a34a',
                'scrollbar-bg': '#CCCCCC',
                'scrollbar-handle': '#1DB954',
                'border': '#1DB954'
            }

    def apply_stylesheet(self):
        colors = self.get_theme_colors()
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: %s;
                color: %s !important;
            }
            QLabel {
                color: %s !important;
            }
            QPushButton {
                color: %s !important;
            }
        """ % (colors['bg-primary'], colors['text-primary'], colors['text-primary'], colors['text-primary']))

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
        if self.active_button and self.active_button != button:
            self.active_button.setProperty("active", False)
            self.active_button.setStyleSheet("""
                QPushButton { 
                    font-size: 14px; 
                    color: %s !important; 
                    background-color: %s; 
                    padding: 10px; 
                    border: none; 
                    text-align: left; 
                }
                QPushButton:hover { 
                    background-color: #333; 
                }
            """ % (self.get_theme_colors()['text-primary'], self.get_theme_colors()['bg-secondary']))
        self.active_button = button
        if button:
            button.setProperty("active", True)
            button.setStyleSheet("""
                QPushButton { 
                    font-size: 14px; 
                    color: %s !important; 
                    background-color: #1DB954; 
                    padding: 10px; 
                    border: none; 
                    text-align: left; 
                }
                QPushButton:hover { 
                    background-color: #17a34a; 
                }
            """ % self.get_theme_colors()['text-primary'])

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.theme_toggle_button.setText("🌙" if self.is_dark_mode else "☀️")
        
        # Apply new stylesheet
        self.apply_stylesheet()

        # Update individual widget styles
        colors = self.get_theme_colors()
        self.theme_toggle_button.setStyleSheet("""
            QPushButton { 
                background-color: %s; 
                color: %s !important; 
                border-radius: 5px; 
                font-size: 14px; 
            }
            QPushButton:hover { 
                background-color: #17a34a; 
            }
        """ % (colors['bg-secondary'], colors['text-primary']))
        self.minimize_button.setStyleSheet("""
            QPushButton { 
                background-color: %s; 
                color: %s !important; 
                border-radius: 5px; 
                font-size: 14px; 
            }
            QPushButton:hover { 
                background-color: #17a34a; 
            }
        """ % (colors['bg-secondary'], colors['text-primary']))
        self.toggle_size_button.setStyleSheet("""
            QPushButton { 
                background-color: %s; 
                color: %s !important; 
                border-radius: 5px; 
                font-size: 14px; 
            }
            QPushButton:hover { 
                background-color: #17a34a; 
            }
        """ % (colors['bg-secondary'], colors['text-primary']))
        self.close_button.setStyleSheet("""
            QPushButton { 
                background-color: %s; 
                color: %s !important; 
                border-radius: 5px; 
                font-size: 14px; 
            }
            QPushButton:hover { 
                background-color: #ff5555; 
            }
        """ % (colors['bg-secondary'], colors['text-primary']))
        self.sidebar_widget.setStyleSheet("background-color: %s;" % colors['bg-secondary'])
        self.content_area.setStyleSheet("""
            QScrollArea { 
                border: 2px solid #1DB954; 
                border-radius: 5px; 
                background-color: %s; 
            }
            QScrollBar:vertical { 
                width: 10px; 
                background: %s; 
            }
            QScrollBar::handle:vertical { 
                background: #1DB954; 
                border-radius: 5px; 
                min-height: 20px; 
            }
        """ % (colors['bg-secondary'], colors['scrollbar-bg']))
        self.sidebar_title.setStyleSheet("font-size: 18px; font-weight: bold; color: %s !important; padding: 10px;" % colors['text-primary'])

        # Explicitly update sidebar buttons with correct text color
        for button in [self.recommend_button, self.catalog_button, self.trends_button, self.playlist_button]:
            if button != self.active_button:
                button.setStyleSheet("""
                    QPushButton { 
                        font-size: 14px; 
                        color: %s !important; 
                        background-color: %s; 
                        padding: 10px; 
                        border: none; 
                        text-align: left; 
                    }
                    QPushButton:hover { 
                        background-color: #333; 
                    }
                """ % (colors['text-primary'], colors['bg-secondary']))
            else:
                button.setStyleSheet("""
                    QPushButton { 
                        font-size: 14px; 
                        color: %s !important; 
                        background-color: #1DB954; 
                        padding: 10px; 
                        border: none; 
                        text-align: left; 
                    }
                    QPushButton:hover { 
                        background-color: #17a34a; 
                    }
                """ % colors['text-primary'])

        # Force refresh for all widgets, including dynamically added content
        for widget in self.central_widget.findChildren((QLabel, QPushButton)):
            widget.setStyleSheet(widget.styleSheet() + "color: %s !important;" % colors['text-primary'])
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

        self.central_widget.update()