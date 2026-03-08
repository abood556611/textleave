import os
import uuid
import json
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from config import Config
from video_generator import create_video, VideoGenerator
from oxapay_service import create_payment_session, verify_payment_session
import threading

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Store video generation progress
video_progress = {}


def allowed_file(filename):
    """Check if file has allowed extension"""
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html', config={
        'durations': Config.AVAILABLE_DURATIONS,
        'fps_options': Config.AVAILABLE_FPS,
        'resolutions': list(Config.RESOLUTIONS.keys()),
        'whatsapp': Config.WHATSAPP_NUMBER,
        'monthly_price': Config.MONTHLY_PRICE,
        'yearly_price': Config.YEARLY_PRICE
    })


@app.route('/api/calculate', methods=['POST'])
def calculate_video_info():
    """Calculate video information based on duration"""
    data = request.get_json()
    duration = int(data.get('duration', 10))
    
    info = VideoGenerator.calculate_video_info(duration)
    
    return jsonify(info)


@app.route('/api/generate', methods=['POST'])
def generate_video():
    """Generate video endpoint"""
    
    # Get form data
    main_text = request.form.get('main_text', '').strip()
    duration = int(request.form.get('duration', 10))
    fps = int(request.form.get('fps', 30))
    resolution = request.form.get('resolution', '9:16')
    is_premium = request.form.get('premium', 'false').lower() == 'true'
    
    # Validation
    if not main_text:
        return jsonify({'error': 'Main text is required'}), 400
    
    if duration not in Config.AVAILABLE_DURATIONS:
        return jsonify({'error': 'Invalid duration'}), 400
    
    if fps not in Config.AVAILABLE_FPS:
        return jsonify({'error': 'Invalid FPS'}), 400
    
    if resolution not in Config.RESOLUTIONS:
        return jsonify({'error': 'Invalid resolution'}), 400
    
    # Handle audio file upload
    audio_path = None
    if 'audio_file' in request.files:
        audio_file = request.files['audio_file']
        if audio_file and audio_file.filename and allowed_file(audio_file.filename):
            filename = secure_filename(audio_file.filename)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}_{filename}")
            audio_file.save(audio_path)
    
    # Generate unique video ID
    video_id = uuid.uuid4().hex
    output_filename = f"video_{video_id}.mp4"
    
    # Initialize progress
    video_progress[video_id] = {
        'progress': 0,
        'status': 'starting',
        'filename': output_filename
    }
    
    # Progress callback
    def update_progress(progress, status):
        video_progress[video_id] = {
            'progress': progress,
            'status': status,
            'filename': output_filename
        }
    
    # Generate video in background thread
    def generate_in_background():
        try:
            add_watermark = not is_premium
            
            output_path = create_video(
                main_text=main_text,
                duration=duration,
                fps=fps,
                resolution=resolution,
                output_filename=output_filename,
                audio_path=audio_path,
                add_watermark=add_watermark,
                progress_callback=update_progress
            )
            
            video_progress[video_id]['status'] = 'complete'
            video_progress[video_id]['progress'] = 100
            video_progress[video_id]['output_path'] = output_path
            
        except Exception as e:
            video_progress[video_id]['status'] = 'error'
            video_progress[video_id]['error'] = str(e)
        
        finally:
            # Clean up uploaded audio file
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass
    
    # Start generation in background
    thread = threading.Thread(target=generate_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'video_id': video_id,
        'message': 'Video generation started'
    })


@app.route('/api/progress/<video_id>', methods=['GET'])
def get_progress(video_id):
    """Get video generation progress"""
    if video_id not in video_progress:
        return jsonify({'error': 'Video ID not found'}), 404
    
    return jsonify(video_progress[video_id])


@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    """Download generated video"""
    if video_id not in video_progress:
        return jsonify({'error': 'Video ID not found'}), 404
    
    progress_info = video_progress[video_id]
    
    if progress_info['status'] != 'complete':
        return jsonify({'error': 'Video not ready yet'}), 400
    
    output_path = progress_info.get('output_path')
    
    if not output_path or not os.path.exists(output_path):
        return jsonify({'error': 'Video file not found'}), 404
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name=progress_info['filename'],
        mimetype='video/mp4'
    )


@app.route('/api/subscription/create', methods=['POST'])
def create_subscription():
    """Create subscription payment"""
    data = request.get_json()
    plan = data.get('plan', 'monthly')  # monthly or yearly
    user_id = data.get('user_id')  # Optional user identifier
    
    # Create payment session with OxaPay
    result = create_payment_session(plan, user_id)
    
    if result.get('success'):
        return jsonify({
            'success': True,
            'payment_id': result['payment_id'],
            'amount': result['amount'],
            'currency': result['currency'],
            'payment_url': result['payment_url'],
            'expires_at': result['expires_at']
        })
    
    return jsonify({
        'success': False,
        'error': result.get('error', 'Failed to create payment')
    }), 400


@app.route('/api/subscription/verify', methods=['POST'])
def verify_subscription():
    """Verify subscription payment"""
    data = request.get_json()
    track_id = data.get('track_id') or data.get('payment_id')
    
    if not track_id:
        return jsonify({'error': 'Track ID is required'}), 400
    
    # Verify payment with OxaPay
    result = verify_payment_session(track_id)
    
    if result.get('verified'):
        return jsonify({
            'verified': True,
            'subscription_active': True,
            'status': result['status'],
            'amount': result['amount'],
            'currency': result['currency']
        })
    
    return jsonify({
        'verified': False,
        'error': result.get('error', 'Payment verification failed')
    }), 400


@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    """Handle OxaPay payment callback"""
    data = request.get_json()
    
    # Log payment callback
    track_id = data.get('trackId')
    status = data.get('status')
    amount = data.get('amount')
    
    # Here you would update your database with payment status
    # For now, just log it
    print(f"Payment callback: {track_id} - {status} - {amount}")
    
    return jsonify({'success': True})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
