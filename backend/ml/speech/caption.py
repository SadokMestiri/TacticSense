import re

class CaptionEnhancer:
    def __init__(self):
        self.filler_words = ['um', 'uh', 'like', 'you know', 'sort of', 'kind of']
    
    def clean_transcript(self, transcript):
        """Remove filler words and clean up transcript"""
        cleaned = transcript
        for word in self.filler_words:
            cleaned = re.sub(r'\b' + word + r'\b', '', cleaned, flags=re.IGNORECASE)
        
        # Fix multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def enhance_srt(self, srt_path, output_path=None):
        """Enhance an SRT file by cleaning captions"""
        if output_path is None:
            output_path = srt_path.replace('.srt', '_enhanced.srt')
        
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by subtitle entries (double newline)
        entries = content.split('\n\n')
        enhanced_entries = []
        
        for entry in entries:
            if not entry.strip():
                continue
                
            lines = entry.split('\n')
            if len(lines) >= 3:
                # First line is index, second is timestamp, rest is text
                index = lines[0]
                timestamp = lines[1]
                text = '\n'.join(lines[2:])
                
                # Clean the text
                cleaned_text = self.clean_transcript(text)
                
                # Rebuild entry
                enhanced_entry = f"{index}\n{timestamp}\n{cleaned_text}"
                enhanced_entries.append(enhanced_entry)
        
        # Join back and write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(enhanced_entries))
        
        return output_path