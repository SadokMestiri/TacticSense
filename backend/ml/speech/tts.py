import os
import tempfile
import hashlib
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play

load_dotenv()

class ElevenLabsTTS:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.client = ElevenLabs(api_key=self.api_key)
    
    def generate_speech(self, text, voice_id="qCwgiN0GsIAYwAJ1nYvZ", output_folder=None, filename_prefix="tts_"):
        """Generate speech from text using ElevenLabs API with caching"""
        if output_folder is None:
            output_folder = os.path.join(os.getcwd(), "processed_videos")
            
        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Create a content hash to uniquely identify this text
        content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
        
        # Create a descriptive filename using the prefix and content hash
        filename = f"{filename_prefix}{content_hash}.mp3"
        output_path = os.path.join(output_folder, filename)
        
        # Check if the file already exists
        if os.path.exists(output_path):
            print(f"Using existing audio file: {filename}")
            return output_path
        
        try:
            # Convert text to speech using the modern SDK
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id="CwhRBWXzGAHq8TQ4Fs17",
                model_id="eleven_flash_v2_5",
                output_format="mp3_44100_128",
            )
            
            # Handle case where audio is a generator instead of bytes
            if hasattr(audio, '__iter__') and not isinstance(audio, (bytes, bytearray)):
                audio_bytes = b''.join(chunk for chunk in audio)
            else:
                audio_bytes = audio
            
            # Save audio to file
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"Generated new audio file: {filename}")
            return output_path
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            raise Exception(f"Error generating speech: {str(e)}")