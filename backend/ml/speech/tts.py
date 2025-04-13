import os
import tempfile
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play

load_dotenv()

class ElevenLabsTTS:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.client = ElevenLabs(api_key=self.api_key)
    
    def generate_speech(self, text, voice_id="qCwgiN0GsIAYwAJ1nYvZ", output_path=None):
        """Generate speech from text using ElevenLabs API"""
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "tts_output.mp3")
        
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
                
            return output_path
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            raise Exception(f"Error generating speech: {str(e)}")