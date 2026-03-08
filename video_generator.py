import os
import tempfile
import traceback
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
from image_generator import ImageGenerator
from config import Config


class VideoGenerator:
    """Generates match-cut style videos from pages"""
    
    def __init__(self, main_text, duration=10, fps=30, resolution='9:16', add_watermark=True):
        """
        Initialize video generator
        
        Args:
            main_text: The main text to display on each page
            duration: Total video duration in seconds
            fps: Frames per second
            resolution: Video resolution ratio (9:16, 16:9, 1:1)
            add_watermark: Whether to add watermark (for free tier)
        """
        self.main_text = main_text
        self.duration = duration
        self.fps = fps
        self.resolution = resolution
        self.add_watermark = add_watermark
        
        # Calculate number of pages
        self.num_pages = int(duration / Config.PAGE_DURATION)
        
        # Initialize image generator
        self.image_gen = ImageGenerator(resolution)
        
        # Get video dimensions
        self.width, self.height = Config.RESOLUTIONS.get(resolution, Config.RESOLUTIONS['9:16'])
    
    def generate_video(self, output_path, audio_path=None, progress_callback=None):
        """
        Generate the complete video
        
        Args:
            output_path: Path to save the output video
            audio_path: Optional path to audio file
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Path to the generated video file
        """
        
        try:
            # Generate all pages
            if progress_callback:
                progress_callback(0, "Generating pages...")
            
            pages = self.image_gen.generate_pages(
                self.main_text,
                self.num_pages,
                self.add_watermark
            )
            
            # Save pages to temporary files
            temp_files = []
            clips = []
            
            for i, page in enumerate(pages):
                if progress_callback:
                    progress = int((i + 1) / self.num_pages * 50)
                    progress_callback(progress, f"Processing page {i+1}/{self.num_pages}...")
                
                # Save page to temp file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                page.save(temp_file.name, 'PNG')
                temp_files.append(temp_file.name)
                
                # Create image clip
                clip = ImageClip(temp_file.name, duration=Config.PAGE_DURATION)
                clips.append(clip)
            
            # Concatenate all clips
            if progress_callback:
                progress_callback(60, "Combining clips...")
            
            video = concatenate_videoclips(clips, method="compose")
            video = video.set_fps(self.fps)
            
            # Add audio if provided
            if audio_path and os.path.exists(audio_path):
                if progress_callback:
                    progress_callback(70, "Adding audio...")
                
                try:
                    audio = AudioFileClip(audio_path)
                    
                    # Loop audio to match video duration
                    if audio.duration < self.duration:
                        num_loops = int(self.duration / audio.duration) + 1
                        audio_clips = [audio] * num_loops
                        audio = concatenate_videoclips(audio_clips)
                    
                    # Trim audio to match video duration
                    audio = audio.subclip(0, self.duration)
                    
                    # Set audio to video
                    video = video.set_audio(audio)
                except Exception as e:
                    print(f"Warning: Could not add audio: {e}")
            
            # Write video file
            if progress_callback:
                progress_callback(80, "Rendering video...")
            
            # Ensure output directory exists and is writable
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, mode=0o777, exist_ok=True)
            
            # Check if directory is writable
            if not os.access(output_dir, os.W_OK):
                raise PermissionError(f"Output directory is not writable: {output_dir}")
            
            # Determine video quality based on watermark
            if self.add_watermark:
                # Free tier: 720p
                if self.height > 1280:
                    video = video.resize(height=1280)
            else:
                # Paid tier: 1080p (full resolution)
                pass
            
            video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                remove_temp=True,
                logger=None  # Suppress moviepy logs
            )
            
            # Clean up
            if progress_callback:
                progress_callback(95, "Cleaning up...")
            
            video.close()
            for clip in clips:
                clip.close()
            
            # Delete temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            if progress_callback:
                progress_callback(100, "Complete!")
            
            return output_path
            
        except Exception as e:
            error_msg = f"Error generating video: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            if progress_callback:
                progress_callback(-1, f"Error: {str(e)}")
            raise Exception(error_msg)
    
    @staticmethod
    def calculate_video_info(duration):
        """Calculate video information"""
        num_pages = int(duration / Config.PAGE_DURATION)
        return {
            'duration': duration,
            'num_pages': num_pages,
            'page_duration': Config.PAGE_DURATION,
            'fps_options': Config.AVAILABLE_FPS
        }


def create_video(main_text, duration=10, fps=30, resolution='9:16', 
                 output_filename=None, audio_path=None, add_watermark=True,
                 progress_callback=None):
    """
    Convenience function to create a video
    
    Args:
        main_text: Main text to display
        duration: Video duration in seconds
        fps: Frames per second
        resolution: Video resolution ratio
        output_filename: Output filename (auto-generated if None)
        audio_path: Path to audio file
        add_watermark: Add watermark for free tier
        progress_callback: Progress callback function
    
    Returns:
        Path to generated video
    """
    
    # Generate output filename if not provided
    if output_filename is None:
        import uuid
        output_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
    
    output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
    
    # Create video generator
    generator = VideoGenerator(
        main_text=main_text,
        duration=duration,
        fps=fps,
        resolution=resolution,
        add_watermark=add_watermark
    )
    
    # Generate video
    return generator.generate_video(output_path, audio_path, progress_callback)
