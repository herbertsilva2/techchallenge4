from pathlib import Path
from dotenv import load_dotenv
import os

# Carrega variáveis do .env (se existir)
load_dotenv()

# Configurações do Azure Speech
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
AZURE_SPEECH_LANGUAGE = os.getenv("AZURE_SPEECH_LANGUAGE", "pt-BR")
AZURE_SPEECH_ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")

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
