# 🎬 AI Thumbnail Generator

A full-stack web application that generates stunning YouTube thumbnails using AI. Built with React (frontend) and FastAPI (backend).

## ✨ Features

- **AI-Powered Text Generation**: Uses Groq API to generate engaging headings, subheadings, labels, and dates
- **Dynamic Image Search**: Fetches relevant images from Unsplash based on your video idea
- **Smart Text Overlay**: Automatically overlays text on images with professional styling
- **Multiple Regeneration Options**: 
  - 🔁 Regenerate just the images (new backgrounds, same text)
  - ✏️ Regenerate both text and images completely
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Real-time Preview**: See your thumbnails instantly with base64 encoding

## 🛠️ Tech Stack

### Frontend
- **React 19** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client for API calls
- **CSS3** - Modern styling with gradients and animations

### Backend
- **FastAPI** - Modern Python web framework
- **Groq API** - AI text generation
- **Unsplash API** - High-quality stock photos
- **Pillow (PIL)** - Image processing and text overlay
- **Python-dotenv** - Environment variable management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Groq API key
- Unsplash API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-thumbnail-generator
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here" >> .env

# Start the backend server
python main.py
```

The backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:5173`

### 4. Get API Keys

#### Groq API
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up and create an account
3. Generate an API key
4. Add it to your `.env` file

#### Unsplash API
1. Visit [Unsplash Developers](https://unsplash.com/developers)
2. Create a developer account
3. Create a new application
4. Copy your Access Key
5. Add it to your `.env` file

## 📁 Project Structure

```
ai-thumbnail-generator/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── groq.py              # Groq API integration
│   ├── unsplash.py          # Unsplash API integration
│   ├── thumbnail.py         # Image processing and text overlay
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css          # Styling
│   │   └── main.jsx         # React entry point
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
└── README.md
```

## 🔧 API Endpoints

### `POST /api/generate-thumbnails`
Generate 3 thumbnails based on a video idea.

**Request:**
```json
{
  "video_idea": "How to make the perfect pizza at home"
}
```

**Response:**
```json
{
  "thumbnails": ["data:image/png;base64,...", ...],
  "text_data": {
    "heading": "Perfect Pizza Secrets",
    "subheading": "You won't believe these techniques",
    "label": "NEW",
    "date": "2024"
  }
}
```

### `POST /api/regenerate-images`
Regenerate images with new backgrounds but same text.

### `POST /api/regenerate-all`
Regenerate both text and images completely.

## 🎨 How It Works

1. **Text Generation**: The app uses Groq's AI to generate engaging, clickable text elements
2. **Image Search**: Unsplash API finds relevant, high-quality images based on your video idea
3. **Text Overlay**: Pillow (PIL) overlays the generated text on images with professional styling
4. **Base64 Encoding**: Images are converted to base64 for instant display in the frontend
5. **Interactive Selection**: Users can select thumbnails and regenerate specific elements

## 🎯 Usage

1. Enter your YouTube video idea in the text area
2. Click "Generate Thumbnails" to create 3 variations
3. Review the generated text data (heading, subheading, label, date)
4. Click on a thumbnail to select it
5. Use the action buttons to:
   - 🔁 Regenerate just the images (new backgrounds)
   - ✏️ Regenerate everything (new text and images)

## 🔒 Environment Variables

Create a `.env` file in the `backend` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
```

## 🚀 Deployment

### Backend Deployment
- Deploy to platforms like Heroku, Railway, or DigitalOcean
- Set environment variables in your hosting platform
- Install dependencies: `pip install -r requirements.txt`

### Frontend Deployment
- Build the project: `npm run build`
- Deploy the `dist` folder to platforms like Vercel, Netlify, or GitHub Pages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for AI text generation
- [Unsplash](https://unsplash.com/) for high-quality stock photos
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework 