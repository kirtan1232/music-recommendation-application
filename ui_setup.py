from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QFrame, QWidget)
from PyQt6.QtCore import Qt

def setup_ui(app):
    main_layout = QVBoxLayout(app.central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    app.theme_manager.apply_stylesheet()

    # Title Bar
    app.title_bar = QFrame()
    app.title_bar.setStyleSheet("background-color: #1DB954;")
    app.title_bar.setFixedHeight(40)
    app.title_bar_layout = QHBoxLayout(app.title_bar)
    app.title_bar_layout.setContentsMargins(10, 0, 10, 0)

    title_label = QLabel("Music Recommendation System")
    title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
    app.title_bar_layout.addWidget(title_label)
    app.title_bar_layout.addStretch()

    # Theme Toggle Button
    app.theme_toggle_button = QPushButton()  # Remove text, will use stylesheet for icon
    app.theme_toggle_button.setFixedSize(30, 30)
    app.theme_toggle_button.setStyleSheet(app.theme_manager.get_theme_toggle_button_stylesheet())
    app.theme_toggle_button.clicked.connect(app.theme_manager.toggle_theme)
    app.title_bar_layout.addWidget(app.theme_toggle_button)

    # Minimize Button
    app.minimize_button = QPushButton("−")
    app.minimize_button.setFixedSize(30, 30)
    app.minimize_button.setStyleSheet(app.theme_manager.get_title_bar_button_stylesheet())
    app.title_bar_layout.addWidget(app.minimize_button)

    # Toggle Size Button
    app.toggle_size_button = QPushButton("□")
    app.toggle_size_button.setFixedSize(30, 30)
    app.toggle_size_button.setStyleSheet(app.theme_manager.get_title_bar_button_stylesheet())
    app.title_bar_layout.addWidget(app.toggle_size_button)

    # Close Button
    app.close_button = QPushButton("×")
    app.close_button.setFixedSize(30, 30)
    app.close_button.setStyleSheet(app.theme_manager.get_close_button_stylesheet())
    app.title_bar_layout.addWidget(app.close_button)

    main_layout.addWidget(app.title_bar)

    # Main Content with Sidebar
    content_layout = QHBoxLayout()
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(0)

    # Sidebar
    sidebar = QVBoxLayout()
    sidebar.setContentsMargins(0, 0, 0, 0)
    sidebar.setSpacing(5)

    app.sidebar_title = QLabel("Menu")
    app.sidebar_title.setStyleSheet(app.theme_manager.get_sidebar_title_stylesheet())
    sidebar.addWidget(app.sidebar_title)

    # Sidebar Buttons
    app.recommend_button = QPushButton("🎵 Recommendations")
    app.recommend_button.setStyleSheet(app.theme_manager.get_button_stylesheet())
    app.recommend_button.setProperty("active", False)
    app.recommend_button.clicked.connect(lambda: app.set_active_button(app.recommend_button))
    sidebar.addWidget(app.recommend_button)

    app.catalog_button = QPushButton("📚 Catalog")
    app.catalog_button.setStyleSheet(app.theme_manager.get_button_stylesheet())
    app.catalog_button.setProperty("active", False)
    app.catalog_button.clicked.connect(lambda: app.set_active_button(app.catalog_button))
    sidebar.addWidget(app.catalog_button)

    app.trends_button = QPushButton("📈 Trends")
    app.trends_button.setStyleSheet(app.theme_manager.get_button_stylesheet())
    app.trends_button.setProperty("active", False)
    app.trends_button.clicked.connect(lambda: app.set_active_button(app.trends_button))
    sidebar.addWidget(app.trends_button)

    app.playlist_button = QPushButton("🎧 Playlist")
    app.playlist_button.setStyleSheet(app.theme_manager.get_button_stylesheet())
    app.playlist_button.setProperty("active", False)
    app.playlist_button.clicked.connect(lambda: app.set_active_button(app.playlist_button))
    sidebar.addWidget(app.playlist_button)

    sidebar.addStretch()

    app.sidebar_widget = QWidget()
    app.sidebar_widget.setLayout(sidebar)
    app.sidebar_widget.setFixedWidth(200)
    app.sidebar_widget.setStyleSheet(app.theme_manager.get_sidebar_stylesheet())
    content_layout.addWidget(app.sidebar_widget)

    # Main Content Area
    app.content_area = QScrollArea()
    app.content_area.setWidgetResizable(True)
    app.content_area.setStyleSheet(app.theme_manager.get_content_area_stylesheet())
    app.content_container = QWidget()
    app.content_grid = QGridLayout(app.content_container)
    app.content_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
    app.content_grid.setSpacing(15)
    app.content_area.setWidget(app.content_container)
    content_layout.addWidget(app.content_area)

    main_layout.addLayout(content_layout)

    app.title_bar.mousePressEvent = app.start_drag
    app.title_bar.mouseMoveEvent = app.drag_window