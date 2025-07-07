import google.generativeai as genai

def get_gemini_recommendations(keyword):
    # Configure the Gemini API with the provided API key
    genai.configure(api_key="AIzaSyA6z_xEBvwAm1vBtbcfp9ZnWRcTLN2Jh6o")  # Keep API key as provided
    
    try:
        # Define the prompt based on the single keyword
        prompt = f"""
Based on the following keyword, recommend up to 5 songs that best match the mood and musical characteristics. 
Keyword: "{keyword}"

Provide the results in the following format:
- Song Title - Artist Name
"""
        
        # Instantiate the GenerativeModel
        model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
        # Call the Gemini API to generate content
        response = model.generate_content(prompt)
        
        # Extract and process the recommendations
        recommendations = response.text.strip().split("\n")
        return [rec.strip() for rec in recommendations if rec.strip()]
    
    except Exception as e:
        return [f"Gemini API Error: {str(e)}"]

def main():
    # Interactive input for a single keyword
    keyword = input("Enter a keyword (e.g., 'upbeat pop', 'melancholic acoustic', 'energetic rock'): ")
    
    # Get recommendations
    recommendations = get_gemini_recommendations(keyword)
    
    # Print the recommendations
    if recommendations and not recommendations[0].startswith("Gemini API Error"):
        print("Recommended Songs:")
        for song in recommendations[:5]:  # Limit to 5 recommendations
            print(song)
    else:
        print(recommendations[0] if recommendations else "No recommendations available.")

if __name__ == "__main__":
    main()