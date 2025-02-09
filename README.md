Precision Baking: AI for Accurate Ingredient Measurement in Grams

Overview

Online recipe platforms often list ingredients in vague measurements like "cups" or "spoons," leading to inconsistent results, especially in professional baking. This lack of precision frustrates bakers and affects the quality of their baked goods.

To solve this, we implemented a platform that:

Converts various measurement units to precise grams.

Analyzes YouTube recipe videos using video links to generate an exact recipe sheet with ingredient measurements in grams.

Generates a recipe by simply entering a dish name.

Utilizes Gemini AI via app calls to provide human-like assistance to bakers through text and camera inputs.

Features

Unit Conversion: Converts measurements (cups, spoons, etc.) into accurate grams.

YouTube Recipe Analysis: Extracts and structures ingredient measurements from YouTube videos.

AI-Powered Recipe Generation: Generates detailed recipes based on dish names.

Gemini AI Integration: Offers an intelligent assistant for bakers via camera and text-based interactions.

Installation & Setup

1. Clone the Repository

git clone https://github.com/jayaraj0304/Solution_Challenge_2k25.git
cd Solution_Challenge_2k25

2. Setup API Keys

Replace the API keys in the .env file:

Replace ACCESS_TOKEN with your Google Cloud access token.

Replace PROJECT_ID with your Google Cloud project ID.

3. Run the Backend

Open a terminal and run:

python app.py

In a new terminal, navigate to the backend directory:

cd backend
python main.py

4. Run the Frontend

In another terminal, navigate to the frontend directory:

cd frontend
python -m http.server

Technologies Used

Python (FastAPI, Flask for backend)

JavaScript (Frontend with HTML, CSS, JS)

Gemini AI API (For video analysis, unit conversion, and text-based recipe generation)

Google Cloud Services

Usage

Convert Measurements: Enter a measurement in cups/spoons and get precise grams.

Analyze YouTube Recipe: Paste a YouTube video link to extract an accurate recipe sheet.

Generate Recipe: Enter a dish name to get an AI-generated recipe.

AI Assistance: Use the Gemini-powered assistant to get baking-related guidance via text or camera.

Contributing

If you’d like to contribute:

Fork the repository.

Create a new branch: git checkout -b feature-branch

Commit your changes: git commit -m "Add new feature"

Push to the branch: git push origin feature-branch

Open a Pull Request.

License

This project is licensed under the MIT License.

Contact

For any queries, reach out to jayaraj at https://www.linkedin.com/in/jayaraj-thamatam1 or open an issue in the repository.

Happy Baking! 🍞🍪🎂

