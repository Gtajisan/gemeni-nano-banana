# AI Photo Editor - Gemini Nano-Banana

## Overview
This is a web-based AI photo editing application powered by Gemini's Nano-Banana image editing model. Users can upload images and edit them using natural language prompts through a ChatGPT-style interface.

## Features
- 🎨 AI-powered image editing using Gemini API
- 📤 Simple drag-and-drop image upload
- 💬 Chat-style interface for intuitive interaction
- ✨ Edit images with natural language prompts
- 🚀 Fast processing with external API endpoint

## Tech Stack
- **Backend**: Python Flask
- **AI API**: Gemini Nano-Banana (via tawsif.is-a.dev)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Ready for Render deployment

## Project Structure
```
.
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Chat-style UI
├── static/
│   └── style.css         # Styling
├── uploads/              # Temporary image uploads
├── requirements.txt      # Python dependencies
└── .gitignore           # Git ignore file
```

## How to Use
1. Upload an image by clicking the "Upload Image" button
2. Enter a natural language prompt describing how you want to edit the image
3. Click "Edit Image" to process
4. View the edited result in the chat interface

## Example Prompts
- "Change background to beach sunset"
- "Add sunglasses to the person"
- "Make it black and white"
- "Remove background"
- "Add a vintage film effect"

## API Endpoint
Uses the public Gemini Nano-Banana API at:
`https://tawsif.is-a.dev/gemini/nano-banana`

## Deployment to Render
This application is configured for easy deployment to Render. The app runs on port 5000 and includes all necessary configuration files.

## Recent Changes
- 2025-11-16: Created AI photo editing web application
- 2025-11-16: Integrated with Gemini Nano-Banana API
- 2025-11-16: Added chat-style UI with upload functionality
- 2025-11-16: Configured for Render deployment
