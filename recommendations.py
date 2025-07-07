from PyQt6.QtWidgets import (QLabel, QLineEdit, QPushButton, QWidget, 
                            QHBoxLayout, QVBoxLayout, QGridLayout, 
                            QSizePolicy, QSpacerItem, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtGui import QMovie  # Import QMovie for GIF animation
import requests
from io import BytesIO
import google.generativeai as genai
import re

class Recommendations:
    def __init__(self, sp, market):
        self.sp = sp
        self.market = market
        genai.configure(api_key="AIzaSyA6z_xEBvwAm1vBtbcfp9ZnWRcTLN2Jh6o")
        self.min_width = 300
        self.max_image_size = 200

    def setup_ui(self, app):
        app.clear_content()
        
        # Create main container
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)
        
        # Header
        header = QLabel("Music Recommendation System")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #1DB954;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Input section (fixed at top)
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter mood or genre (e.g., 'happy summer' or 'relaxing jazz')")
        self.input_field.setStyleSheet("""
            font-size: 14px; padding: 10px; 
            border: 2px solid #1DB954; border-radius: 5px;
            background-color: #2A2A2A; color: #FFFFFF;
        """)
        self.input_field.setMinimumHeight(45)
        input_layout.addWidget(self.input_field)
        
        recommend_button = QPushButton("Search")
        recommend_button.setFixedSize(100, 45)
        recommend_button.setStyleSheet("""
            QPushButton {
                font-size: 14px; font-weight: bold; 
                color: #FFFFFF; background-color: #1DB954;
                border-radius: 5px; border: none;
            }
            QPushButton:hover { background-color: #17a34a; }
            QPushButton:pressed { background-color: #158a3f; }
        """)
        recommend_button.clicked.connect(lambda: self.get_recommendations(self.input_field.text()))
        input_layout.addWidget(recommend_button)
        
        main_layout.addWidget(input_container)
        
        # Background GIF with animation (reduced size)
        self.background_gif = QLabel()
        self.background_gif.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie("background.gif")
        if self.movie.isValid():
            self.background_gif.setMovie(self.movie)
            self.movie.start()  # Start the GIF animation
            # Reduce size to 150x150 pixels (adjust as needed)
            self.background_gif.setFixedSize(570,300)
        main_layout.addWidget(self.background_gif)
        
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
        
        app.content_area.setMinimumWidth(self.min_width)
        app.content_container.adjustSize()

    def get_gemini_recommendations(self, keyword):
        try:
            prompt = f"""
Based on the keyword "{keyword}", recommend exactly 5 songs that match the mood or genre. 
Format each recommendation strictly as: "Song Title - Artist Name".
Also recommend me songs which are available on Spotify.
Return only the recommendations, no additional text or explanations.
"""
            model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
            response = model.generate_content(prompt)
            
            recommendations = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line and re.match(r'^(.+)\s-\s(.+)$', line):
                    recommendations.append(line)
                elif line and re.match(r'^(.+)\sby\s(.+)$', line):
                    song, artist = line.split(' by ', 1)
                    recommendations.append(f"{song.strip()} - {artist.strip()}")
            
            return recommendations[:5]
        
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return []

    def get_recommendations(self, keyword):
        self.clear_recommendations()
        self.background_gif.hide()

        if not keyword:
            self.show_message("Please enter a keyword to search for music.")
            self.background_gif.show()
            return

        recommendations = self.get_gemini_recommendations(keyword)
        
        if not recommendations:
            self.show_message("No recommendations found. Try a different keyword.")
            self.background_gif.show()
            return
        
        recommendations_data = []
        for rec in recommendations:
            try:
                song_name, artist_name = rec.split(' - ', 1)
                image_url = None
                
                if self.sp:
                    try:
                        search_results = self.sp.search(
                            q=f"track:{song_name} artist:{artist_name}", 
                            type="track", 
                            limit=1, 
                            market=self.market
                        )
                        if search_results['tracks']['items']:
                            track = search_results['tracks']['items'][0]
                            song_name = track['name']
                            artist_name = track['artists'][0]['name']
                            if track['album']['images']:
                                image_url = track['album']['images'][0]['url']
                    except Exception as e:
                        print(f"Spotify search error: {str(e)}")
                
                recommendations_data.append({
                    "name": song_name.strip(),
                    "artist": artist_name.strip(),
                    "image_url": image_url
                })
            except Exception as e:
                print(f"Error processing recommendation: {rec} - {str(e)}")
                continue
        
        self.display_recommendations(recommendations_data)

    def display_recommendations(self, recommendations):
        self.clear_recommendations()
        
        if not recommendations:
            self.show_message("No valid recommendations to display.")
            self.background_gif.show()
            return
        
        content_width = self.content_container.width() - 40
        items_per_row = 2 if content_width > 600 else 1
        image_size = min(self.max_image_size, (content_width // items_per_row) - 40)
        
        for i, rec in enumerate(recommendations):
            row = i // items_per_row
            col = i % items_per_row
            
            card = QWidget()
            card.setStyleSheet("background-color: #2A2A2A; border-radius: 8px; padding: 10px;")
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            layout = QHBoxLayout(card)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(15)
            
            image_label = QLabel()
            image_label.setFixedSize(image_size, image_size)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if rec['image_url']:
                try:
                    response = requests.get(rec['image_url'])
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
            
            layout.addWidget(image_label)
            
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(5)
            
            song_label = QLabel(rec['name'])
            song_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
            song_label.setWordWrap(True)
            
            artist_label = QLabel(rec['artist'])
            artist_label.setStyleSheet("font-size: 14px; color: #AAAAAA;")
            artist_label.setWordWrap(True)
            
            info_layout.addWidget(song_label)
            info_layout.addWidget(artist_label)
            info_layout.addStretch()
            
            layout.addWidget(info_widget, 1)
            
            self.content_grid.addWidget(card, row, col)
        
        self.content_container.adjustSize()

    def clear_recommendations(self):
        for i in range(self.content_grid.count() - 1, -1, -1):
            widget = self.content_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.content_grid.addItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 
            0, 0, 1, 2
        )

    def show_message(self, text):
        self.clear_recommendations()
        
        message = QLabel(text)
        message.setStyleSheet("font-size: 14px; color: #FFFFFF; padding: 20px;")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        
        self.content_grid.addWidget(message, 0, 0, 1, 2)
        self.content_container.adjustSize()
        self.background_gif.show()