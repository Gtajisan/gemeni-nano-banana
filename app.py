import os
import io
import base64
from flask import Flask, render_template, request, jsonify, send_file
from google import genai
from google.genai import types
from PIL import Image
from werkzeug.utils import secure_filename
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.urandom(24)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    logging.error("GEMINI_API_KEY not found in environment variables")
    client = None
else:
    client = genai.Client(api_key=api_key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edit-image', methods=['POST'])
def edit_image():
    try:
        if not client:
            return jsonify({
                'success': False,
                'error': 'GEMINI_API_KEY not configured. Please add your API key in the Secrets tab.'
            }), 500

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

        image_bytes = file.read()
        filename = file.filename
        
        mime_type = f"image/{filename.rsplit('.', 1)[1].lower()}"
        if mime_type == 'image/jpg':
            mime_type = 'image/jpeg'
        
        logging.info(f"Processing image edit request with prompt: {prompt}")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE']
            )
        )
        
        if not response.candidates or not response.candidates[0].content:
            return jsonify({'success': False, 'error': 'No response from AI'}), 500
        
        content = response.candidates[0].content
        if not content.parts:
            return jsonify({'success': False, 'error': 'No image generated'}), 500
        
        for part in content.parts:
            if part.inline_data and part.inline_data.data:
                edited_image_bytes = part.inline_data.data
                edited_image_base64 = base64.b64encode(edited_image_bytes).decode('utf-8')
                
                return jsonify({
                    'success': True,
                    'image': f"data:image/png;base64,{edited_image_base64}",
                    'message': 'Image edited successfully!'
                })
        
        return jsonify({'success': False, 'error': 'No image in response'}), 500
        
    except Exception as e:
        logging.error(f"Error editing image: {str(e)}")
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'api_configured': client is not None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
