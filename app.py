import os
import io
import base64
import requests
import uuid
from urllib.parse import quote
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.urandom(24)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
API_ENDPOINT = 'https://tawsif.is-a.dev/gemini/nano-banana'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/edit-image', methods=['POST'])
def edit_image():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400
        
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            return jsonify({'success': False, 'error': 'Please provide an editing prompt'}), 400
        
        file = request.files['image']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No image selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Use PNG, JPG, JPEG, GIF, or WEBP'}), 400

        filename = f"{uuid.uuid4().hex}.{file.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        replit_domain = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        image_url = f"https://{replit_domain}/uploads/{filename}"
        
        logging.info(f"Processing image edit request with prompt: {prompt}")
        logging.info(f"Image URL: {image_url}")
        
        api_url = f"{API_ENDPOINT}?prompt={quote(prompt)}&url={quote(image_url)}"
        
        response = requests.get(api_url, timeout=60)
        
        try:
            os.remove(filepath)
        except:
            pass
        
        if response.status_code != 200:
            logging.error(f"API returned status {response.status_code}: {response.text}")
            return jsonify({
                'success': False, 
                'error': f'API error: {response.status_code}'
            }), 500
        
        result = response.json()
        logging.info(f"API response: {result}")
        
        if result.get('success') and 'imageUrl' in result:
            return jsonify({
                'success': True,
                'image': result['imageUrl'],
                'message': 'Image edited successfully!'
            })
        elif not result.get('success'):
            error_msg = result.get('error', 'Unknown error from API')
            logging.error(f"API returned error: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'No image in API response'
            }), 500
        
    except requests.Timeout:
        logging.error("API request timeout")
        return jsonify({'success': False, 'error': 'Request timeout - image processing took too long'}), 500
    except requests.RequestException as e:
        logging.error(f"API request error: {str(e)}")
        return jsonify({'success': False, 'error': f'API error: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Error editing image: {str(e)}")
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'api_endpoint': API_ENDPOINT})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
