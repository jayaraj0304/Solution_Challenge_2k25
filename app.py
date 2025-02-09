from flask import Flask, render_template, request, jsonify
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import re
from urllib.parse import urlparse, parse_qs
import datetime

app = Flask(__name__)
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Material-specific constants
MATERIAL_PROPERTIES = {
    'flour': {'base_density': 0.53, 'k': 0.003},
    'sugar': {'base_density': 0.85, 'k': 0.001},
    'salt': {'base_density': 1.2, 'k': 0.0005},
    'baking powder': {'base_density': 0.9, 'k': 0.002},
    'cocoa powder': {'base_density': 0.5, 'k': 0.004},
    'cornstarch': {'base_density': 0.6, 'k': 0.003},
}

# Reference humidity
REF_HUMIDITY = 50


def calculate_conversion_with_humidity(ingredient, quantity, unit, humidity):
    """Calculate the conversion with humidity adjustment"""
    properties = MATERIAL_PROPERTIES.get(ingredient.lower())
    if not properties:
        return get_conversion_from_gemini(ingredient, quantity, unit, humidity)
    
    base_density = properties['base_density']
    k = properties['k']
    
    # Calculate Humidity Correction Factor (HCF)
    hcf = 1 + (k * (humidity - REF_HUMIDITY))
    
    # Adjust density
    adjusted_density = base_density * hcf
    
    # Convert based on unit
    if unit.lower() == 'tablespoon':
        return 15 * quantity * adjusted_density
    elif unit.lower() == 'teaspoon':
        return 5 * quantity * adjusted_density
    elif unit.lower() == 'cup':
        return 236.588 * quantity * adjusted_density
    
    return None

def calculate_conversion_without_humidity(ingredient, quantity, unit):
    """Calculate the conversion without humidity adjustment"""
    properties = MATERIAL_PROPERTIES.get(ingredient.lower())
    if not properties:
        return get_conversion_from_gemini_simple(ingredient, quantity, unit)
    
    base_density = properties['base_density']
    
    # Convert based on unit without humidity adjustment
    if unit.lower() == 'tablespoon':
        return 15 * quantity * base_density
    elif unit.lower() == 'teaspoon':
        return 5 * quantity * base_density
    elif unit.lower() == 'cup':
        return 236.588 * quantity * base_density
    
    return None

def get_conversion_from_gemini(ingredient, quantity, unit, humidity):
    """Get conversion for unknown ingredients using Gemini with humidity"""
    prompt = f"""
    Convert {quantity} {unit} of {ingredient} to grams, considering {humidity}% humidity.
    The humidity reference point is 50%.
    Consider that humidity affects density.
    Please provide ONLY the numeric result in grams.
    """
    
    try:
        response = model.generate_content(prompt)
        result = float(''.join(filter(lambda x: x.isdigit() or x == '.', response.text)))
        return result
    except Exception as e:
        raise Exception(f"Conversion error: {str(e)}")

def get_conversion_from_gemini_simple(ingredient, quantity, unit):
    """Get conversion for unknown ingredients using Gemini without humidity"""
    prompt = f"""
    Convert {quantity} {unit} of {ingredient} to grams.
    Please provide ONLY the numeric result in grams.
    """
    
    try:
        response = model.generate_content(prompt)
        result = float(''.join(filter(lambda x: x.isdigit() or x == '.', response.text)))
        return result
    except Exception as e:
        raise Exception(f"Conversion error: {str(e)}")


def get_weather_data(location):
    api_key = os.getenv('WEATHER_API_KEY')
    location = location.strip()
    if not location:
        return None, "Location cannot be empty"
        
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 404:
            return None, f"Location '{location}' not found. Please enter a valid city name."
        elif response.status_code == 401:
            return None, "Invalid API key. Please check your OpenWeatherMap API key."
        elif response.status_code != 200:
            return None, f"Weather service error: {response.status_code}"
            
        data = response.json()
        return {
            'humidity': data['main']['humidity'],
            'temperature': data['main']['temp'] - 273.15
        }, None
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"

