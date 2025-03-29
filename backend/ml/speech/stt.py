import whisper
import os
import tempfile

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)
    
    def transcribe_audio(self, audio_path):
        """Transcribe audio file using Whisper"""
        result = self.model.transcribe(audio_path)
        return result
    
    def generate_srt(self, result, output_path):
        """Convert Whisper result to SRT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments']):
                # Format: index, start --> end, text
                f.write(f"{i+1}\n")
                start = self.format_timestamp(segment['start'])
                end = self.format_timestamp(segment['end'])
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        return output_path
    
    @staticmethod
    def format_timestamp(seconds):
        """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"