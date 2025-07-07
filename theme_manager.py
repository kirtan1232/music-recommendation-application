from PyQt6.QtWidgets import QLabel, QPushButton

class ThemeManager:
    def __init__(self, app):
        self.app = app

    def get_theme_colors(self):
        if self.app.is_dark_mode:
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
        self.app.central_widget.setStyleSheet("""
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

    def get_title_bar_button_stylesheet(self):
        colors = self.get_theme_colors()
        return """
            QPushButton { 
                background-color: transparent; 
                color: %s !important; 
                border: none; 
                font-size: 14px; 
                padding: 0; 
            }
            QPushButton:hover { 
                background-color: %s; 
            }
        """ % (colors['text-primary'], colors['accent-hover'])

    def get_close_button_stylesheet(self):
        colors = self.get_theme_colors()
        return """
            QPushButton { 
                background-color: transparent; 
                color: %s !important; 
                border: none; 
                font-size: 14px; 
                padding: 0; 
            }
            QPushButton:hover { 
                background-color: #ff5555; 
            }
        """ % (colors['text-primary'])

    def get_theme_toggle_button_stylesheet(self):
        colors = self.get_theme_colors()
        icon = "🌙" if self.app.is_dark_mode else "☀️"  # Use minimal icons
        return """
            QPushButton { 
                background-color: transparent; 
                color: %s !important; 
                border: none; 
                font-size: 16px; 
                padding: 0; 
                text-align: center; 
            }
            QPushButton:hover { 
                background-color: %s; 
            }
        """ % (colors['text-primary'], colors['accent-hover'])

    def get_button_stylesheet(self):
        colors = self.get_theme_colors()
        return """
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
        """ % (colors['text-primary'], colors['bg-secondary'])

    def get_active_button_stylesheet(self):
        colors = self.get_theme_colors()
        return """
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
        """ % colors['text-primary']

    def get_sidebar_stylesheet(self):
        colors = self.get_theme_colors()
        return "background-color: %s;" % colors['bg-secondary']

    def get_content_area_stylesheet(self):
        colors = self.get_theme_colors()
        return """
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
        """ % (colors['bg-secondary'], colors['scrollbar-bg'])

    def get_sidebar_title_stylesheet(self):
        colors = self.get_theme_colors()
        return "font-size: 18px; font-weight: bold; color: %s !important; padding: 10px;" % colors['text-primary']

    def toggle_theme(self):
        self.app.is_dark_mode = not self.app.is_dark_mode
        self.app.theme_toggle_button.setStyleSheet(self.get_theme_toggle_button_stylesheet())  # Update stylesheet to reflect new icon
        
        self.apply_stylesheet()

        colors = self.get_theme_colors()
        self.app.theme_toggle_button.setStyleSheet(self.get_theme_toggle_button_stylesheet())
        self.app.minimize_button.setStyleSheet(self.get_title_bar_button_stylesheet())
        self.app.toggle_size_button.setStyleSheet(self.get_title_bar_button_stylesheet())
        self.app.close_button.setStyleSheet(self.get_close_button_stylesheet())
        self.app.sidebar_widget.setStyleSheet(self.get_sidebar_stylesheet())
        self.app.content_area.setStyleSheet(self.get_content_area_stylesheet())
        self.app.sidebar_title.setStyleSheet(self.get_sidebar_title_stylesheet())

        for button in [self.app.recommend_button, self.app.catalog_button, self.app.trends_button, self.app.playlist_button]:
            if button != self.app.active_button:
                button.setStyleSheet(self.get_button_stylesheet())
            else:
                button.setStyleSheet(self.get_active_button_stylesheet())

        for widget in self.app.central_widget.findChildren((QLabel, QPushButton)):
            widget.setStyleSheet(widget.styleSheet() + "color: %s !important;" % colors['text-primary'])
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

        self.app.central_widget.update()