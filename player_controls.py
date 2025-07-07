from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                            QPushButton, QSlider, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
import requests
from io import BytesIO

class PlayerControls(QWidget):
    update_signal = pyqtSignal()

    def __init__(self, sp, parent=None):
        super().__init__(parent)
        self.sp = sp
        self.current_volume = 50  # Default volume
        self.volume_changed_by_user = False
        self.setup_ui()
        if self.sp is not None:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_playback)
            self.timer.start(1000)
            self.update_signal.connect(self.update_playback)
            # Set initial volume
            try:
                playback = self.sp.current_playback()
                if playback and 'device' in playback:
                    self.current_volume = playback['device']['volume_percent']
                    self.volume_slider.setValue(self.current_volume)
            except Exception as e:
                print(f"Error getting initial volume: {e}")
        else:
            self.set_controls_enabled(False)
            self.track_name.setText("Spotify not connected")

    def setup_ui(self):
        self.setStyleSheet("""
            background-color: #2A2A2A;
            border-top: 1px solid #1DB954;
            padding: 10px;
        """)
        self.setFixedHeight(120)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 5, 15, 5)
        main_layout.setSpacing(20)

        # Album art
        self.album_art = QLabel()
        self.album_art.setFixedSize(80, 80)
        self.album_art.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 4px;
        """)
        main_layout.addWidget(self.album_art)

        # Track info
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)
        
        self.track_name = QLabel("Not Playing")
        self.track_name.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #FFFFFF;
            margin-bottom: 2px;
        """)
        self.track_name.setWordWrap(True)
        
        self.artist_name = QLabel("")
        self.artist_name.setStyleSheet("font-size: 12px; color: #AAAAAA;")
        
        info_layout.addWidget(self.track_name)
        info_layout.addWidget(self.artist_name)
        info_layout.addStretch()
        
        main_layout.addLayout(info_layout, 1)

        # Controls
        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)

        # Progress bar with timestamps
        progress_layout = QHBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(10)
        
        self.current_time = QLabel("0:00")
        self.current_time.setStyleSheet("font-size: 11px; color: #AAAAAA;")
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setEnabled(False)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #555555;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #1DB954;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
                background: #FFFFFF;
            }
        """)
        
        self.duration_time = QLabel("0:00")
        self.duration_time.setStyleSheet("font-size: 11px; color: #AAAAAA;")
        
        progress_layout.addWidget(self.current_time)
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addWidget(self.duration_time)
        controls_layout.addLayout(progress_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Previous button
        self.prev_button = QPushButton("⏮")
        self.prev_button.setFixedSize(32, 32)
        self.prev_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                color: #FFFFFF;
                background-color: transparent;
                border: none;
                padding-bottom: 2px;
            }
            QPushButton:hover { 
                background-color: #444444; 
                color: #1DB954;
            }
            QPushButton:pressed { 
                background-color: #555555;
            }
        """)
        self.prev_button.clicked.connect(self.previous_track)
        buttons_layout.addWidget(self.prev_button)

        # Play/Pause button
        self.play_button = QPushButton("⏸")
        self.play_button.setFixedSize(42, 42)
        self.play_button.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                color: #FFFFFF;
                background-color: #1DB954;
                border: none;
                padding-bottom: 2px;
            }
            QPushButton:hover { 
                background-color: #1ED760; 
            }
            QPushButton:pressed { 
                background-color: #1AA34A;
            }
        """)
        self.play_button.clicked.connect(self.toggle_playback)
        buttons_layout.addWidget(self.play_button)

        # Next button
        self.next_button = QPushButton("⏭")
        self.next_button.setFixedSize(32, 32)
        self.next_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                color: #FFFFFF;
                background-color: transparent;
                border: none;
                padding-bottom: 2px;
            }
            QPushButton:hover { 
                background-color: #444444; 
                color: #1DB954;
            }
            QPushButton:pressed { 
                background-color: #555555;
            }
        """)
        self.next_button.clicked.connect(self.next_track)
        buttons_layout.addWidget(self.next_button)

        # Volume control
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.current_volume)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #555555;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #1DB954;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
                background: #FFFFFF;
            }
        """)
        self.volume_slider.sliderPressed.connect(self.volume_slider_pressed)
        self.volume_slider.sliderReleased.connect(self.volume_slider_released)
        self.volume_slider.valueChanged.connect(self.set_volume)
        buttons_layout.addWidget(self.volume_slider)
        
        controls_layout.addLayout(buttons_layout)
        main_layout.addLayout(controls_layout, 2)

    def volume_slider_pressed(self):
        self.volume_changed_by_user = True

    def volume_slider_released(self):
        self.volume_changed_by_user = False

    def format_time(self, milliseconds):
        """Convert milliseconds to MM:SS format"""
        seconds = int(milliseconds / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def update_playback(self):
        try:
            current = self.sp.current_playback()
            if current is None:
                self.show_no_playback()
                return

            track = current.get('item')
            if not track:
                self.show_no_playback()
                return

            # Update track info
            self.track_name.setText(track.get('name', 'Unknown Track'))
            artists = [artist.get('name', 'Unknown Artist') for artist in track.get('artists', [])]
            self.artist_name.setText(", ".join(artists) if artists else "Unknown Artist")
            
            # Update album art
            album_images = track.get('album', {}).get('images', [])
            if album_images:
                self.load_album_art(album_images[0].get('url'))
            else:
                self.album_art.clear()

            # Update play/pause button
            self.play_button.setText("⏸" if current.get('is_playing', False) else "▶")

            # Update progress and timestamps
            progress_ms = current.get('progress_ms', 0)
            duration_ms = track.get('duration_ms', 1)
            if duration_ms > 0:
                progress = (progress_ms / duration_ms) * 1000
                self.progress_slider.setValue(int(progress))
                self.current_time.setText(self.format_time(progress_ms))
                self.duration_time.setText(self.format_time(duration_ms))

            # Update volume only if not being changed by user
            if not self.volume_changed_by_user and 'device' in current and 'volume_percent' in current['device']:
                self.current_volume = current['device']['volume_percent']
                self.volume_slider.setValue(self.current_volume)

        except Exception as e:
            print(f"Error updating playback: {e}")
            self.show_no_playback()

    def load_album_art(self, image_url):
        """Load album art from URL in a thread-safe way"""
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.album_art.setPixmap(pixmap.scaled(
                    80, 80, 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
        except Exception as e:
            print(f"Error loading album art: {e}")
            self.album_art.clear()

    def show_no_playback(self):
        """Reset UI when no playback is active"""
        self.track_name.setText("Not Playing")
        self.artist_name.setText("")
        self.album_art.clear()
        self.play_button.setText("▶")
        self.current_time.setText("0:00")
        self.duration_time.setText("0:00")
        self.progress_slider.setValue(0)

    def set_controls_enabled(self, enabled):
        """Enable or disable all controls"""
        self.prev_button.setEnabled(enabled)
        self.play_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
        self.volume_slider.setEnabled(enabled)
        self.progress_slider.setEnabled(False)

    def toggle_playback(self):
        try:
            current = self.sp.current_playback()
            if current is None:
                devices = self.sp.devices()
                if devices and devices.get('devices'):
                    self.sp.transfer_playback(devices['devices'][0]['id'], force_play=True)
            else:
                if current.get('is_playing', False):
                    self.sp.pause_playback()
                else:
                    self.sp.start_playback()
            self.update_signal.emit()
        except Exception as e:
            print(f"Error toggling playback: {e}")

    def next_track(self):
        try:
            self.sp.next_track()
            self.update_signal.emit()
        except Exception as e:
            print(f"Error skipping to next track: {e}")

    def previous_track(self):
        try:
            self.sp.previous_track()
            self.update_signal.emit()
        except Exception as e:
            print(f"Error going to previous track: {e}")

    def set_volume(self, value):
        try:
            if value != self.current_volume:
                self.current_volume = value
                self.sp.volume(value)
        except Exception as e:
            print(f"Error setting volume: {e}")