from typing import Tuple, List, Set
from src.domain.video_models import VideoAnalysis
from src.domain.audio_models import AudioAnalysis
from src.domain.text_models import TextAnalysis
from src.domain.fusion_models import Evidence, RiskLevel

class RiskRules:
    """Regras de risco do mecanismo de fusão multimodal."""
    
    TEXT_CATEGORIES_WEIGHTS = {
        "MEDO": 15.0,
        "AJUDA": 25.0,
        "COERÇÃO": 20.0,
        "VIOLÊNCIA": 30.0
    }
    
    TEXT_HIGH_RISK_WEIGHT = 15.0
    
    YOLO_OBJECT_WEIGHTS = {
        "hand_on_face": 10.0,
        "defensive_posture": 20.0,
        "razor_blade": 30.0,
        "box_cutter": 30.0,
        "knife": 25.0,
        "scissors": 20.0
    }
    
    NO_FACE_WEIGHT = 5.0
    MULTIMODAL_WEIGHT = 10.0
    
    @staticmethod
    def evaluate(video: VideoAnalysis | None, audio: AudioAnalysis | None, text: TextAnalysis | None) -> Tuple[float, List[Evidence], List[str]]:
        """Avalia as evidências e retorna o score final, lista de evidências e justificativas."""
        
        score = 0.0
        evidences: List[Evidence] = []
        justifications: List[str] = []
        
        modalities_with_evidence: Set[str] = set()
        
        # 1. Análise de Texto
        if text and text.transcript and text.transcript.sentences:
            seen_categories = set()
            high_risk_found = False
            
            category_counts = {}
            high_risk_count = 0
            
            for sentence in text.transcript.sentences:
                # Categoria High Risk
                if sentence.risk_level.lower() == "alto":
                    high_risk_found = True
                    high_risk_count += 1
                
                # Categorias Específicas
                for cat in sentence.categories:
                    cat_upper = cat.upper()
                    if cat_upper in RiskRules.TEXT_CATEGORIES_WEIGHTS:
                        category_counts[cat_upper] = category_counts.get(cat_upper, 0) + 1
                        if cat_upper not in seen_categories:
                            seen_categories.add(cat_upper)
                            score += RiskRules.TEXT_CATEGORIES_WEIGHTS[cat_upper]
                            evidences.append(Evidence(
                                modality="text",
                                description=f"Categoria textual {cat_upper} detectada",
                                confidence=1.0
                            ))
                            modalities_with_evidence.add("text")
            
            # Adiciona justificativas com contagem
            for cat, count in category_counts.items():
                justifications.append(f"Categoria textual {cat} identificada em {count} frase(s).")
            
            if high_risk_found:
                score += RiskRules.TEXT_HIGH_RISK_WEIGHT
                evidences.append(Evidence(
                    modality="text",
                    description="Frase textual com risk_level alto",
                    confidence=1.0
                ))
                modalities_with_evidence.add("text")
                justifications.append(f"Frase com nível de risco alto identificada em {high_risk_count} ocorrência(s).")

        # 2. Análise de Vídeo (Face e YOLO)
        if video and video.frames_analyzed > 0:
            # Regra: mais de 70% dos frames sem rosto
            no_face_ratio = video.frames_without_faces / video.frames_analyzed
            if no_face_ratio > 0.7:
                score += RiskRules.NO_FACE_WEIGHT
                evidences.append(Evidence(
                    modality="video",
                    description="Ausência de rosto em grande parte do vídeo",
                    confidence=1.0
                ))
                modalities_with_evidence.add("video")
                percentage = int(no_face_ratio * 100)
                justifications.append(f"Mais de 70% dos frames analisados não apresentaram rosto ({percentage}%).")
            
            # Regras YOLO
            seen_objects = set()
            object_counts = {}
            for frame in video.frames:
                for obj in frame.objects:
                    obj_name = obj.class_name.lower()
                    if obj_name in RiskRules.YOLO_OBJECT_WEIGHTS:
                        object_counts[obj_name] = object_counts.get(obj_name, 0) + 1
                        if obj_name not in seen_objects:
                            seen_objects.add(obj_name)
                            score += RiskRules.YOLO_OBJECT_WEIGHTS[obj_name]
                            evidences.append(Evidence(
                                modality="video",
                                description=f"Detecção visual de {obj_name}",
                                confidence=obj.confidence
                            ))
                            modalities_with_evidence.add("video")
            
            for obj_name, count in object_counts.items():
                if obj_name == "hand_on_face":
                    justifications.append(f"Mão no rosto detectada em {count} frame(s).")
                elif obj_name == "defensive_posture":
                    justifications.append(f"Postura defensiva detectada em {count} frame(s).")
                elif obj_name in {"razor_blade", "box_cutter", "knife", "scissors"}:
                    justifications.append(f"Objeto cortante ou suspeito ({obj_name}) detectado em {count} frame(s).")
                else:
                    justifications.append(f"Objeto {obj_name} detectado em {count} frame(s).")

        # 3. Análise de Áudio (Placeholder for future rules, AudioAnalysis does not add risk yet)
        if audio:
            pass # Sem regras acústicas implementadas
        
        # 4. Fusão Multimodal (Evidências relevantes em duas ou mais modalidades)
        if len(modalities_with_evidence) >= 2:
            score += RiskRules.MULTIMODAL_WEIGHT
            evidences.append(Evidence(
                modality="fusion",
                description="Evidências identificadas em múltiplas modalidades",
                confidence=1.0
            ))
            mods_str = " e ".join(sorted(modalities_with_evidence))
            justifications.append(f"Evidências identificadas em {mods_str}.")

        # 5. Limites do Score
        score = min(max(score, 0.0), 100.0)
        
        return score, evidences, justifications

    @staticmethod
    def get_risk_level(score: float) -> RiskLevel:
        """Determina o nível de risco baseado no score."""
        if score < 30:
            return RiskLevel.LOW
        elif score < 60:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    @staticmethod
    def get_recommendations(risk_level: RiskLevel, has_evidences: bool = False) -> List[str]:
        """Retorna recomendações padrão baseadas no nível de risco."""
        if risk_level == RiskLevel.LOW:
            if has_evidences:
                return [
                    "Sinais pontuais foram identificados, mas não atingiram o limite para risco moderado.",
                    "Manter avaliação humana e atenção aos sinais apontados."
                ]
            else:
                return [
                    "Nenhum sinal relevante foi identificado pelas regras atuais.",
                    "Manter avaliação humana conforme o fluxo normal."
                ]
        elif risk_level == RiskLevel.MEDIUM:
            return [
                "Recomenda-se revisão humana das evidências identificadas.",
                "Avaliar o caso conforme o protocolo institucional de triagem."
            ]
        else: # HIGH
            return [
                "Recomenda-se avaliação prioritária por profissional habilitado.",
                "Revisar os trechos e frames indicados antes de qualquer decisão.",
                "Seguir os protocolos institucionais aplicáveis."
            ]
