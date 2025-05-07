import spotipy
from PyQt6.QtWidgets import (QLabel, QWidget, QHBoxLayout, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import requests
from io import BytesIO

class Trends:
    def __init__(self, sp, market):
        self.sp = sp
        self.market = market

    def setup_ui(self, app):
        app.clear_content()

        trends_label = QLabel("Music Trends", alignment=Qt.AlignmentFlag.AlignCenter)
        trends_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF; padding: 10px; background-color: #1DB954; border-radius: 10px;")
        app.content_grid.addWidget(trends_label, 0, 0)

        self.get_new_releases(app)

    def get_new_releases(self, app):
        try:
            trends = self.sp.new_releases(limit=10, country=self.market)
            new_releases = []
            for item in trends['albums']['items']:
                release_info = {
                    "name": item['name'],
                    "artist": item['artists'][0]['name'],
                    "date": item['release_date'],
                    "image_url": item['images'][0]['url'] if item['images'] else None
                }
                new_releases.append(release_info)
            self.set_new_releases(new_releases, app)
        except Exception as e:
            self.set_trends_output(f"Error fetching new releases: {str(e)}", app)

    def set_new_releases(self, releases, app):
        for i in range(1, app.content_grid.count()):
            widget = app.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        content_width = app.content_area.width() - 30  # Subtract some padding
        image_max_size = min(content_width // 4, 150)  # Responsive max image size

        for i, release in enumerate(releases):
            release_container = QWidget()
            release_layout = QHBoxLayout(release_container)
            release_layout.setContentsMargins(5, 5, 5, 5)

            image_label = QLabel()
            if release['image_url']:
                try:
                    response = requests.get(release['image_url'])
                    image_data = BytesIO(response.content)
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data.read())
                    scaled_pixmap = pixmap.scaled(image_max_size, image_max_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                except Exception:
                    image_label.setText("Image not available")
            else:
                image_label.setText("No image")
            image_label.setMaximumSize(image_max_size, image_max_size)
            image_label.setStyleSheet(f"border: 1px solid #1DB954; border-radius: 5px; max-width: {image_max_size}px; max-height: {image_max_size}px;")
            release_layout.addWidget(image_label)

            info_label = QLabel(f"{release['name']} by {release['artist']} (Released: {release['date']})")
            info_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
            info_label.setWordWrap(True)
            release_layout.addWidget(info_label)

            row = (i // 2) + 1
            col = (i % 2) * 2
            app.content_grid.addWidget(release_container, row, col, 1, 2)

        app.content_container.adjustSize()

    def set_trends_output(self, text, app):
        for i in range(1, app.content_grid.count()):
            widget = app.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        label = QLabel(text)
        label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        label.setWordWrap(True)
        layout.addWidget(label)
        app.content_grid.addWidget(container, 1, 0, 1, 2)
        app.content_container.adjustSize()