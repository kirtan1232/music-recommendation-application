import spotipy
from PyQt6.QtWidgets import (QLabel, QLineEdit, QPushButton, QWidget, QHBoxLayout, QGridLayout, QApplication)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
import requests
from io import BytesIO

class ImageLoaderThread(QThread):
    image_loaded = pyqtSignal(QLabel, QPixmap)

    def __init__(self, url, max_size):
        super().__init__()
        self.url = url
        self.max_size = max_size

    def run(self):
        try:
            response = requests.get(self.url, timeout=5)
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.read())
            scaled_pixmap = pixmap.scaled(self.max_size, self.max_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.image_loaded.emit(self.sender(), scaled_pixmap)
        except Exception:
            pass

class Catalog:
    def __init__(self, sp, market):
        self.sp = sp
        self.market = market
        self.image_cache = {}  # Cache for images
        self.threads = []  # Keep track of threads to avoid garbage collection

    def setup_ui(self, app):
        app.clear_content()
        app.set_current_section(self.setup_ui)

        catalog_label = QLabel("Explore Music Catalog", alignment=Qt.AlignmentFlag.AlignCenter)
        catalog_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF; padding: 10px; background-color: #1DB954; border-radius: 10px;")
        app.content_grid.addWidget(catalog_label, 0, 0)

        self.catalog_input = QLineEdit()
        self.catalog_input.setPlaceholderText("Enter Artist, Track, or Album (e.g., 'The Beatles')")
        self.catalog_input.setStyleSheet("font-size: 14px; padding: 10px; border: 2px solid #1DB954; border-radius: 5px; background-color: #2A2A2A; color: #FFFFFF;")
        self.catalog_input.setMinimumHeight(40)
        app.content_grid.addWidget(self.catalog_input, 1, 0)

        catalog_button = QPushButton("Search Catalog")
        catalog_button.setStyleSheet("""
            QPushButton { font-size: 16px; font-weight: bold; color: #FFFFFF; background-color: #1DB954;
                          padding: 10px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #17a34a; }
            QPushButton:pressed { background-color: #158a3f; }
        """)
        catalog_button.setMinimumHeight(50)
        catalog_button.clicked.connect(lambda: self.search_catalog(self.catalog_input.text(), app))
        app.content_grid.addWidget(catalog_button, 2, 0)

        app.content_container.adjustSize()

    def search_catalog(self, query, app):
        self.clear_catalog(app)

        if not query:
            self.set_catalog_output("Please enter an artist, track, or album.", app)
            return

        try:
            results = self.sp.search(q=query, type="track,artist,album", limit=5, market=self.market)
            catalog_data = {
                "tracks": [],
                "artists": [],
                "albums": []
            }

            if results['tracks']['items']:
                for track in results['tracks']['items']:
                    album_id = track['album']['id']
                    album_info = self.sp.album(album_id)
                    image_url = album_info['images'][0]['url'] if album_info['images'] else None
                    catalog_data["tracks"].append({
                        "name": track['name'],
                        "artist": track['artists'][0]['name'],
                        "image_url": image_url
                    })

            if results['artists']['items']:
                for artist in results['artists']['items']:
                    top_track = self.sp.artist_top_tracks(artist['id'], country=self.market)['tracks'][0] if self.sp.artist_top_tracks(artist['id'], country=self.market)['tracks'] else None
                    image_url = None
                    if top_track:
                        album_id = top_track['album']['id']
                        album_info = self.sp.album(album_id)
                        image_url = album_info['images'][0]['url'] if album_info['images'] else None
                    catalog_data["artists"].append({
                        "name": artist['name'],
                        "genres": ', '.join(artist['genres'][:2]) if artist['genres'] else 'Unknown',
                        "image_url": image_url
                    })

            if results['albums']['items']:
                for album in results['albums']['items']:
                    image_url = album['images'][0]['url'] if album['images'] else None
                    catalog_data["albums"].append({
                        "name": album['name'],
                        "artist": album['artists'][0]['name'],
                        "image_url": image_url
                    })

            self.set_catalog(catalog_data, app)
        except spotipy.exceptions.SpotifyException as e:
            self.set_catalog_output(f"Error: {str(e)}", app)
        except Exception as e:
            self.set_catalog_output(f"Error: {str(e)}", app)

    def set_catalog(self, catalog_data, app):
        for i in range(3, app.content_grid.count()):
            widget = app.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        content_width = app.get_content_width()
        columns = 2 if content_width < 600 else 5  # Switch to 2 columns if width < 600px
        image_max_size = min(content_width // (columns + 1), 120)  # Adjust image size based on columns

        items = []
        items.extend([(f"Track: {t['name']}", t['artist'], t['image_url']) for t in catalog_data['tracks']])
        items.extend([(f"Artist: {a['name']}", f"Genres: {a['genres']}", a['image_url']) for a in catalog_data['artists']])
        items.extend([(f"Album: {a['name']}", a['artist'], a['image_url']) for a in catalog_data['albums']])

        for i, (name, detail, image_url) in enumerate(items):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(2, 2, 2, 2)

            image_label = QLabel()
            if image_url:
                if image_url in self.image_cache:
                    scaled_pixmap = self.image_cache[image_url]
                    image_label.setPixmap(scaled_pixmap)
                else:
                    image_label.setText("Loading...")
                    thread = ImageLoaderThread(image_url, image_max_size)
                    thread.image_loaded.connect(lambda label, pixmap, url=image_url: self.on_image_loaded(label, pixmap, url))
                    thread.sender = lambda: image_label
                    thread.start()
                    self.threads.append(thread)
            else:
                image_label.setText("No image")
            image_label.setMaximumSize(image_max_size, image_max_size)
            image_label.setStyleSheet(f"border: 1px solid #1DB954; border-radius: 5px; max-width: {image_max_size}px; max-height: {image_max_size}px;")
            layout.addWidget(image_label)

            info_label = QLabel(f"{name} - {detail}")
            info_label.setStyleSheet("font-size: 12px; color: #FFFFFF;")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

            row = (i // columns) + 3
            col = i % columns
            app.content_grid.addWidget(container, row, col, 1, 1)

        app.content_grid.setHorizontalSpacing(5)
        app.content_grid.setVerticalSpacing(5)
        app.content_container.adjustSize()

    def on_image_loaded(self, label, pixmap, url):
        self.image_cache[url] = pixmap
        label.setText("")
        label.setPixmap(pixmap)
        QApplication.processEvents()

    def clear_catalog(self, app):
        for i in range(3, app.content_grid.count()):
            widget = app.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def set_catalog_output(self, text, app):
        for i in range(3, app.content_grid.count()):
            widget = app.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        content_width = app.get_content_width()
        columns = 2 if content_width < 600 else 5
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        label = QLabel(text)
        label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        label.setWordWrap(True)
        layout.addWidget(label)
        app.content_grid.addWidget(container, 3, 0, 1, columns)
        app.content_container.adjustSize()