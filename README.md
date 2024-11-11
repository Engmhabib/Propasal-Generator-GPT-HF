
# Proposal-Generator-GPT-HF

This repository contains a Flask web application that generates personalized proposals (e.g., marriage, friendship, business) along with a thematic image using OpenAI's `gpt-3.5-turbo` and Hugging Face's Stable Diffusion APIs. The application prompts the user for details about the proposal and then generates both a written proposal and an accompanying image based on the provided themes.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Detailed Code Explanation](#detailed-code-explanation)
  - [app.py](#apppy)
  - [tasks.py](#taskspy)
  - [Templates](#templates)
- [Usage](#usage)
- [Notes](#notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Introduction

This application serves as an educational project to demonstrate how to integrate OpenAI's `gpt-3.5-turbo` and Hugging Face's Stable Diffusion APIs into a Flask web application. Users can input the type of proposal they want to generate, the recipient's name, themes, and any additional details. The app then generates a heartfelt proposal and a corresponding image.

## Features

- **Personalized Proposals**: Generates a customized proposal letter based on user input using `gpt-3.5-turbo`.
- **Image Generation**: Creates a thematic image that complements the proposal using Hugging Face's Stable Diffusion.
- **Error Handling**: Implements robust error handling and retry mechanisms.
- **Extensible**: Code is modular and can be extended for additional features.
- **Accessible**: Utilizes APIs that are more widely accessible, reducing the barrier to entry for students.

## Prerequisites

- **Python 3.7 or higher**
- OpenAI API access with permissions for:
  - `gpt-3.5-turbo` model
- Hugging Face account and API token with **Read** permissions
- An OpenAI API key
- A Hugging Face API token
- Basic knowledge of Python and Flask

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Engmhabib/Propasal-Generator-GPT-HF.git
   cd proposal-generator
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

   **requirements.txt**

   ```text
   Flask
   openai
   requests
   python-dotenv
   tenacity
   huggingface-hub
   Pillow
   ```

## Configuration

1. **Set Up Environment Variables**

   Create a `.env` file in the root directory of the project:

   ```bash
   touch .env
   ```

   Add the following lines to `.env`:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   HUGGINGFACE_API_TOKEN=your_huggingface_api_token_here
   FLASK_SECRET_KEY=your_flask_secret_key_here
   ```

   - Replace `your_openai_api_key_here` with your actual OpenAI API key.
   - Replace `your_huggingface_api_token_here` with your Hugging Face API token.
   - Replace `your_flask_secret_key_here` with a secret key for Flask sessions.

2. **Ensure API Access**

   - **OpenAI API Key**: Ensure your OpenAI API key has access to the `gpt-3.5-turbo` model. You can sign up for an API key at [OpenAI's website](https://platform.openai.com/signup/).
   
   - **Hugging Face API Token**: Ensure your Hugging Face API token has **Read** permissions. Follow the [Hugging Face Token Creation Guide](#creating-a-hugging-face-api-token) to generate one.

## Running the Application

Start the Flask application by running:

```bash
python app.py
```

The application will be available at `http://localhost:5000/`.

## Project Structure

```
proposal-generator/
├── app.py
├── tasks.py
├── templates/
│   ├── index.html
│   └── proposal.html
├── static/
│   └── images/
├── requirements.txt
└── .env
```

- **app.py**: The main Flask application.
- **tasks.py**: Contains functions for generating the proposal and image.
- **templates/**: HTML templates for rendering web pages.
- **static/images/**: Directory where generated images are saved.
- **requirements.txt**: Lists all the Python dependencies.
- **.env**: Contains environment variables (not checked into version control).

## Detailed Code Explanation

### app.py

This is the main Flask application that handles HTTP requests and routes.

```python
# app.py
import os
from flask import Flask, render_template, request, url_for, flash
import logging
from tasks import generate_proposal_and_image
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get and validate form data
        proposal_type = request.form.get('proposal_type', '').strip()
        recipient_name = request.form.get('recipient_name', '').strip()
        themes = request.form.get('themes', '').strip()
        additional_details = request.form.get('additional_details', '').strip()

        # Input validation
        errors = []
        if not proposal_type:
            errors.append('Proposal type is required.')
        if proposal_type.lower() not in ['marriage', 'friendship', 'business', 'other']:
            errors.append('Please select a valid proposal type.')
        if not recipient_name:
            errors.append('Recipient\'s name is required.')
        if not themes:
            errors.append('Please specify at least one theme.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('index.html')

        try:
            logger.info("Form submitted. Generating proposal and image.")
            # Generate proposal and image
            result = generate_proposal_and_image(
                proposal_type, recipient_name, themes, additional_details
            )
            if 'error' in result:
                raise Exception(result['error'])

            proposal = result.get('proposal')
            image_filename = result.get('image_filename')
            image_url = url_for('static', filename=f'images/{image_filename}')
            logger.info(f"Generated image URL: {image_url}")

            return render_template('proposal.html', proposal=proposal, image_url=image_url)

        except Exception as e:
            logger.error(f"Error generating proposal: {e}")
            flash('An error occurred while generating your proposal. Please try again.', 'error')
            return render_template('index.html')

    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

**Key Functions:**

- `index()`: Handles GET and POST requests to the root URL. It collects user input, validates it, and calls `generate_proposal_and_image()` to generate the content.

### tasks.py

Contains the core logic for generating the proposal text and image using OpenAI's and Hugging Face's APIs.

```python
import os
import openai
from PIL import Image
from io import BytesIO
import uuid
import logging
from typing import Dict
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
required_env_vars = {
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
    'HUGGINGFACE_API_TOKEN': os.environ.get('HUGGINGFACE_API_TOKEN'),
}
missing_vars = [var for var, value in required_env_vars.items() if not value]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

openai.api_key = required_env_vars['OPENAI_API_KEY']
hf_token = required_env_vars['HUGGINGFACE_API_TOKEN']

class ProposalGenerationError(Exception):
    """Custom exception for proposal generation errors"""
    pass

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_proposal(proposal_type: str, recipient_name: str, themes: str, additional_details: str) -> str:
    """Generate a proposal using OpenAI's GPT-3.5-turbo model with retry logic."""
    try:
        logger.info("Starting proposal generation.")
        # Sanitize inputs
        proposal_type = proposal_type.strip().lower()
        recipient_name = recipient_name.strip()
        themes = themes.strip()
        additional_details = additional_details.strip()

        # Create the prompt for the proposal
        prompt = f"""
        Write a heartfelt {proposal_type} proposal to {recipient_name}.
        Themes: {themes}
        Additional context: {additional_details}

        Please ensure the proposal is:
        - Sincere and genuine
        - Approximately 300 words
        - Positive and uplifting
        - Appropriate for the nature of a {proposal_type} proposal
        """

        # Generate the proposal using GPT-3.5-turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an expert in crafting {proposal_type} proposals that are heartfelt and appropriate."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )

        proposal = response['choices'][0]['message']['content'].strip()
        logger.info("Proposal generated successfully.")
        return proposal

    except Exception as e:
        logger.error(f"Proposal generation failed: {str(e)}")
        raise ProposalGenerationError(f"Failed to generate proposal: {str(e)}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_image(proposal_type: str, themes: str) -> str:
    """Generate an image using Hugging Face's Stable Diffusion via Inference API with retry logic."""
    try:
        logger.info("Starting image generation.")
        # Initialize the InferenceClient
        inference = InferenceClient(token=hf_token)

        # Create the prompt for image generation
        safe_prompt = f"A beautiful image representing the theme: {themes}. Style: Romantic, uplifting, suitable for a {proposal_type} proposal. Content: Safe, positive themes."

        # Generate the image using Stable Diffusion
        logger.info(f"Sending request to Hugging Face with prompt: {safe_prompt}")
        image = inference.text_to_image(
            model="stabilityai/stable-diffusion-2-1",
            prompt=safe_prompt,
            num_inference_steps=50,
            guidance_scale=7.5
        )

        # Validate the response type
        if isinstance(image, Image.Image):
            logger.info("Image generation successful. Saving the image.")
            # Create a unique filename for the image
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}.png"

            # Define the directory to save images
            base_dir = Path(__file__).resolve().parent
            images_dir = base_dir / 'static' / 'images'
            images_dir.mkdir(parents=True, exist_ok=True)

            # Save the image as PNG
            image_path = images_dir / filename
            image.save(image_path, format='PNG', optimize=True)
            logger.info(f"Image generated and saved as {filename}.")
            return filename
        else:
            logger.error(f"Unexpected response type: {type(image)}")
            raise ValueError(f"Unexpected response type: {type(image)}")

    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        raise ProposalGenerationError(f"Failed to generate image: {str(e)}")

def generate_proposal_and_image(
    proposal_type: str,
    recipient_name: str,
    themes: str,
    additional_details: str
) -> Dict[str, str]:
    """Generate both proposal and image, handling any errors."""
    try:
        logger.info("Initiating proposal and image generation process.")
        # Generate the proposal text
        proposal = generate_proposal(proposal_type, recipient_name, themes, additional_details)

        # Generate and save the image
        image_filename = generate_image(proposal_type, themes)

        logger.info("Proposal and image generation process completed successfully.")
        return {
            'proposal': proposal,
            'image_filename': image_filename
        }

    except ProposalGenerationError as e:
        logger.error(f"Proposal and image generation failed: {str(e)}")
        return {'error': str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {'error': 'An unexpected error occurred.'}
```

**Key Functions:**

- `generate_proposal()`: Uses `gpt-3.5-turbo` to create a personalized proposal based on user input.
- `generate_image()`: Uses Hugging Face's Stable Diffusion to generate an image that matches the themes provided.
- `generate_proposal_and_image()`: Orchestrates the calls to generate both the proposal and image, handling exceptions and retries.

### Templates

#### index.html

The form where users input their proposal details.

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Create Your Proposal</title>
</head>
<body>
    <h1>Create Your Proposal</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <ul class="flashes">
                {% for category, message in messages %}
                    <li class="{{ category }}">{{ message }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    {% endwith %}
    <form method="POST">
        <label for="proposal_type">Proposal Type:</label>
        <select name="proposal_type" id="proposal_type" required>
            <option value="">Select...</option>
            <option value="Marriage">Marriage</option>
            <option value="Friendship">Friendship</option>
            <option value="Business">Business</option>
            <option value="Other">Other</option>
        </select>
        <br><br>

        <label for="recipient_name">Recipient's Name:</label>
        <input type="text" id="recipient_name" name="recipient_name" required>
        <br><br>

        <label for="themes">Themes (comma-separated):</label>
        <input type="text" id="themes" name="themes" required>
        <br><br>

        <label for="additional_details">Additional Details (optional):</label>
        <textarea id="additional_details" name="additional_details"></textarea>
        <br><br>

        <button type="submit">Generate Proposal</button>
    </form>
</body>
</html>
```

#### proposal.html

Displays the generated proposal and image.

```html
<!-- templates/proposal.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Your Generated Proposal</title>
</head>
<body>
    <h1>Your Proposal</h1>
    <div>
        <p>{{ proposal | safe }}</p>
    </div>
    <div>
        <img src="{{ image_url }}" alt="Generated Image">
    </div>
    <a href="{{ url_for('index') }}">Create Another Proposal</a>
</body>
</html>
```

## Usage

1. **Navigate to the Application**

   Open your web browser and go to `http://localhost:5000/`.

2. **Fill Out the Form**

   - **Proposal Type**: Select the type of proposal (e.g., Marriage, Friendship, Business, Other).
   - **Recipient's Name**: Enter the name of the person the proposal is for.
   - **Themes**: Specify one or more themes (e.g., love, partnership, collaboration).
   - **Additional Details** (optional): Provide any extra information to personalize the proposal.

3. **Generate Proposal**

   Click the "Generate Proposal" button. The application will process your input and generate both the proposal text and an accompanying image.

4. **View Results**

   The generated proposal and image will be displayed on a new page. You can read the proposal and see the image that was created based on your themes.

5. **Create Another Proposal**

   Click on "Create Another Proposal" to return to the form and generate more proposals.

## Notes

- **Error Handling**: If there's an error during the generation process (e.g., API issues), an error message will be displayed, and you can try again.
- **Data Storage**: Generated images are stored in the `static/images` directory. Be aware of storage usage if generating a large number of images.
- **API Usage**: Keep in mind OpenAI's and Hugging Face's API usage policies and rate limits. Excessive use may incur costs or be throttled.

## Troubleshooting

- **Invalid API Key**: Ensure your OpenAI and Hugging Face API keys are correct and have the necessary permissions.
- **API Access Issues**: If you encounter model availability errors, check if your API keys have access to `gpt-3.5-turbo` and the Stable Diffusion model on Hugging Face.
- **Module Not Found**: Make sure all dependencies are installed using `pip install -r requirements.txt`.
- **Permission Errors**: Ensure the `static/images` directory exists and has the correct permissions.
- **Network Issues**: Verify your internet connection and firewall settings.
- **Hugging Face Rate Limits**: If you hit rate limits, wait for a while before retrying or consider upgrading your Hugging Face plan.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Disclaimer**: This application is intended for educational purposes. Ensure compliance with OpenAI's and Hugging Face's policies and terms of service when using their APIs.

# Acknowledgments

- [OpenAI](https://openai.com/) for providing powerful AI models.
- [Hugging Face](https://huggingface.co/) for providing accessible AI models and APIs.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Tenacity](https://tenacity.readthedocs.io/) for retry logic.
- [Python Dotenv](https://saurabh-kumar.com/python-dotenv/) for managing environment variables.

# Students

Feel free to explore the code, modify it, and experiment with additional features. This project demonstrates how to integrate accessible AI models into web applications. Happy coding!

---

## Creating a Hugging Face API Token

To use the Proposal Generator Application, you and your students will need to generate your own Hugging Face API tokens. Follow the steps below to create and configure your tokens.

### Step 1: Sign Up or Log In to Hugging Face

1. **Visit Hugging Face:**
   - Go to [Hugging Face](https://huggingface.co/).

2. **Create an Account:**
   - Click on **"Sign up"** and fill in the necessary details.
   - Verify your email to activate your account.

3. **Log In:**
   - If you already have an account, click **"Log in"** and enter your credentials.

### Step 2: Generate a New API Token

1. **Access Settings:**
   - Click on your profile avatar at the top right corner.
   - Select **"Settings"** from the dropdown menu.

2. **Navigate to Access Tokens:**
   - In the left sidebar, click on **"Access Tokens"** under the **"Access"** section.

3. **Create a New Token:**
   - Click on **"New token"**.

4. **Configure the Token:**
   - **Token Type:** Select **"Fine-grained"**.
   - **Permissions:** 
     - **Read:** **Enable** this permission.
     - **Write:** **Do not enable** this permission as it's unnecessary for generating images.
   - **Note:** **Fine-grained tokens offer enhanced security** by allowing you to specify exact permissions.

5. **Generate and Copy the Token:**
   - Click **"Generate"**.
   - **Copy the token immediately** as it will not be shown again.

### Step 3: Store the Token Securely

1. **Create a `.env` File:**
   - In your project directory, create a `.env` file if it doesn't exist.
   
   ```bash
   touch .env
   ```

2. **Add the Token to `.env`:**
   
   ```env
   HUGGINGFACE_API_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

   - Replace `hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` with your actual token.

3. **Ensure `.env` is Ignored by Git:**
   
   - Add `.env` to your `.gitignore` to prevent accidental exposure.
   
   ```bash
   echo ".env" >> .gitignore
   ```

### Step 4: Verify the Token

1. **Run the Test Script:**
   
   Use the provided `test_hf_token.py` script to ensure your token works correctly.

   ```python
   # test_hf_token.py
   from huggingface_hub import InferenceClient
   from PIL import Image
   import os
   from dotenv import load_dotenv
   from pathlib import Path

   # Load environment variables
   load_dotenv()

   hf_token = os.environ.get('HUGGINGFACE_API_TOKEN')

   if not hf_token:
       raise EnvironmentError("HUGGINGFACE_API_TOKEN not found in environment variables.")

   inference = InferenceClient(token=hf_token)

   prompt = "A serene landscape with mountains and a river."

   try:
       print("Generating image...")
       image = inference.text_to_image(
           model="stabilityai/stable-diffusion-2-1",
           prompt=prompt,
           num_inference_steps=50,
           guidance_scale=7.5
       )
       if isinstance(image, Image.Image):
           unique_id = "test_image"
           filename = f"{unique_id}.png"
           images_dir = Path(__file__).resolve().parent / 'static' / 'images'
           images_dir.mkdir(parents=True, exist_ok=True)
           image_path = images_dir / filename
           image.save(image_path, format='PNG', optimize=True)
           print(f"Image generated and saved as {filename}.")
       else:
           print(f"Unexpected response type: {type(image)}")
   except Exception as e:
       print(f"Image generation failed: {e}")
   ```

2. **Run the Test Script:**

   ```bash
   python test_hf_token.py
   ```

3. **Check the Output:**

   - An image should be generated and saved in the `static/images` directory.
   - The console should display "Image generated and saved as test_image.png."

   If the script fails, double-check the token and ensure it has the correct permissions.
