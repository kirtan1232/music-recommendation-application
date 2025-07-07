import spotipy
from PyQt6.QtWidgets import (QLabel, QLineEdit, QPushButton, QWidget, 
                            QHBoxLayout, QVBoxLayout, QGridLayout, 
                            QSizePolicy, QSpacerItem, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont
import requests
from io import BytesIO
import re

class Catalog:
    def __init__(self, sp, market):
        self.sp = sp
        self.market = market
        self.min_width = 300
        self.max_image_size = 150
        self.catalog_data = {
            "tracks": [],
            "artists": [],
            "albums": []
        }

    def setup_ui(self, app):
        app.clear_content()
        
        # Create main container
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)
        
        # Header
        header = QLabel("Music Catalog Explorer")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #1DB954;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Input section (fixed at top)
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Search artists, tracks, or albums...")
        self.input_field.setStyleSheet("""
            font-size: 14px; padding: 10px; 
            border: 2px solid #1DB954; border-radius: 5px;
            background-color: #2A2A2A; color: #FFFFFF;
        """)
        self.input_field.setMinimumHeight(45)
        
        # Remove the manual mousePressEvent handler and let Qt handle the placeholder behavior
        
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
        search_button.clicked.connect(lambda: self.search_catalog(self.input_field.text()))
        input_layout.addWidget(search_button)
        
        main_layout.addWidget(input_container)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        # Content container
        self.content_container = QWidget()
        self.content_grid = QGridLayout(self.content_container)
        self.content_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_grid.setSpacing(15)
        
        scroll_area.setWidget(self.content_container)
        main_layout.addWidget(scroll_area)
        
        # Add main container to app's content grid
        app.content_grid.addWidget(main_container, 0, 0)
        
        # Set default placeholder text (no need to set actual text)
        self.input_field.setPlaceholderText("Search artists, tracks, or albums...")
        
        # Optionally perform a default search
        self.search_catalog("Red Hot Chili Peppers")  # Default search term

    def search_catalog(self, query):
        self.clear_results()

        if not query:
            self.show_message("Please enter a search term.")
            return

        try:
            results = self.sp.search(q=query, type="track,artist,album", limit=5, market=self.market)
            
            self.catalog_data = {
                "tracks": [],
                "artists": [],
                "albums": []
            }

            if results.get('tracks', {}).get('items'):
                for track in results['tracks']['items']:
                    image_url = track['album']['images'][0]['url'] if track['album']['images'] else None
                    self.catalog_data["tracks"].append({
                        "name": track['name'],
                        "artist": track['artists'][0]['name'],
                        "image_url": image_url
                    })

            if results.get('artists', {}).get('items'):
                for artist in results['artists']['items']:
                    image_url = artist['images'][0]['url'] if artist.get('images') else None
                    self.catalog_data["artists"].append({
                        "name": artist['name'],
                        "genres": ', '.join(artist['genres'][:3]) if artist['genres'] else 'Various genres',
                        "image_url": image_url
                    })

            if results.get('albums', {}).get('items'):
                for album in results['albums']['items']:
                    image_url = album['images'][0]['url'] if album['images'] else None
                    self.catalog_data["albums"].append({
                        "name": album['name'],
                        "artist": album['artists'][0]['name'],
                        "image_url": image_url
                    })

            self.display_results(self.catalog_data)

        except spotipy.exceptions.SpotifyException as e:
            self.show_message(f"Spotify API Error: {str(e)}")
        except Exception as e:
            self.show_message(f"Error: {str(e)}")

    def display_results(self, catalog_data):
        self.clear_results()
        
        if not any(catalog_data.values()):
            self.show_message("No results found. Try a different search.")
            return
        
        content_width = self.content_container.width() - 40
        items_per_row = 2 if content_width < 600 else 3
        image_size = min(self.max_image_size, (content_width // items_per_row) - 40)
        
        all_items = []
        all_items.extend([("🎵 Track", f"{t['name']}\nby {t['artist']}", t['image_url']) for t in catalog_data['tracks']])
        all_items.extend([("🎤 Artist", f"{a['name']}\n{a['genres']}", a['image_url']) for a in catalog_data['artists']])
        all_items.extend([("💿 Album", f"{a['name']}\nby {a['artist']}", a['image_url']) for a in catalog_data['albums']])
        
        for i, (category, text, image_url) in enumerate(all_items):
            row = i // items_per_row
            col = i % items_per_row
            
            card = QWidget()
            card.setStyleSheet("""
                background-color: #2A2A2A; 
                border-radius: 8px; 
                padding: 10px;
                border: 1px solid #1DB954;
            """)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            layout = QVBoxLayout(card)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            category_label = QLabel(category)
            category_label.setStyleSheet("font-size: 12px; color: #1DB954; font-weight: bold;")
            layout.addWidget(category_label)
            
            image_label = QLabel()
            image_label.setFixedSize(image_size, image_size)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if image_url:
                try:
                    response = requests.get(image_url)
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
            
            layout.addWidget(image_label, 0, Qt.AlignmentFlag.AlignCenter)
            
            text_label = QLabel(text)
            text_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
            text_label.setWordWrap(True)
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(text_label)
            
            self.content_grid.addWidget(card, row, col)
        
        self.content_container.adjustSize()

    def clear_results(self):
        for i in range(self.content_grid.count() - 1, -1, -1):
            widget = self.content_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.content_grid.addItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 
            0, 0, 1, 3
        )

    def show_message(self, text):
        self.clear_results()
        
        message = QLabel(text)
        message.setStyleSheet("font-size: 14px; color: #FFFFFF; padding: 20px;")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        
        self.content_grid.addWidget(message, 0, 0, 1, 3)
        self.content_container.adjustSize()