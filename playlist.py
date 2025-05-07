import spotipy
from PyQt6.QtWidgets import (QLabel, QLineEdit, QPushButton, QWidget, QHBoxLayout, QGridLayout, QVBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import requests
from io import BytesIO

class Playlist:
    def __init__(self, sp, market):
        self.sp = sp
        self.market = market

    def setup_ui(self, app):
        app.clear_content()

        playlist_label = QLabel("Playlist Metadata", alignment=Qt.AlignmentFlag.AlignCenter)
        playlist_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF; padding: 10px; background-color: #1DB954; border-radius: 10px;")
        app.content_grid.addWidget(playlist_label, 0, 0)

        self.playlist_input = QLineEdit()
        self.playlist_input.setPlaceholderText("Enter Playlist ID or URL (e.g., '37i9dQZF1DXcBWIGoYBM5M')")
        self.playlist_input.setStyleSheet("font-size: 14px; padding: 10px; border: 2px solid #1DB954; border-radius: 5px; background-color: #2A2A2A; color: #FFFFFF;")
        self.playlist_input.setMinimumHeight(40)
        app.content_grid.addWidget(self.playlist_input, 1, 0)

        playlist_button = QPushButton("Get Metadata")
        playlist_button.setStyleSheet("""
            QPushButton { font-size: 16px; font-weight: bold; color: #FFFFFF; background-color: #1DB954;
                          padding: 10px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #17a34a; }
            QPushButton:pressed { background-color: #158a3f; }
        """)
        playlist_button.setMinimumHeight(50)
        playlist_button.clicked.connect(lambda: self.get_playlist_metadata(self.playlist_input.text(), app))
        app.content_grid.addWidget(playlist_button, 2, 0)

        app.content_container.adjustSize()

    def get_playlist_metadata(self, playlist_id, app):
        self.clear_playlist(app)

        if not playlist_id:
            self.set_playlist_output("Please enter a playlist ID or URL.", app)
            return

        if 'playlist' in playlist_id:
            playlist_id = playlist_id.split('playlist/')[1].split('?')[0]

        try:
            playlist = self.sp.playlist(playlist_id, market=self.market)
            if playlist:
                tracks_data = []
                for item in playlist['tracks']['items'][:3]:
                    track = item['track']
                    album_id = track['album']['id']
                    album_info = self.sp.album(album_id)
                    image_url = album_info['images'][0]['url'] if album_info['images'] else None
                    tracks_data.append({
                        "name": track['name'],
                        "artist": track['artists'][0]['name'],
                        "image_url": image_url
                    })
                self.set_playlist({
                    "name": playlist['name'],
                    "owner": playlist['owner']['display_name'],
                    "total_tracks": playlist['tracks']['total'],
                    "description": playlist['description'] or 'No description',
                    "tracks": tracks_data
                }, app)
            else:
                self.set_playlist_output("Playlist not found.", app)
        except spotipy.exceptions.SpotifyException as e:
            self.set_playlist_output(f"Error: {str(e)}", app)
        except Exception as e:
            self.set_playlist_output(f"Error: {str(e)}", app)

    def set_playlist(self, playlist_data, app):
        for i in range(3, app.content_grid.count()):
            widget = app.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        content_width = app.content_area.width() - 30  # Subtract some padding
        image_max_size = min(content_width // 4, 150)  # Responsive max image size

        metadata_container = QWidget()
        metadata_layout = QVBoxLayout(metadata_container)
        metadata_layout.setContentsMargins(5, 5, 5, 5)
        info_label = QLabel(f"Name: {playlist_data['name']}\nOwner: {playlist_data['owner']}\nTotal Tracks: {playlist_data['total_tracks']}\nDescription: {playlist_data['description']}")
        info_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        info_label.setWordWrap(True)
        metadata_layout.addWidget(info_label)
        app.content_grid.addWidget(metadata_container, 3, 0, 1, 2)

        for i, track in enumerate(playlist_data['tracks'], 1):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(5, 5, 5, 5)

            image_label = QLabel()
            if track['image_url']:
                try:
                    response = requests.get(track['image_url'])
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
            layout.addWidget(image_label)

            info_label = QLabel(f"{i}. {track['name']} by {track['artist']}")
            info_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

            row = (i // 2) + 4
            col = (i % 2) * 2
            app.content_grid.addWidget(container, row, col, 1, 2)

        app.content_container.adjustSize()

    def clear_playlist(self, app):
        for i in range(3, app.content_grid.count()):
            widget = app.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def set_playlist_output(self, text, app):
        for i in range(3, app.content_grid.count()):
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
        app.content_grid.addWidget(container, 3, 0, 1, 2)
        app.content_container.adjustSize()