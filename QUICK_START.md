# 🚀 Quick Start Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- Groq API key
- Unsplash API key

## 1. Get API Keys

### Groq API
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up and create an account
3. Generate an API key
4. Copy the key

### Unsplash API
1. Visit [Unsplash Developers](https://unsplash.com/developers)
2. Create a developer account
3. Create a new application
4. Copy your Access Key

## 2. Setup Environment

```bash
# Run the setup script
./setup.sh

# Or manually:
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_actual_groq_key" > .env
echo "UNSPLASH_ACCESS_KEY=your_actual_unsplash_key" >> .env

cd ../frontend
npm install
```

## 3. Start the Application

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## 4. Use the App

1. Open [http://localhost:5173](http://localhost:5173) in your browser
2. Enter a YouTube video idea (e.g., "How to make the perfect pizza")
3. Click "Generate Thumbnails"
4. Select a thumbnail you like
5. Use the action buttons to regenerate images or text

## Troubleshooting

### Backend Issues
- Make sure your API keys are correct in `backend/.env`
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Ensure the backend is running on port 8000

### Frontend Issues
- Make sure Node.js dependencies are installed: `npm install`
- Check that the frontend is running on port 5173
- Verify the proxy configuration in `vite.config.js`

### API Issues
- Groq API: Check your API key and rate limits
- Unsplash API: Verify your Access Key and usage limits

## API Endpoints

- `POST /api/generate-thumbnails` - Generate 3 thumbnails
- `POST /api/regenerate-images` - New backgrounds, same text
- `POST /api/regenerate-all` - New text and images

## Features

✅ AI-powered text generation  
✅ Dynamic image search  
✅ Professional text overlay  
✅ Multiple regeneration options  
✅ Responsive design  
✅ Real-time preview  

🎉 **Enjoy creating stunning YouTube thumbnails!** 