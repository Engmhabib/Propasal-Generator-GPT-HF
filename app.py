# app.py
import os
from flask import Flask, render_template, request, url_for, flash
import logging
from tasks import generate_proposal_and_image
from datetime import timedelta

app = Flask(__name__)
# Use a proper secret key in production
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
            # Generate proposal and image
            result = generate_proposal_and_image(
                proposal_type, recipient_name, themes, additional_details
            )
            if 'error' in result:
                raise Exception(result['error'])

            proposal = result.get('proposal')
            image_filename = result.get('image_filename')
            image_url = url_for('static', filename=f'images/{image_filename}')

            return render_template('proposal.html', proposal=proposal, image_url=image_url)

        except Exception as e:
            logger.error(f"Error generating proposal: {e}")
            flash('An error occurred while generating your proposal. Please try again.', 'error')
            return render_template('index.html')

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
