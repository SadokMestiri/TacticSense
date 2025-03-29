import requests
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsTTS:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def generate_speech(self, text, voice_id="21m00Tcm4TlvDq8ikWAM", output_path=None):
        """Generate speech from text using ElevenLabs API"""
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "tts_output.mp3")
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        else:
            raise Exception(f"Error generating speech: {response.text}")