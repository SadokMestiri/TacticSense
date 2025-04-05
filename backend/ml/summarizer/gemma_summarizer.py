import os
import gc
import torch
import re
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

class GemmaSummarizerService:
    """Service to summarize soccer match transcripts using the base Gemma model."""
    
    def __init__(self, model_name="google/gemma-3-1b-it", use_8bit=True):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.use_8bit = use_8bit
    
    def load_model(self):
        """Load the model with memory optimizations."""
        if self.model is not None:
            # Model already loaded
            return
            
        # Clear GPU memory
        torch.cuda.empty_cache()
        gc.collect()
        
        print(f"Loading model: {self.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        if self.use_8bit:
            # 8-bit quantization for memory efficiency
            bnb_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_skip_modules=["embed_tokens", "lm_head"]
            )
            
            # Load in 8-bit mode
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype=torch.float16,
                max_memory={0: "7GiB", "cpu": "12GiB"}
            )
        else:
            # Load in FP16 mode
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
        print("Model loaded successfully")
    
    def unload_model(self):
        """Free up GPU memory by deleting the model."""
        if self.model is not None:
            del self.model
            self.model = None
            del self.tokenizer
            self.tokenizer = None
            torch.cuda.empty_cache()
            gc.collect()
            print("Model unloaded from memory")
    
    def load_transcript_from_srt(self, srt_path):
        """Extract transcript text from an SRT file."""
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove SRT formatting (numbers and timestamps)
        srt_pattern = r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n(.*?)(?=\n\n\d+\n|$)'
        matches = re.findall(srt_pattern, content, re.DOTALL)
        transcript = ' '.join([m.replace('\n', ' ') for m in matches])
        
        return transcript
    
    def create_optimized_prompt(self, transcript):
        """Create an optimized prompt that guides the model to produce high-quality summaries."""
        prompt = f"""<start_of_turn>user
You are a professional soccer commentator tasked with creating concise, engaging summaries of match highlights.

Context: The transcript contains speech recognition errors in player and team names - please correct these in your summary.

Please summarize the following match highlights in a concise, engaging paragraph:

HIGHLIGHTS TRANSCRIPT:
{transcript}

Create a summary that:
1. Highlights key moments and actions
2. Uses proper soccer terminology
3. Has an engaging, professional tone
IMPORTANT: Your response should ONLY contain the summary itself. Do not include any introduction or closing remarks.
<end_of_turn>

<start_of_turn>model
"""
        return prompt
    
    def summarize(self, transcript, max_length=500):
        """Generate a summary for the given transcript."""
        # Load model if not already loaded
        if self.model is None:
            self.load_model()
            
        # Create optimized prompt
        prompt = self.create_optimized_prompt(transcript)
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate summary
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
        # Extract generated summary - SIMPLIFIED VERSION
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Filter out common phrases that appear before the actual summary
        # These patterns match the start of responses we've seen
        filter_patterns = [
            "model",
            "Here's a",
            "Okay, here's",
            "Here is",
        ]
        
        # Remove everything up to and including these patterns
        summary = full_response
        for pattern in filter_patterns:
            if pattern in summary:
                # Split and take everything after the pattern
                parts = summary.split(pattern, 1)
                if len(parts) > 1:
                    summary = parts[1].strip()
        
        # If there are any remnants of the prompt, remove them
        if "TRANSCRIPT:" in summary:
            summary = summary.split("TRANSCRIPT:")[-1].strip()
        
        return summary
    
    def summarize_from_file(self, srt_path, max_length=500):
        """Generate a summary from an SRT file."""
        transcript = self.load_transcript_from_srt(srt_path)
        return self.summarize(transcript, max_length)