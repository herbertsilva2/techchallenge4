from pathlib import Path
from dotenv import load_dotenv
import os

# Carrega configurações públicas do .env e segredos locais não versionados do .env.local.
load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env.local", override=True)

# Configurações do Azure Speech
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
AZURE_SPEECH_LANGUAGE = os.getenv("AZURE_SPEECH_LANGUAGE", "pt-BR")
AZURE_SPEECH_ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


# Objetos cortantes podem ser pequenos ou parcialmente ocultos; o limiar é
# validado temporalmente pelo FrameAnalyzer antes de gerar risco.
YOLO_SHARP_OBJECT_MIN_CONFIDENCE = _env_float("YOLO_SHARP_OBJECT_MIN_CONFIDENCE", 0.10)

# Caminho base do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Diretórios principais
DATA_DIR = PROJECT_ROOT / "data"
SAMPLES_DIR = DATA_DIR / "samples"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
DOCS_DIR = PROJECT_ROOT / "docs"

# Garante que o diretório outputs exista
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
