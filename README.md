# Emotional Journey Visualizer AI

This Flask web application uses Google's Gemini AI (specifically the "gemma-3-27b-it" model by default) to analyze user-described situations and generate an emotional map. This map includes core emotions, emotional transitions, trigger analysis, psychological interpretations, healing suggestions, an empathetic message, and a visual flowchart of emotional stages rendered using Graphviz.

The frontend is built with **Materialize CSS** and includes interactive features like a loading spinner, fullscreen SVG viewing, and dynamic form validation.

## Features

*   **User Input:** Accepts a description of a situation, preferred language, age, and country via a Materialize-styled form.
*   **AI-Powered Analysis:** Leverages Google Gemini for in-depth emotional mapping.
*   **Structured Output:** The AI is prompted to return a JSON object containing specific keys for emotional analysis components.
*   **Visual Flowchart:** Generates an SVG flowchart of the emotional stages using Graphviz, viewable in fullscreen.
*   **Interactive Web Interface:** Provides a user-friendly web form (`index.html`) using Materialize CSS for input and displays the analysis results in styled cards.
*   **Customizable Prompt:** The `build_prompt` function meticulously crafts the prompt sent to the AI.
*   **Error Handling:** Includes logging and user-facing error messages for API key issues, model initialization failures, AI response parsing errors, and content safety blocks.
*   **Input Validation:** Basic validation for situation length (240 characters) with visual feedback.
*   **Loading State:** Displays a loading spinner and disables the submit button while the AI processes the request.
*   **Responsive Design:** Includes a notice for optimal viewing of the flowchart on larger screens.
*   **Google Analytics:** Integrated for usage tracking.

## Prerequisites

*   **Python 3.7+**
*   **Pip** (Python package installer)
*   **Graphviz:** The Graphviz software must be installed on your system and in your system's PATH for the `graphviz` Python library to function correctly.
    *   **Linux (Ubuntu/Debian):** `sudo apt-get install graphviz`
    *   **macOS (using Homebrew):** `brew install graphviz`
    *   **Windows:** Download an installer from the [official Graphviz website](https://graphviz.org/download/) and ensure the `bin` directory is added to your PATH.
*   **Google AI Studio Account & Gemini API Key:** You need to obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Setup and Installation

1.  **Clone the repository (or create a project directory):**
    ```bash
    # Example: git clone <your-repo-url> # If you have a repo
    # cd <your-repo-directory-or-project-name>
    ```

2.  **Create the directory structure:**
    Inside your project directory, create a `templates` folder.
    ```
    your-project-name/
    ├── app.py
    ├── templates/
    │   └── index.html
    └── .env
    └── requirements.txt
    ```

3.  **Save the code:**
    *   Save the Python script as `app.py` in the root of your project directory.
    *   Save the HTML content as `index.html` inside the `templates` folder.

4.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

5.  **Install Python dependencies:**
    Create a `requirements.txt` file in the root of your project directory with the following content:
    ```txt
    Flask
    graphviz
    google-generativeai
    python-dotenv
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Create a `.env` file** in the root directory of the project (the same directory as `app.py`).
2.  **Add your Gemini API Key to the `.env` file:**
    ```env
    GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
    ```
    Replace `YOUR_ACTUAL_GEMINI_API_KEY` with the key you obtained from Google AI Studio.

3.  **(Optional) Change AI Model:**
    The application uses a specific Gemini model by default (defined as `MODEL_NAME` in `app.py`). You can change this variable if you wish to use a different compatible Gemini model.

## Running the Application

1.  Ensure your virtual environment is activated and your `.env` file is configured.
2.  Run the Flask application:
    ```bash
    python app.py
    ```
3.  Open your web browser and navigate to the address displayed in your terminal (typically `http://localhost:5001` or `http://0.0.0.0:5001`).

## Usage

1.  Access the web application via your browser.
2.  Fill in the form fields for your situation, preferred language, age (optional), and country (optional).
3.  Click the "Map My Emotions" button. A loader will indicate processing.
4.  The application will process your input, query the Gemini AI, and display the generated emotional map, healing suggestions, a final message, and the visual flowchart. The flowchart can be viewed in fullscreen.

## AI Prompt Details

The core of the AI interaction lies in the `build_prompt` function. It instructs the AI to act as an "expert Emotional Mapping AI" and provide a very concise emotional map with few key stages.

The most critical instruction to the AI is that its output must be a single, valid JSON object, and nothing else.

The prompt specifies the following sections (keys) to be included in the JSON response:
1.  `core_emotions`
2.  `emotional_transitions`
3.  `trigger_analysis`
4.  `psychological_interpretation`
5.  `emotional_stages` (for Graphviz nodes, including stage ID/label and description)
6.  `connections` (for Graphviz edges, including source, target, and optional label)
7.  `healing_suggestions`
8.  `final_message`

## Code Structure

*   **`app.py`:** The main Flask application file.
    *   Imports necessary libraries.
    *   Sets up logging.
    *   Loads environment variables (API Key).
    *   Initializes the Gemini Generative Model.
    *   Defines Flask routes for rendering the main page and handling form submissions.
    *   `build_prompt()`: Constructs the detailed prompt for the AI.
    *   `extract_json_from_text()`:  Extracts the JSON block from the AI's raw text response.
    *   Graphviz `Digraph` setup: Configures node and edge styles for the flowchart.
*   **`templates/index.html`:** The Jinja2 template for the web interface.
    *   Uses **Materialize CSS** for styling and components.
    *   Contains a form for user input.
    *   Displays error messages passed from the Flask backend.
    *   Renders the AI analysis results, including the embedded SVG flowchart.
    *   Includes JavaScript for Materialize components initialization, loading state, fullscreen SVG, character limit feedback, and dynamic input label activation.
    *   Integrates Google Analytics.
    *   Features a static "profile" sidenav.
*   **`.env`:** Stores the `GEMINI_API_KEY`.
*   **`requirements.txt`:** Lists Python dependencies.

## Error Handling & Logging

*   **Logging:** The application uses the `logging` module to record informational messages, warnings, errors, and critical failures. Logs are printed to the console.
*   **User Feedback (via `index.html`):**
    *   User-facing messages are displayed for issues such as AI model unavailability, unparseable AI responses, content safety blocks, or other unexpected errors.

## Troubleshooting

*   **"CRITICAL: GEMINI_API_KEY not found"**: Ensure you have created a `.env` file in the project root with your `GEMINI_API_KEY`.
*   **"Failed to initialize GenerativeModel"**: Double-check your API key, internet connection, and that the specified `MODEL_NAME` is valid and accessible with your key.
*   **Graphviz errors (e.g., related to "dot" execution)**: Make sure Graphviz is installed correctly on your system and its `bin` directory is in your system's PATH.
*   **"AI response could not be parsed"**: The AI might not have returned valid JSON. Try rephrasing your input. The raw AI output is logged for debugging (and can be un-commented in `index.html` to be displayed).
*   **"Your request was blocked"**: The input prompt or the AI's intended response might have triggered safety filters. Try rephrasing your input.
*   **Styling issues or JavaScript not working**: Ensure Materialize CSS and JS are correctly linked in `index.html`. Check the browser's developer console for errors. Make sure `index.html` is inside a `templates` folder.

## Future Enhancements

*   More dynamic front-end interactions (e.g., using AJAX to avoid page reloads).
*   User accounts to save emotional maps.
*   Option to choose different AI models from the UI.
*   More detailed Graphviz customization options accessible to the user.
*   Store and analyze trends in emotional maps over time.
*   Allow users to edit/refine the generated map.
