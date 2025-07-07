from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QPoint, Qt  # Added Qt import
import sys
from ui_setup import setup_ui
from theme_manager import ThemeManager

class App:
    def __init__(self, central_widget):
        self.central_widget = central_widget
        self.drag_position = QPoint()
        self.active_button = None
        self.is_dark_mode = True
        self.theme_manager = ThemeManager(self)
        self.setup_ui()

    def setup_ui(self):
        setup_ui(self)

    def start_drag(self, event):  # Fixed indentation and parameter
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
            self.active_button.setStyleSheet(self.theme_manager.get_button_stylesheet())
        self.active_button = button
        if button:
            button.setProperty("active", True)
            button.setStyleSheet(self.theme_manager.get_active_button_stylesheet())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    app_instance = App(window)
    window.show()
    sys.exit(app.exec())