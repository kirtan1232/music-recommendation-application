To install these dependencies on another machine, you would:

Copy both requirements.txt and your application files

Run: pip install -r requirements.txt

Create a .env file with the Spotify credentials

Run the application with python main.py

Note: The Gemini API key in recommendations.py is also hardcoded - you should similarly move this to environment variables for security.
