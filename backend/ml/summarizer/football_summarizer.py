from transformers import BartForConditionalGeneration, BartTokenizer
import torch
import re
import os

class FootballSummarizer:
    def __init__(self):
        """Initialize the football summarizer using the trained DistilBART model"""
        # Set model path - look for model in the models directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "models", "football-summarizer")
        
        # Try to load trained model, otherwise use base model
        try:
            if os.path.exists(model_path):
                print(f"Loading fine-tuned model from {model_path}")
                self.model = BartForConditionalGeneration.from_pretrained(model_path)
                self.tokenizer = BartTokenizer.from_pretrained(model_path)
            else:
                # Fall back to the pre-trained model
                print("Fine-tuned model not found, using base DistilBART")
                self.model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-6-6")
                self.tokenizer = BartTokenizer.from_pretrained("sshleifer/distilbart-cnn-6-6")
        except Exception as e:
            print(f"Error loading model: {str(e)}, using base DistilBART")
            self.model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-6-6")
            self.tokenizer = BartTokenizer.from_pretrained("sshleifer/distilbart-cnn-6-6")
        
        # Move to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        
        # Football-specific excitement patterns
        self.excitement_patterns = [
            r'\b(goal|score|scores|scored|shot|shots|save|saves|saved)\b',
            r'\b(attack|counter|penalty|free-kick|corner|header)\b',
            r'\b(amazing|incredible|fantastic|brilliant|excellent)\b',
            r'\b(messi|ronaldo|neymar|mbappé|haaland|salah|lewandowski)\b',  # Star players
            r'!{2,}',  # Multiple exclamation marks
        ]
    
    def summarize(self, transcript, max_length=150, min_length=40):
        """Generate a summary of a football match transcript"""
        # Prepare input
        inputs = self.tokenizer(transcript, return_tensors="pt", max_length=1024, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate summary
        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,
                min_length=min_length,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )
        
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    
    def find_key_moments(self, transcript):
        """Find exciting moments in the transcript"""
        import nltk
        try:
            # Ensure NLTK resources are available
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        sentences = nltk.sent_tokenize(transcript)
        key_moments = []
        
        for i, sentence in enumerate(sentences):
            # Calculate excitement score
            excitement_score = 0
            for pattern in self.excitement_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                excitement_score += len(matches) * 0.5
            
            # Add timing context if available
            timing_match = re.search(r'\b(\d{1,2}:\d{2}|\d{1,2}\'|\d{1,2} minutes?)\b', sentence)
            match_time = timing_match.group(1) if timing_match else None
            
            # If this is an exciting sentence
            if excitement_score >= 1.0:
                key_moments.append({
                    'text': sentence,
                    'excitement': min(excitement_score, 5),  # Cap at 5
                    'time': match_time
                })
        
        # Sort by excitement level
        key_moments.sort(key=lambda x: x['excitement'], reverse=True)
        return key_moments[:5]  # Return top 5