def get_location_suggestions(query):
    if not query or len(query) < 2:
        return []
        
    api_key = os.getenv('WEATHER_API_KEY')
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return [f"{city['name']}, {city.get('state', '')}, {city['country']}" for city in data]
    except:
        pass
    return []

def get_ingredient_suggestions(query):
    if not query:
        return []
    query = query.lower()
    return [ingredient for ingredient in MATERIAL_PROPERTIES.keys() if query in ingredient.lower()]

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    if not url:
        return None
        
    # Regular YouTube URL
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com'}:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

def analyze_video(url):
    """Analyze YouTube cooking video using Gemini"""
    video_id = extract_video_id(url)
    if not video_id:
        return None, "Invalid YouTube URL"

    try:
        prompt = f"""
        Analyze this cooking video {video_id} and provide:
        1. A detailed list of steps in chronological order
        2. Important cooking tips mentioned
        3. Key ingredients and their measurements
        4. Special techniques or tools used
        
        Format the response in clear sections with proper markdown.
        
        Video URL:{video_id}
        """
        
        response = model.generate_content(prompt)
        
        analysis_data = {
            'content': response.text,
            'video_id': video_id,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        return analysis_data, None
        
    except Exception as e:
        return None, f"Analysis error: {str(e)}"

def generate_recipe(dish_name):
    """Generate recipe with precise measurements using Gemini"""
    prompt = f"""
    Generate a detailed recipe for {dish_name} with:
    1. List of ingredients with EXACT measurements in grams
    2. Step-by-step preparation instructions
    3. Cooking time and temperature details
    4. Special equipment needed
    5. Tips for best results
    
    Format the response in clear sections with proper markdown.
    Ensure ALL measurements are in grams for consistency.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, f"Recipe generation error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video')
def video_page():
    return render_template('video.html')

@app.route('/recipe')
def recipe_page():
    return render_template('recipe.html')

@app.route('/suggest/location')
def suggest_location():
    query = request.args.get('q', '').strip()
    suggestions = get_location_suggestions(query)
    return jsonify(suggestions)

@app.route('/suggest/ingredient')
def suggest_ingredient():
    query = request.args.get('q', '').strip()
    suggestions = get_ingredient_suggestions(query)
    return jsonify(suggestions)

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        location = data.get('location', '').strip()
        ingredient = data.get('ingredient', '').strip()
        quantity = float(data.get('quantity', 0))
        unit = data.get('unit', '').strip()
        
        # Input validation
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        if not ingredient:
            return jsonify({'error': 'Ingredient is required'}), 400
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400
        if not unit:
            return jsonify({'error': 'Unit is required'}), 400
            
        # Get weather data
        weather_data, weather_error = get_weather_data(location)
        if weather_error:
            return jsonify({'error': weather_error}), 400
        
        # Calculate conversion
        try:
            result = calculate_conversion(ingredient, quantity, unit, weather_data['humidity'])
            if result is None:
                return jsonify({'error': 'Invalid unit'}), 400
                
            return jsonify({
                'grams': round(result, 2),
                'humidity': weather_data['humidity'],
                'temperature': round(weather_data['temperature'], 1)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        
    except ValueError as e:
        return jsonify({'error': 'Invalid quantity format'}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/analyze-video', methods=['POST'])
def analyze():
    try:
        # Handle both form data and JSON input
        if request.is_json:
            url = request.json.get('url', '').strip()
        else:
            url = request.form.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'YouTube URL is required'
            }), 400
            
        analysis_data, error = analyze_video(url)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 400
            
        return jsonify({
            'success': True,
            'analysis': analysis_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/generate-recipe', methods=['POST'])
def recipe():
    try:
        data = request.json
        dish_name = data.get('dish_name', '').strip()
        
        if not dish_name:
            return jsonify({'error': 'Dish name is required'}), 400
            
        recipe, error = generate_recipe(dish_name)
        if error:
            return jsonify({'error': error}), 400
            
        return jsonify({'recipe': recipe})
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)