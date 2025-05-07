import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget)
from PyQt6.QtCore import Qt
from app import App
from recommendations import Recommendations
from catalog import Catalog
from trends import Trends
from playlist import Playlist

class MusicRecommendationSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Recommendation System")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="e0b95b00815a44a7bfe0679d69b0c0c9",
            client_secret="c64ba96c85e54a72b51c3a933b2402be",
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="user-library-read playlist-read-private user-top-read user-read-private"
        ))

        user_profile = self.sp.current_user()
        self.market = user_profile.get('country', 'US')

        self.recommendations = Recommendations(self.sp, self.market)
        self.catalog = Catalog(self.sp, self.market)
        self.trends = Trends(self.sp, self.market)
        self.playlist = Playlist(self.sp, self.market)

        self.app = App(central_widget)
        self.app.recommend_button.clicked.connect(lambda: self.recommendations.setup_ui(self.app))
        self.app.catalog_button.clicked.connect(lambda: self.catalog.setup_ui(self.app))
        self.app.trends_button.clicked.connect(lambda: self.trends.setup_ui(self.app))
        self.app.playlist_button.clicked.connect(lambda: self.playlist.setup_ui(self.app))
        self.app.close_button.clicked.connect(self.close)
        self.app.minimize_button.clicked.connect(self.showMinimized)
        self.app.toggle_size_button.clicked.connect(self.toggle_window_size)

        # Initial setup with Recommendations
        self.recommendations.setup_ui(self.app)

        self.is_fullscreen = True

    def toggle_window_size(self):
        if self.is_fullscreen:
            self.setGeometry(200, 200, 800, 600)
            self.is_fullscreen = False
        else:
            self.setGeometry(0, 0, 1920, 1080)
            self.is_fullscreen = True

    def mousePressEvent(self, event):
        if not self.is_fullscreen and event.button() == Qt.MouseButton.LeftButton:
            self.app.start_drag(event)

    def mouseMoveEvent(self, event):
        if not self.is_fullscreen:
            self.app.drag_window(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicRecommendationSystem()
    window.show()
    sys.exit(app.exec())