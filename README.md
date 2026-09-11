# 🐕 Dog Breed Detector

Detect dog breeds from images using AI powered by YOLOv8 and the Dog CEO API.

## Features

✅ **Fast Detection** - Analyzes images in 2-5 seconds  
✅ **High Accuracy** - YOLOv8 specialized in dog detection  
✅ **Free** - No API keys or paid services required  
✅ **Bilingual** - English and Spanish support  
✅ **Responsive** - Works on desktop, tablet, and mobile  
✅ **Rich Info** - Breed characteristics and images  
✅ **Export** - Download results as CSV  

## Tech Stack

- **Frontend**: HTML5, Tailwind CSS, Chart.js, Vanilla JavaScript
- **Backend**: Python Flask, YOLOv8, OpenCV
- **API**: Dog CEO (free dog images and info)
- **Hosting**: Hostinger (or any Python-capable host)

## Installation

### 1. Clone/Setup Project
```bash
cd dog-breed-detector
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Flask (lightweight backend)
- YOLOv8 (object detection model)
- OpenCV (image processing)
- Requests (API calls)
- Flask-CORS (enable cross-origin requests)

### 4. Download YOLOv8 Model
The model will auto-download on first run (~80MB). To pre-download:
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
python server.py
```
Backend runs on `http://localhost:5000`

**Terminal 2 - Frontend:**
Simply open `index.html` in your browser or serve it:
```bash
# Python 3
python -m http.server 8000

# Then visit http://localhost:8000
```

## Usage

1. **Upload Image** - Click or drag a dog image
2. **Analyze** - Click the analyze button
3. **View Results** - See breed detection with:
   - Confidence percentage
   - Breed distribution chart
   - Breed characteristics
   - Random breed images from Dog CEO API
4. **Download** - Export results as CSV

## Project Structure

```
dog-breed-detector/
├── server.py              # Flask backend with YOLOv8
├── index.html             # Frontend HTML
├── app.js                 # JavaScript logic
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
└── README.md              # This file
```

## API Endpoints

### POST /analyze
Analyzes uploaded dog image.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "breeds": [
    {
      "breed": "Golden Retriever",
      "confidence": 87.5,
      "image_url": "https://...",
      "characteristics": {
        "size": "Large",
        "temperament": "Friendly, Intelligent, Devoted",
        "lifespan": "10-12 years",
        "origin": "Scotland"
      }
    }
  ],
  "total_breeds": 1
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Deployment to Hostinger

### 1. Using Hostinger Hatchling Plan

1. Connect via SFTP
2. Upload project files
3. Create virtual environment on server
4. Install requirements
5. Use Hostinger's application manager or set up using supervisord

### 2. Using Heroku (Alternative)

```bash
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
```

### 3. Environment Variables

Set these on your host:
```
FLASK_ENV=production
API_PORT=5000
```

## Performance Tips

- **Optimize Images**: Resize large images before upload (max 1080p)
- **Cache Results**: Browser stores last upload locally
- **Use GPU**: If available, YOLOv8 will use GPU (CUDA)
- **Model Size**: Using `yolov8n` (nano) for faster inference. Upgrade to `yolov8m` (medium) for better accuracy

## Troubleshooting

### 1. "No module named 'ultralytics'"
```bash
pip install ultralytics
```

### 2. "Connection refused" on API
Make sure backend is running:
```bash
python server.py
```

### 3. CORS Errors
Update `.env`:
```
CORS_ORIGINS=http://localhost:8000
```

### 4. Slow Detection
- Close other applications
- Use a smaller image
- Upgrade model: `yolov8m.pt` instead of `yolov8n.pt`

## Future Enhancements

- [ ] Multi-dog detection in single image
- [ ] Real-time webcam detection
- [ ] Breed comparison tool
- [ ] Model fine-tuning on custom dataset
- [ ] Mobile app (React Native)
- [ ] Database for results history
- [ ] Advanced filtering and search

## License

Free for personal and commercial use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Flask/YOLOv8 documentation
3. Check Dog CEO API status

## Credits

- **YOLOv8**: Ultralytics
- **Dog Images**: Dog CEO API
- **Frontend**: Tailwind CSS, Chart.js
- **Backend**: Flask

---

Made with ❤️ and 🐕
