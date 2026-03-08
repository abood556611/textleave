# TextLeaf API Documentation

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. Homepage
```
GET /
```
Returns the main HTML page.

---

### 2. Calculate Video Info
```
POST /api/calculate
```

Calculate video information based on duration.

**Request Body:**
```json
{
  "duration": 10
}
```

**Response:**
```json
{
  "duration": 10,
  "num_pages": 20,
  "page_duration": 0.5,
  "fps_options": [30, 60]
}
```

---

### 3. Generate Video
```
POST /api/generate
```

Generate a new video.

**Request (multipart/form-data):**
- `main_text` (required): The main text to display
- `duration` (required): Video duration (5, 10, or 15 seconds)
- `fps` (required): Frames per second (30 or 60)
- `resolution` (required): Video resolution (9:16, 16:9, or 1:1)
- `premium` (optional): "true" for premium (no watermark, 1080p)
- `audio_file` (optional): Audio file (mp3, wav, ogg, m4a)

**Example:**
```bash
curl -X POST http://localhost:5000/api/generate \
  -F "main_text=Hello World" \
  -F "duration=10" \
  -F "fps=30" \
  -F "resolution=9:16" \
  -F "premium=false"
```

**Response:**
```json
{
  "video_id": "abc123def456",
  "message": "Video generation started"
}
```

---

### 4. Get Generation Progress
```
GET /api/progress/<video_id>
```

Get the progress of video generation.

**Response:**
```json
{
  "progress": 75,
  "status": "Processing page 15/20...",
  "filename": "video_abc123def456.mp4"
}
```

**Status values:**
- `starting`: Generation is starting
- `Generating pages...`: Creating page images
- `Processing page X/Y...`: Converting pages
- `Combining clips...`: Merging video
- `Adding audio...`: Adding audio track
- `Rendering video...`: Final rendering
- `Cleaning up...`: Cleanup
- `Complete!`: Video is ready
- `error`: Generation failed

---

### 5. Download Video
```
GET /api/download/<video_id>
```

Download the generated video.

**Response:**
- Content-Type: `video/mp4`
- Content-Disposition: `attachment; filename="video_abc123def456.mp4"`

**Example:**
```bash
curl -O http://localhost:5000/api/download/abc123def456
```

---

### 6. Create Subscription
```
POST /api/subscription/create
```

Create a new subscription payment.

**Request Body:**
```json
{
  "plan": "monthly",
  "user_id": "optional_user_id"
}
```

**Plans:**
- `monthly`: $5/month
- `yearly`: $50/year

**Response:**
```json
{
  "success": true,
  "payment_id": "xyz789",
  "amount": 5,
  "currency": "USD",
  "payment_url": "https://pay.oxapay.com/...",
  "expires_at": "2024-03-08T10:30:00Z"
}
```

---

### 7. Verify Subscription
```
POST /api/subscription/verify
```

Verify a subscription payment.

**Request Body:**
```json
{
  "track_id": "xyz789"
}
```

**Response:**
```json
{
  "verified": true,
  "subscription_active": true,
  "status": "Paid",
  "amount": 5,
  "currency": "USD"
}
```

---

### 8. Payment Callback (Webhook)
```
POST /api/payment/callback
```

Receives payment notifications from OxaPay.

**Request Body (from OxaPay):**
```json
{
  "trackId": "xyz789",
  "status": "Paid",
  "amount": 5,
  "currency": "USD"
}
```

---

## Error Responses

All endpoints may return errors in the following format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Video Generation Flow

1. **Submit video generation request** → `POST /api/generate`
2. **Receive video_id** → `{"video_id": "abc123"}`
3. **Poll for progress** → `GET /api/progress/abc123` (every 1-2 seconds)
4. **Wait for completion** → `{"status": "Complete!"}`
5. **Download video** → `GET /api/download/abc123`

---

## Subscription Flow

1. **Create payment** → `POST /api/subscription/create`
2. **Redirect user** → Open `payment_url` in browser
3. **User pays** → OxaPay payment page
4. **Webhook callback** → `POST /api/payment/callback` (automatic)
5. **Verify payment** → `POST /api/subscription/verify`
6. **Enable premium** → User can use premium features

---

## Configuration Options

### Durations
- 5 seconds (10 pages)
- 10 seconds (20 pages)
- 15 seconds (30 pages)

### FPS Options
- 30 FPS (standard)
- 60 FPS (smooth)

### Resolutions
- 9:16 (1080x1920) - Vertical for Instagram/TikTok
- 16:9 (1920x1080) - Horizontal for YouTube
- 1:1 (1080x1080) - Square for social media

### Free vs Premium

**Free Tier:**
- Watermark: "TextLeaf.com"
- Resolution: 720p
- All durations and ratios

**Premium Tier ($5/month or $50/year):**
- No watermark
- Resolution: 1080p
- Green Screen option (coming soon)
- Priority processing

---

## Rate Limits

No rate limits currently enforced in development.

For production:
- Free tier: 10 videos/day
- Premium: Unlimited

---

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- M4A (.m4a)

Maximum file size: 50MB

---

## Example Integration

### JavaScript (Fetch API)

```javascript
// Generate video
async function generateVideo(mainText, duration, fps, resolution) {
    const formData = new FormData();
    formData.append('main_text', mainText);
    formData.append('duration', duration);
    formData.append('fps', fps);
    formData.append('resolution', resolution);
    formData.append('premium', 'false');
    
    const response = await fetch('/api/generate', {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    return data.video_id;
}

// Poll for progress
async function checkProgress(videoId) {
    const response = await fetch(`/api/progress/${videoId}`);
    const data = await response.json();
    return data;
}

// Download video
function downloadVideo(videoId) {
    window.location.href = `/api/download/${videoId}`;
}
```

### Python (requests)

```python
import requests
import time

# Generate video
response = requests.post('http://localhost:5000/api/generate', data={
    'main_text': 'Hello World',
    'duration': 10,
    'fps': 30,
    'resolution': '9:16',
    'premium': 'false'
})

video_id = response.json()['video_id']

# Poll for completion
while True:
    progress = requests.get(f'http://localhost:5000/api/progress/{video_id}').json()
    print(f"Progress: {progress['progress']}% - {progress['status']}")
    
    if progress['status'] == 'Complete!':
        break
    
    time.sleep(2)

# Download video
video = requests.get(f'http://localhost:5000/api/download/{video_id}')
with open('output.mp4', 'wb') as f:
    f.write(video.content)
```

---

## Support

For technical support:
- WhatsApp: +963 958 917 677
- Email: support@textleaf.com (coming soon)

## Payment Support

For payment issues:
- Supported networks: BSC, TRX, ETH, POLYGON, AVAX, BTC, LTC
- Currency: USDT
- Payment provider: OxaPay
