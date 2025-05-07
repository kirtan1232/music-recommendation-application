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

class Recommendations:
    def __init__(self, sp, market):
        self.sp = sp
        self.market = market
        self.image_cache = {}
        self.threads = []

    def setup_ui(self, app):
        app.clear_content()
        app.set_current_section(self.setup_ui)

        input_label = QLabel("Enter Song or Playlist (Name or URL):")
        input_label.setStyleSheet("font-size: 16px; color: #FFFFFF; margin-top: 10px;")
        app.content_grid.addWidget(input_label, 0, 0)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("e.g., 'Bohemian Rhapsody' or a Spotify URL")
        self.input_field.setStyleSheet("""
            font-size: 14px; padding: 10px; border: 2px solid #1DB954; border-radius: 5px;
            background-color: #2A2A2A; color: #FFFFFF;
        """)
        self.input_field.setMinimumHeight(40)
        app.content_grid.addWidget(self.input_field, 1, 0)

        recommend_button = QPushButton("Get Recommendations")
        recommend_button.setStyleSheet("""
            QPushButton { font-size: 16px; font-weight: bold; color: #FFFFFF; background-color: #1DB954;
                          padding: 10px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #17a34a; }
            QPushButton:pressed { background-color: #158a3f; }
        """)
        recommend_button.setMinimumHeight(50)
        recommend_button.clicked.connect(lambda: self.get_recommendations(self.input_field.text(), app))
        app.content_grid.addWidget(recommend_button, 2, 0)

        app.content_container.adjustSize()

    def get_recommendations(self, query, app):
        self.clear_recommendations(app)

        if not query:
            self.set_recommendation_output("Please enter a song or playlist.", app)
            return

        try:
            results = self.sp.search(q=query, type="track,playlist", limit=1, market=self.market)
            track_id = None
            artist_id = None
            genre = None

            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_id = track['id']
                artist_id = track['artists'][0]['id']
                artist_info = self.sp.artist(artist_id)
                genre = artist_info['genres'][0] if artist_info['genres'] else 'pop'
                self.set_recommendation_output(f"Found track: {track['name']} by {track['artists'][0]['name']}", app)
            elif results['playlists']['items']:
                playlist = results['playlists']['items'][0]
                playlist_id = playlist['id']
                tracks = self.sp.playlist_tracks(playlist_id, market=self.market)['items']
                if tracks:
                    track_id = tracks[0]['track']['id']
                    artist_id = tracks[0]['track']['artists'][0]['id']
                    artist_info = self.sp.artist(artist_id)
                    genre = artist_info['genres'][0] if artist_info['genres'] else 'pop'
                    self.set_recommendation_output(f"Found playlist: {playlist['name']}", app)
                else:
                    self.set_recommendation_output("Playlist is empty.", app)
                    return
            else:
                self.set_recommendation_output("No matching track or playlist found in your region.", app)
                return

            if track_id:
                track_info = self.sp.track(track_id, market=self.market)
                if not track_info['is_playable']:
                    self.set_recommendation_output("This track is not playable in your region, so recommendations cannot be generated.", app)
                    return

                recommendations = None
                try:
                    self.set_recommendation_output("Attempting track-based recommendations...", app)
                    recommendations = self.sp.recommendations(seed_tracks=[track_id], limit=5, market=self.market)
                except spotipy.exceptions.SpotifyException as e:
                    if e.http_status == 404:
                        self.set_recommendation_output("Track-based recommendations failed, trying artist-based recommendations...", app)
                if not recommendations and artist_id:
                    try:
                        recommendations = self.sp.recommendations(seed_artists=[artist_id], limit=5, market=self.market)
                    except spotipy.exceptions.SpotifyException as e:
                        if e.http_status == 404:
                            self.set_recommendation_output("Artist-based recommendations failed, trying genre-based recommendations...", app)
                if not recommendations and genre:
                    try:
                        recommendations = self.sp.recommendations(seed_genres=[genre], limit=5, market=self.market)
                    except spotipy.exceptions.SpotifyException as e:
                        if e.http_status == 404:
                            self.set_recommendation_output("Genre-based recommendations failed.", app)

                rec_tracks = recommendations['tracks'] if recommendations else []
                if not rec_tracks:
                    self.set_recommendation_output("No recommendations available. This may be due to account restrictions (e.g., free account) or regional limitations.", app)
                    return

                recommendations_data = []
                for idx, track in enumerate(rec_tracks, 1):
                    album_id = track['album']['id']
                    album_info = self.sp.album(album_id)
                    image_url = album_info['images'][0]['url'] if album_info['images'] else None
                    recommendations_data.append({
                        "name": f"{idx}. {track['name']}",
                        "artist": track['artists'][0]['name'],
                        "image_url": image_url
                    })
                self.set_recommendations(recommendations_data, app)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 403:
                self.set_recommendation_output("Error: Access forbidden. You may need a Spotify Premium account to access recommendations.", app)
            elif e.http_status == 404:
                self.set_recommendation_output("Error: Recommendations not available. The track, artist, or genre may not be accessible in your region.", app)
            else:
                self.set_recommendation_output(f"Spotify API Error: {str(e)}", app)
        except Exception as e:
            self.set_recommendation_output(f"Error: {str(e)}", app)

    def set_recommendations(self, recommendations, app):
        for i in range(3, app.content_grid.count()):
            widget = app.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        content_width = app.get_content_width()
        columns = 2 if content_width < 600 else 5
        image_max_size = min(content_width // (columns + 1), 120)

        for i, rec in enumerate(recommendations):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(2, 2, 2, 2)

            image_label = QLabel()
            if rec['image_url']:
                if rec['image_url'] in self.image_cache:
                    scaled_pixmap = self.image_cache[rec['image_url']]
                    image_label.setPixmap(scaled_pixmap)
                else:
                    image_label.setText("Loading...")
                    thread = ImageLoaderThread(rec['image_url'], image_max_size)
                    thread.image_loaded.connect(lambda label, pixmap, url=rec['image_url']: self.on_image_loaded(label, pixmap, url))
                    thread.sender = lambda: image_label
                    thread.start()
                    self.threads.append(thread)
            else:
                image_label.setText("No image")
            image_label.setMaximumSize(image_max_size, image_max_size)
            image_label.setStyleSheet(f"border: 1px solid #1DB954; border-radius: 5px; max-width: {image_max_size}px; max-height: {image_max_size}px;")
            layout.addWidget(image_label)

            info_label = QLabel(f"{rec['name']} by {rec['artist']}")
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

    def clear_recommendations(self, app):
        for i in range(3, app.content_grid.count()):
            widget = app.content_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def set_recommendation_output(self, text, app):
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