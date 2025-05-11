import re
import os

class SRTFormatter:
    def __init__(self):
        self.time_pattern = re.compile(r'(\d+):(\d+):(\d+),(\d+)')
    
    def seconds_to_timestamp(self, seconds):
        """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def timestamp_to_seconds(self, timestamp):
        """Convert SRT timestamp to seconds"""
        match = self.time_pattern.match(timestamp)
        if not match:
            return 0
        
        hours, minutes, seconds, milliseconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
    
    def shift_timing(self, srt_path, offset_seconds, output_path=None):
        """Shift all timestamps in an SRT file by a given number of seconds"""
        if output_path is None:
            output_path = srt_path.replace('.srt', f'_shifted{offset_seconds}.srt')
        
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        def replace_time(match):
            time_str = match.group(0)
            seconds = self.timestamp_to_seconds(time_str)
            new_seconds = max(0, seconds + offset_seconds)  # Prevent negative times
            return self.seconds_to_timestamp(new_seconds)
        
        # Replace all timestamps
        adjusted_content = self.time_pattern.sub(replace_time, content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(adjusted_content)
        
        return output_path
    
    def merge_srt_files(self, srt_files, output_path):
        """Merge multiple SRT files into one, adjusting indexes"""
        entries = []
        current_index = 1
        
        for srt_file in srt_files:
            with open(srt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by entry
            file_entries = content.split('\n\n')
            for entry in file_entries:
                if not entry.strip():
                    continue
                
                lines = entry.split('\n')
                if len(lines) >= 3:
                    # Replace index with current_index
                    lines[0] = str(current_index)
                    entries.append('\n'.join(lines))
                    current_index += 1
        
        # Write merged file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(entries))
        
        return output_path