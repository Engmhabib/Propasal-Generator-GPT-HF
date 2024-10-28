# tasks.py
import os
import openai
from PIL import Image
from io import BytesIO
import uuid
import logging
import requests
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

# Load and validate environment variables
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
        # Initialize the InferenceClient
        inference = InferenceClient(token=hf_token)

        # Create the prompt for image generation
        safe_prompt = f"A beautiful image representing the theme: {themes}. Style: Romantic, uplifting, suitable for a {proposal_type} proposal. Content: Safe, positive themes."

        # Generate the image using Stable Diffusion
        image = inference.text_to_image(
            model="stabilityai/stable-diffusion-2-1",
            prompt=safe_prompt,
            num_inference_steps=50,
            guidance_scale=7.5
        )

        # Validate the response type
        if isinstance(image, Image.Image):
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
        # Generate the proposal text
        proposal = generate_proposal(proposal_type, recipient_name, themes, additional_details)

        # Generate and save the image
        image_filename = generate_image(proposal_type, themes)

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
