import spotipy
from PyQt6.QtWidgets import (QLabel, QLineEdit, QPushButton, QWidget, 
                            QHBoxLayout, QVBoxLayout, QGridLayout, 
                            QSizePolicy, QSpacerItem, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont
import requests
from io import BytesIO

class Playlist:
    def __init__(self, sp, market):
        self.sp = sp
        self.market = market
        self.min_width = 300
        self.max_image_size = 150

    def setup_ui(self, app):
        app.clear_content()
        
        # Create a main container with vertical layout
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)
        
        # Header
        header = QLabel("Playlist Explorer")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #1DB954;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Input section (fixed at top)
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter playlist ID or URL...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                font-size: 14px; 
                padding: 10px;
                border: 2px solid #1DB954;
                border-radius: 5px;
                background-color: #2A2A2A;
                color: #FFFFFF;
            }
        """)
        # Set placeholder text color using QPalette
        palette = self.input_field.palette()
        palette.setColor(palette.ColorRole.PlaceholderText, Qt.GlobalColor.gray)
        self.input_field.setPalette(palette)
        self.input_field.setMinimumHeight(45)
        input_layout.addWidget(self.input_field)
        
        search_button = QPushButton("Search")
        search_button.setFixedSize(100, 45)
        search_button.setStyleSheet("""
            QPushButton {
                font-size: 14px; font-weight: bold; 
                color: #FFFFFF; background-color: #1DB954;
                border-radius: 5px; border: none;
            }
            QPushButton:hover { background-color: #17a34a; }
            QPushButton:pressed { background-color: #158a3f; }
        """)
        search_button.clicked.connect(lambda: self.get_playlist(self.input_field.text(), app))
        input_layout.addWidget(search_button)
        
        main_layout.addWidget(input_container)
        
        # Create scroll area for playlist content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        # Content container for playlist items
        self.content_container = QWidget()
        self.content_grid = QGridLayout(self.content_container)
        self.content_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_grid.setSpacing(15)
        
        scroll_area.setWidget(self.content_container)
        main_layout.addWidget(scroll_area)
        
        # Add main container to app's content grid
        app.content_grid.addWidget(main_container, 0, 0)
        
        # Show default playlist (but don't display the URL in the input field)
        default_playlist = "https://open.spotify.com/playlist/7ghJanbkXZNnLWL7w498FZ?si=718887de62b64527"
        self.get_playlist(default_playlist, app)  # Perform search without showing URL

    def get_playlist(self, playlist_id, app):
        self.clear_results()

        if not playlist_id:
            self.show_message("Please enter a playlist ID or URL.")
            return

        # Extract ID from URL if needed
        if 'playlist' in playlist_id:
            playlist_id = playlist_id.split('playlist/')[1].split('?')[0]

        try:
            playlist = self.sp.playlist(playlist_id, market=self.market)
            if not playlist:
                self.show_message("Playlist not found.")
                return

            # Get first 5 tracks
            tracks = []
            for item in playlist['tracks']['items'][:5]:
                track = item['track']
                image_url = track['album']['images'][0]['url'] if track['album']['images'] else None
                tracks.append({
                    "name": track['name'],
                    "artist": track['artists'][0]['name'],
                    "image_url": image_url
                })

            self.display_playlist({
                "name": playlist['name'],
                "owner": playlist['owner']['display_name'],
                "description": playlist['description'] or "No description",
                "total_tracks": playlist['tracks']['total'],
                "tracks": tracks
            })

        except spotipy.exceptions.SpotifyException as e:
            self.show_message(f"Spotify API Error: {str(e)}")
        except Exception as e:
            self.show_message(f"Error: {str(e)}")

    def display_playlist(self, playlist_data):
        self.clear_results()
        
        # Calculate responsive layout
        content_width = self.content_container.width() - 40
        image_size = min(self.max_image_size, content_width // 2 - 40)
        
        # Playlist metadata
        metadata_card = QWidget()
        metadata_card.setStyleSheet("""
            background-color: #2A2A2A;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #1DB954;
        """)
        
        metadata_layout = QVBoxLayout(metadata_card)
        metadata_layout.setSpacing(10)
        
        name_label = QLabel(playlist_data['name'])
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1DB954;")
        metadata_layout.addWidget(name_label)
        
        details_label = QLabel(
            f"👤 {playlist_data['owner']}\n"
            f"📝 {playlist_data['description']}\n"
            f"🎵 {playlist_data['total_tracks']} tracks"
        )
        details_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        details_label.setWordWrap(True)
        metadata_layout.addWidget(details_label)
        
        self.content_grid.addWidget(metadata_card, 0, 0, 1, 2)
        
        # Tracks
        for i, track in enumerate(playlist_data['tracks'], 1):
            track_card = QWidget()
            track_card.setStyleSheet("""
                background-color: #2A2A2A;
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #333333;
            """)
            
            track_layout = QHBoxLayout(track_card)
            track_layout.setContentsMargins(5, 5, 5, 5)
            track_layout.setSpacing(15)
            
            # Number
            num_label = QLabel(f"{i}.")
            num_label.setStyleSheet("font-size: 16px; color: #1DB954; font-weight: bold;")
            num_label.setFixedWidth(30)
            track_layout.addWidget(num_label)
            
            # Image
            image_label = QLabel()
            image_label.setFixedSize(image_size, image_size)
            if track['image_url']:
                try:
                    response = requests.get(track['image_url'])
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    pixmap = pixmap.scaled(
                        image_size, image_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    image_label.setPixmap(pixmap)
                except Exception:
                    image_label.setText("No Image")
                    image_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
            else:
                image_label.setText("No Image")
                image_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
            track_layout.addWidget(image_label)
            
            # Track info
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(5)
            
            track_label = QLabel(track['name'])
            track_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
            track_label.setWordWrap(True)
            
            artist_label = QLabel(track['artist'])
            artist_label.setStyleSheet("font-size: 14px; color: #AAAAAA;")
            artist_label.setWordWrap(True)
            
            info_layout.addWidget(track_label)
            info_layout.addWidget(artist_label)
            info_layout.addStretch()
            
            track_layout.addWidget(info_widget, 1)
            
            self.content_grid.addWidget(track_card, i, 0, 1, 2)
        
        self.content_container.adjustSize()

    def clear_results(self):
        for i in range(self.content_grid.count() - 1, -1, -1):
            widget = self.content_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.content_grid.addItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 
            0, 0, 1, 2
        )

    def show_message(self, text):
        self.clear_results()
        
        message = QLabel(text)
        message.setStyleSheet("font-size: 14px; color: #FFFFFF; padding: 20px;")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        
        self.content_grid.addWidget(message, 0, 0, 1, 2)
        self.content_container.adjustSize()