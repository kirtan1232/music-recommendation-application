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
        self.setGeometry(200, 200, 800, 600)  # Default small screen size
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="e0b95b00815a44a7bfe0679d69b0c0c9",
            client_secret="c64ba96c85e54a72b51c3a933b2402be",
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="user-library-read playlist-read-private user-top-read user-read-private user-read-playback-state user-modify-playback-state"
        ))

        user_profile = self.sp.current_user()
        self.market = user_profile.get('country', 'US')

        self.recommendations = Recommendations(self.sp, self.market)
        self.catalog = Catalog(self.sp, self.market)
        self.trends = Trends(self.sp, self.market)
        self.playlist = Playlist(self.sp, self.market)

        self.app = App(central_widget, self.sp)
        self.app.recommend_button.clicked.connect(lambda: self.recommendations.setup_ui(self.app))
        self.app.catalog_button.clicked.connect(lambda: self.catalog.setup_ui(self.app))
        self.app.trends_button.clicked.connect(lambda: self.trends.setup_ui(self.app))
        self.app.playlist_button.clicked.connect(lambda: self.playlist.setup_ui(self.app))
        self.app.close_button.clicked.connect(self.close)
        self.app.minimize_button.clicked.connect(self.showMinimized)

        # Initial setup with Recommendations
        self.recommendations.setup_ui(self.app)
        self.app.set_active_button(self.app.recommend_button)  # Highlight Recommendations button on startup
       

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.app.start_drag(event)

    def mouseMoveEvent(self, event):
        self.app.drag_window(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
    
        # Safely handle catalog resize
        if hasattr(self, 'catalog') and hasattr(self.catalog, 'catalog_data'):
            try:
                if any(self.catalog.catalog_data.values()):  # Check if there's any data to display
                    self.catalog.display_results(self.catalog.catalog_data, self.app)
            except Exception as e:
                print(f"Error during catalog resize: {str(e)}")
        
        # Handle other components similarly if needed
        if hasattr(self, 'recommendations'):
            try:
                # Add similar handling for recommendations if needed
                pass
            except Exception as e:
                print(f"Error during recommendations resize: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicRecommendationSystem()
    window.show()
    sys.exit(app.exec())