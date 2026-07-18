import re
from src.domain.text_models import Transcript, SentenceAnalysis, TextAnalysis
from src.text.keywords import KEYWORDS

class TextAnalyzer:
    """Analisador de texto baseado em regras determinísticas."""
    
    def __init__(self):
        self.keywords = KEYWORDS

    def analyze(self, transcript: Transcript) -> TextAnalysis:
        if not transcript or not transcript.full_text:
            return TextAnalysis(
                transcript=Transcript(full_text="", sentences=[]),
                overall_sentiment=0.0
            )

        # Dividir o texto em frases usando pontuação final
        raw_sentences = re.split(r'(?<=[.!?]) +', transcript.full_text)
        
        sentences = []
        for raw_sentence in raw_sentences:
            text = raw_sentence.strip()
            if not text:
                continue
                
            categories_found = []
            keyword_count = 0
            
            text_lower = text.lower()
            
            for category, words in self.keywords.items():
                category_matched = False
                for word in words:
                    # Usar word boundaries para evitar falsos positivos
                    # ex: "soco" dentro de "socorro"
                    pattern = r'\b' + re.escape(word) + r'\b'
                    if re.search(pattern, text_lower):
                        keyword_count += 1
                        category_matched = True
                        
                if category_matched:
                    categories_found.append(category)
                    
            # Definir nível de risco da frase
            risk_level = "baixo"
            if keyword_count >= 3:
                risk_level = "alto"
            elif keyword_count >= 1:
                risk_level = "moderado"
                
            sentences.append(SentenceAnalysis(
                text=text,
                sentiment_score=0.0,
                categories=categories_found,
                keyword_count=keyword_count,
                risk_level=risk_level
            ))

        analyzed_transcript = Transcript(
            full_text=transcript.full_text,
            sentences=sentences
        )

        return TextAnalysis(
            transcript=analyzed_transcript,
            overall_sentiment=0.0
        )
