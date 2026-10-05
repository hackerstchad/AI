#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██╗   ██╗██╗  ████████╗██████╗  █████╗     ██╗   ██╗ ██████╗ ██╗ ██████╗   ║
║   ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔══██╗    ██║   ██║██╔═══██╗██║██╔════╝   ║
║   ██║   ██║██║     ██║   ██████╔╝██║  ██║    ██║   ██║██║   ██║██║██║        ║
║   ██║   ██║██║     ██║   ██╔══██╗██║  ██║    ╚██╗ ██╔╝██║   ██║██║██║        ║
║   ╚██████╔╝███████╗██║   ██║  ██║╚█████╔╝     ╚████╔╝ ╚██████╔╝██║╚██████╗   ║
║    ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚════╝       ╚═══╝   ╚═════╝ ╚═╝ ╚═════╝   ║
║                                                                              ║
║                 U L T R A   V O I C E   T T S  —  v2.0.0                     ║
║                                                                              ║
║   Synthèse vocale avancée, multi-moteurs, 100% gratuite et offline-capable.  ║
║   Interface Tkinter stylisée avec effets audio, Voice Activity Detection,    ║
║   normalisation du texte, prévisualisation, export WAV/MP3, et plus.         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

SOMMAIRE
--------
1. Configuration et constantes
2. Utilitaires linguistiques (normalisation, phonèmes, SSML)
3. Moteurs TTS (pyttsx3, gTTS, Coqui TTS, espeak)
4. Post-traitement audio (normalisation, VAD, reverb, égalisation)
5. Pipeline de synthèse unifiée
6. Interface Tkinter avancée
7. Point d'entrée __main__

UTILISATION RAPIDE
------------------
    # Interface graphique
    python ultra_voice_tts.py

    # Utilisation programmatique
    from ultra_voice_tts import UltraVoiceTTS
    tts = UltraVoiceTTS()
    tts.speak("Bonjour le monde", engine="pyttsx3")
    tts.save("sortie.wav", "Bonjour le monde", engine="coqui")
"""

from __future__ import annotations

import argparse
import io
import json
import os
import platform
import re
import shutil
import sys
import tempfile
import threading
import time
import traceback
import wave
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from queue import Empty, Queue
from threading import Lock, Thread
from tkinter import (
    BOTH,
    BOTTOM,
    CENTER,
    DISABLED,
    END,
    HORIZONTAL,
    LEFT,
    NORMAL,
    RIGHT,
    TOP,
    BooleanVar,
    Button,
    Checkbutton,
    DoubleVar,
    Entry,
    Frame,
    Label,
    Listbox,
    Menu,
    Message,
    OptionMenu,
    Scale,
    Scrollbar,
    StringVar,
    Text,
    Tk,
    Toplevel,
    filedialog,
    messagebox,
    scrolledtext,
    ttk,
)
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

# Suppression des warnings non critiques pour une UI propre
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


# =============================================================================
# 1. CONFIGURATION ET CONSTANTES
# =============================================================================

APP_NAME = "Ultra Voice TTS"
APP_VERSION = "2.0.0"
APP_AUTHOR = "CodePal"

# Répertoire de cache cross-platform
CACHE_DIR = Path.home() / ".cache" / "ultra_voice_tts"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Dossier temporaire dédié
TEMP_DIR = Path(tempfile.gettempdir()) / "ultra_voice_tts"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Paramètres audio par défaut
DEFAULT_SAMPLE_RATE = 22050
DEFAULT_BITRATE = "192k"

# Moteurs TTS supportés
ENGINE_PYTTSX3 = "pyttsx3"
ENGINE_GTTS = "gTTS"
ENGINE_COQUI = "coqui"
ENGINE_ESPEAK = "espeak"
ENGINE_SYSTEM = "system"

ALL_ENGINES = [ENGINE_PYTTSX3, ENGINE_GTTS, ENGINE_COQUI, ENGINE_ESPEAK, ENGINE_SYSTEM]

# Langues supportées par gTTS (sous-ensemble courant)
GTTS_LANGUAGES = {
    "fr": "Français",
    "en": "English",
    "es": "Español",
    "de": "Deutsch",
    "it": "Italiano",
    "pt": "Português",
    "nl": "Nederlands",
    "ru": "Русский",
    "ja": "日本語",
    "zh": "中文",
    "ar": "العربية",
    "ko": "한국어",
    "pl": "Polski",
    "tr": "Türkçe",
    "sv": "Svenska",
}

# Effets audio disponibles
EFFECTS = {
    "normalize": "Normalisation RMS",
    "vad_trim": "Suppression silences (VAD)",
    "eq": "Égalisation simple",
    "speed": "Ajustement vitesse",
    "pitch": "Ajustement hauteur",
    "reverb": "Réverbération légère",
    "chorus": "Chorus doux",
}


# =============================================================================
# 2. UTILITAIRES LINGUISTIQUES
# =============================================================================

class TextNormalizer:
    """Normalise et enrichit un texte brut pour une meilleure synthèse vocale."""

    # Abbréviations courantes en français et anglais
    ABBREVIATIONS: Dict[str, Dict[str, str]] = {
        "fr": {
            "M.": "Monsieur",
            "Mme": "Madame",
            "Mlle": "Mademoiselle",
            "Dr": "Docteur",
            "Pr": "Professeur",
            "Mme.": "Madame",
            "M.": "Monsieur",
            "p. ex.": "par exemple",
            "c.-à-d.": "c'est-à-dire",
            "Mme": "Madame",
            "Mlle": "Mademoiselle",
            "Mr": "Monsieur",
            "etc.": "et cætera",
            "1er": "premier",
            "1re": "première",
            "2e": "deuxième",
            "3e": "troisième",
        },
        "en": {
            "Mr.": "Mister",
            "Mrs.": "Misses",
            "Ms.": "Miz",
            "Dr.": "Doctor",
            "Prof.": "Professor",
            "St.": "Saint",
            "Ave.": "Avenue",
            "Blvd.": "Boulevard",
            "etc.": "et cetera",
        },
    }

    # Ponctuation et pauses
    PAUSE_MAP = {
        ".": "<break time=\"500ms\"/>",
        ";": "<break time=\"400ms\"/>",
        ":": "<break time=\"300ms\"/>",
        "!": "<break time=\"500ms\"/>",
        "?": "<break time=\"500ms\"/>",
        ",": "<break time=\"200ms\"/>",
    }

    @classmethod
    def expand_abbreviations(cls, text: str, lang: str = "fr") -> str:
        """Développe les abbréviations courantes."""
        mapping = cls.ABBREVIATIONS.get(lang, cls.ABBREVIATIONS["en"])
        for abbr, full in mapping.items():
            text = re.sub(r"\b" + re.escape(abbr) + r"\b", full, text, flags=re.IGNORECASE)
        return text

    @classmethod
    def numbers_to_words(cls, text: str, lang: str = "fr") -> str:
        """Convertit les nombres en mots quand c'est possible."""
        try:
            import num2words
        except ImportError:
            return text

        def replace_num(match: re.Match) -> str:
            num_str = match.group(0)
            try:
                # Gestion simple des nombres entiers
                if "," in num_str or "." in num_str:
                    return num_str
                return num2words.num2words(int(num_str), lang=lang)
            except Exception:
                return num_str

        return re.sub(r"\b\d+\b", replace_num, text)

    @classmethod
    def normalize_whitespace(cls, text: str) -> str:
        """Supprime les espaces multiples et les retours à la ligne parasites."""
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\n", " ").replace("\r", " ")
        return text.strip()

    @classmethod
    def clean_text(cls, text: str, lang: str = "fr") -> str:
        """Pipeline complet de normalisation."""
        if not text:
            return ""
        text = cls.normalize_whitespace(text)
        text = cls.expand_abbreviations(text, lang)
        text = cls.numbers_to_words(text, lang)
        # Supprime les caractères de contrôle sauf retours à la ligne
        text = "".join(ch for ch in text if ch == "\n" or ord(ch) >= 32)
        return text.strip()

    @classmethod
    def to_ssml(cls, text: str, lang: str = "fr", rate: str = "medium", pitch: str = "medium") -> str:
        """Génère un fragment SSML simple pour moteurs compatibles."""
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        ssml = f'<speak xml:lang="{lang}">\n'
        ssml += f'<prosody rate="{rate}" pitch="{pitch}">\n'
        ssml += escaped
        ssml += "\n</prosody>\n</speak>"
        return ssml

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        """Découpe un texte en phrases."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]


class PhonemeHelper:
    """Fournit une conversion approximative texte -> phonèmes via espeak/phonemizer."""

    @staticmethod
    def is_available() -> bool:
        return shutil.which("espeak") is not None or shutil.which("espeak-ng") is not None

    @classmethod
    def text_to_phonemes(cls, text: str, lang: str = "fr") -> str:
        """Retourne une transcription phonétique approximative."""
        try:
            from phonemizer import phonemize
            return phonemize(text, language=lang, backend="espeak")
        except Exception:
            pass

        binary = shutil.which("espeak-ng") or shutil.which("espeak")
        if not binary:
            return "[phonemizer non disponible]"
        try:
            import subprocess
            result = subprocess.run(
                [binary, "-v", lang, "-x", "--ipa", text],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip()
        except Exception as exc:
            return f"[erreur phonèmes: {exc}]"


# =============================================================================
# 3. POST-TRAITEMENT AUDIO
# =============================================================================

class AudioProcessor:
    """Applique des effets audio sur des échantillons numpy."""

    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE):
        self.sample_rate = sample_rate

    @staticmethod
    def to_float_array(audio_bytes: bytes, sample_width: int = 2) -> "np.ndarray":
        """Convertit des bytes PCM en tableau float normalisé [-1, 1]."""
        import numpy as np
        if sample_width == 1:
            data = np.frombuffer(audio_bytes, dtype=np.uint8).astype(np.float32)
            data = (data - 128.0) / 128.0
        elif sample_width == 2:
            data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
            data = data / 32768.0
        else:
            raise ValueError("sample_width non supporté (1 ou 2)")
        return data

    @staticmethod
    def to_int16_bytes(data: "np.ndarray") -> bytes:
        """Convertit un tableau float [-1, 1] en bytes PCM int16."""
        import numpy as np
        clipped = np.clip(data, -1.0, 1.0)
        return (clipped * 32767.0).astype(np.int16).tobytes()

    def normalize(self, data: "np.ndarray", target_db: float = -3.0) -> "np.ndarray":
        """Normalise le niveau sonore RMS."""
        import numpy as np
        rms = np.sqrt(np.mean(data**2))
        if rms == 0:
            return data
        current_db = 20 * np.log10(rms + 1e-12)
        gain_db = target_db - current_db
        gain = 10 ** (gain_db / 20.0)
        return data * gain

    def change_speed(self, data: "np.ndarray", factor: float) -> "np.ndarray":
        """Change la vitesse sans modifier la hauteur (phase vocoder simplifié)."""
        import numpy as np
        from scipy import signal
        if factor <= 0 or abs(factor - 1.0) < 0.01:
            return data
        # Méthode simple par resampling + conservation de pitch (approximation)
        n = len(data)
        new_n = int(n / factor)
        resampled = signal.resample(data, new_n)
        return resampled

    def change_pitch(self, data: "np.ndarray", semitones: float) -> "np.ndarray":
        """Change la hauteur en tons (via interpolation/resampling simplifié)."""
        import numpy as np
        from scipy import signal
        if abs(semitones) < 0.1:
            return data
        factor = 2 ** (semitones / 12.0)
        new_len = int(len(data) / factor)
        return signal.resample(data, new_len)

    def simple_eq(self, data: "np.ndarray") -> "np.ndarray":
        """Égalisation simple : boost des fréquences vocales (~1-4 kHz)."""
        import numpy as np
        from scipy import signal
        # Filtre passe-bande boosté (approximation)
        sos = signal.butter(2, [300, 4000], btype="bandpass", fs=self.sample_rate, output="sos")
        boosted = signal.sosfilt(sos, data) * 1.3
        return np.clip(data + boosted * 0.3, -1.0, 1.0)

    def trim_silence(self, data: "np.ndarray", threshold: float = 0.01) -> "np.ndarray":
        """Supprime les silences au début et à la fin."""
        import numpy as np
        above = np.where(np.abs(data) > threshold)[0]
        if above.size == 0:
            return data
        return data[above[0] : above[-1] + 1]

    def apply_vad_trim(self, data: "np.ndarray", aggressiveness: int = 2) -> "np.ndarray":
        """Utilise WebRTC VAD pour détecter et garder les segments vocaux."""
        try:
            import webrtcvad
        except ImportError:
            return self.trim_silence(data)

        # WebRTC VAD nécessite du PCM 16 bits mono à 8000/16000/32000/48000 Hz
        import numpy as np
        import resampy

        target_sr = 16000
        resampled = resampy.resample(data, self.sample_rate, target_sr)
        pcm = (np.clip(resampled, -1.0, 1.0) * 32767).astype(np.int16).tobytes()

        vad = webrtcvad.Vad(aggressiveness)
        frame_ms = 30
        frame_len = int(target_sr * frame_ms / 1000) * 2
        frames = [pcm[i : i + frame_len] for i in range(0, len(pcm), frame_len) if len(pcm[i : i + frame_len]) == frame_len]
        voiced = [vad.is_speech(frame, target_sr) for frame in frames]

        # Garder les segments voisés avec un peu de contexte
        keep = []
        for i, is_voiced in enumerate(voiced):
            keep.append(is_voiced)
        if not any(keep):
            return data

        # Reconstitution approximative
        out_frames = [frames[i] for i, k in enumerate(keep) if k]
        out_pcm = b"".join(out_frames)
        out_data = np.frombuffer(out_pcm, dtype=np.int16).astype(np.float32) / 32768.0
        return resampy.resample(out_data, target_sr, self.sample_rate)

    def reverb(self, data: "np.ndarray", decay: float = 0.4, delay_ms: float = 60.0) -> "np.ndarray":
        """Ajoute une réverbération simple par comb filter."""
        import numpy as np
        delay_samples = int(self.sample_rate * delay_ms / 1000.0)
        out = np.zeros(len(data) + delay_samples, dtype=np.float32)
        out[: len(data)] = data
        for i in range(delay_samples, len(out)):
            out[i] += out[i - delay_samples] * decay
        return out[: len(data)]

    def chorus(self, data: "np.ndarray", depth: float = 0.02, rate: float = 1.5) -> "np.ndarray":
        """Effet chorus très léger."""
        import numpy as np
        t = np.arange(len(data)) / self.sample_rate
        mod = depth * np.sin(2 * np.pi * rate * t)
        delayed = np.interp(np.arange(len(data)) - mod * self.sample_rate, np.arange(len(data)), data)
        return np.clip(data * 0.7 + delayed * 0.3, -1.0, 1.0)

    def apply_effects(
        self,
        data: "np.ndarray",
        effects: List[str],
        speed: float = 1.0,
        pitch: float = 0.0,
    ) -> "np.ndarray":
        """Applique une chaîne d'effets audio."""
        if "normalize" in effects:
            data = self.normalize(data)
        if "eq" in effects:
            data = self.simple_eq(data)
        if abs(speed - 1.0) > 0.01 or "speed" in effects:
            data = self.change_speed(data, speed)
        if abs(pitch) > 0.1 or "pitch" in effects:
            data = self.change_pitch(data, pitch)
        if "reverb" in effects:
            data = self.reverb(data)
        if "chorus" in effects:
            data = self.chorus(data)
        if "vad_trim" in effects:
            data = self.apply_vad_trim(data)
        data = self.normalize(data)
        return np.clip(data, -1.0, 1.0)


# =============================================================================
# 4. MOTEURS TTS
# =============================================================================

@dataclass
class TTSEngineInfo:
    """Métadonnées d'un moteur TTS."""
    name: str
    description: str
    requires_internet: bool
    supports_offline: bool
    voices: List[str] = field(default_factory=list)


class BaseTTSEngine:
    """Classe de base pour tous les moteurs TTS."""

    def __init__(self, lang: str = "fr", speed: float = 1.0, pitch: float = 0.0):
        self.lang = lang
        self.speed = speed
        self.pitch = pitch

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> bytes:
        """Génère de l'audio et retourne les bytes WAV/PCM."""
        raise NotImplementedError

    def list_voices(self) -> List[str]:
        return []

    def is_available(self) -> bool:
        return True


class Pyttsx3Engine(BaseTTSEngine):
    """Moteur natif pyttsx3 (offline, utilise SAPI5/NSSpeechSynth/espeak)."""

    def __init__(self, lang: str = "fr", speed: float = 1.0, pitch: float = 0.0, voice_id: Optional[str] = None):
        super().__init__(lang, speed, pitch)
        self.voice_id = voice_id
        self._engine = None
        self._voices: List[str] = []
        self._init_engine()

    def _init_engine(self):
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", int(180 * self.speed))
            voices = self._engine.getProperty("voices")
            self._voices = [v.id for v in voices]
            if self.voice_id and self.voice_id in self._voices:
                self._engine.setProperty("voice", self.voice_id)
            else:
                # Sélectionne une voix correspondant à la langue
                for v in voices:
                    if self.lang[:2].lower() in (v.languages or "").lower() or self.lang[:2].lower() in v.id.lower():
                        self._engine.setProperty("voice", v.id)
                        break
        except Exception as exc:
            raise RuntimeError(f"pyttsx3 non disponible: {exc}")

    def list_voices(self) -> List[str]:
        return self._voices

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> bytes:
        if self._engine is None:
            raise RuntimeError("Moteur pyttsx3 non initialisé")
        out_path = output_path or (TEMP_DIR / f"pyttsx3_{int(time.time()*1000)}.wav")
        self._engine.save_to_file(text, str(out_path))
        self._engine.runAndWait()
        return out_path.read_bytes()

    def is_available(self) -> bool:
        return self._engine is not None


class GTTSEngine(BaseTTSEngine):
    """Moteur Google Translate TTS (online, gratuit, pas de clé API)."""

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> bytes:
        try:
            from gtts import gTTS
        except ImportError as exc:
            raise RuntimeError(f"gTTS non installé: {exc}")

        # gTTS limite la taille des textes ~100 caractères par requête
        max_len = 100
        chunks = [text[i : i + max_len] for i in range(0, len(text), max_len)]
        from pydub import AudioSegment

        combined = AudioSegment.silent(duration=0)
        for chunk in chunks:
            tts = gTTS(text=chunk, lang=self.lang[:2], slow=(self.speed < 0.9))
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            segment = AudioSegment.from_mp3(mp3_fp)
            combined += segment

        if output_path:
            combined.export(str(output_path), format="wav")
            return output_path.read_bytes()
        buf = io.BytesIO()
        combined.export(buf, format="wav")
        return buf.getvalue()

    def is_available(self) -> bool:
        try:
            import gtts
            import requests
            return True
        except Exception:
            return False


class EspeakEngine(BaseTTSEngine):
    """Moteur espeak/espeak-ng en ligne de commande (offline)."""

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> bytes:
        binary = shutil.which("espeak-ng") or shutil.which("espeak")
        if not binary:
            raise RuntimeError("espeak/espeak-ng non installé")
        out_path = output_path or (TEMP_DIR / f"espeak_{int(time.time()*1000)}.wav")
        import subprocess

        speed_wpm = int(175 * self.speed)
        pitch_val = int(self.pitch * 10)
        cmd = [
            binary,
            "-v", self.lang[:2],
            "-s", str(speed_wpm),
            "-p", str(pitch_val),
            "-w", str(out_path),
            text,
        ]
        subprocess.run(cmd, check=False, capture_output=True)
        if not out_path.exists():
            raise RuntimeError("espeak n'a pas généré de fichier audio")
        return out_path.read_bytes()

    def is_available(self) -> bool:
        return shutil.which("espeak") is not None or shutil.which("espeak-ng") is not None


class CoquiEngine(BaseTTSEngine):
    """Moteur neuronal Coqui TTS (offline, modèles téléchargeables)."""

    def __init__(self, lang: str = "fr", speed: float = 1.0, pitch: float = 0.0, model_name: Optional[str] = None):
        super().__init__(lang, speed, pitch)
        self.model_name = model_name
        self._tts = None
        self._init_model()

    def _init_model(self):
        try:
            from TTS.api import TTS
        except ImportError as exc:
            raise RuntimeError(f"Coqui TTS non installé: {exc}")

        # Sélection d'un modèle par défaut selon la langue
        if self.model_name:
            model = self.model_name
        elif self.lang.startswith("fr"):
            model = "tts_models/fr/css10/vits"
        elif self.lang.startswith("en"):
            model = "tts_models/en/ljspeech/tacotron2-DDC"
        elif self.lang.startswith("es"):
            model = "tts_models/es/css10/vits"
        else:
            model = "tts_models/en/ljspeech/tacotron2-DDC"

        try:
            self._tts = TTS(model).to("cpu")
        except Exception as exc:
            raise RuntimeError(f"Impossible de charger le modèle Coqui '{model}': {exc}")

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> bytes:
        if self._tts is None:
            raise RuntimeError("Modèle Coqui non initialisé")
        out_path = output_path or (TEMP_DIR / f"coqui_{int(time.time()*1000)}.wav")
        self._tts.tts_to_file(text=text, file_path=str(out_path))
        return out_path.read_bytes()

    def is_available(self) -> bool:
        try:
            from TTS.api import TTS
            return True
        except Exception:
            return False


class SystemEngine(BaseTTSEngine):
    """Moteur système natif (macOS `say`, Linux `spd-say`, Windows SAPI via pyttsx3)."""

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> bytes:
        system = platform.system().lower()
        out_path = output_path or (TEMP_DIR / f"system_{int(time.time()*1000)}.wav")
        import subprocess

        if system == "darwin":
            cmd = ["say", "-o", str(out_path), text]
        elif system == "linux":
            cmd = ["spd-say", "-w", "-o", str(out_path), text]
        else:
            # Fallback pyttsx3
            engine = Pyttsx3Engine(self.lang, self.speed, self.pitch)
            return engine.synthesize(text, out_path)

        subprocess.run(cmd, check=False, capture_output=True)
        if not out_path.exists():
            raise RuntimeError("Le moteur système n'a pas généré de fichier audio")
        return out_path.read_bytes()

    def is_available(self) -> bool:
        system = platform.system().lower()
        if system == "darwin":
            return shutil.which("say") is not None
        if system == "linux":
            return shutil.which("spd-say") is not None
        return True


# =============================================================================
# 5. PIPELINE UNIFIÉE
# =============================================================================

class UltraVoiceTTS:
    """Pipeline principal de synthèse vocale multi-moteurs."""

    def __init__(self, lang: str = "fr", engine: str = ENGINE_PYTTSX3):
        self.lang = lang
        self.engine_name = engine
        self.speed = 1.0
        self.pitch = 0.0
        self.effects: List[str] = ["normalize"]
        self.voice_id: Optional[str] = None
        self.model_name: Optional[str] = None
        self._engine: Optional[BaseTTSEngine] = None
        self._lock = Lock()
        self._init_engine()

    def _init_engine(self):
        if self.engine_name == ENGINE_PYTTSX3:
            self._engine = Pyttsx3Engine(self.lang, self.speed, self.pitch, self.voice_id)
        elif self.engine_name == ENGINE_GTTS:
            self._engine = GTTSEngine(self.lang, self.speed, self.pitch)
        elif self.engine_name == ENGINE_ESPEAK:
            self._engine = EspeakEngine(self.lang, self.speed, self.pitch)
        elif self.engine_name == ENGINE_COQUI:
            self._engine = CoquiEngine(self.lang, self.speed, self.pitch, self.model_name)
        elif self.engine_name == ENGINE_SYSTEM:
            self._engine = SystemEngine(self.lang, self.speed, self.pitch)
        else:
            raise ValueError(f"Moteur inconnu: {self.engine_name}")

    def set_engine(self, engine: str):
        with self._lock:
            self.engine_name = engine
            self._init_engine()

    def set_voice(self, voice_id: str):
        self.voice_id = voice_id
        if self.engine_name == ENGINE_PYTTSX3:
            self._init_engine()

    def set_model(self, model_name: str):
        self.model_name = model_name
        if self.engine_name == ENGINE_COQUI:
            self._init_engine()

    def set_effects(self, effects: List[str]):
        self.effects = list(effects)

    def set_speed(self, speed: float):
        self.speed = max(0.5, min(3.0, speed))
        if hasattr(self._engine, "speed"):
            self._engine.speed = self.speed

    def set_pitch(self, pitch: float):
        self.pitch = max(-12.0, min(12.0, pitch))
        if hasattr(self._engine, "pitch"):
            self._engine.pitch = self.pitch

    def synthesize(
        self,
        text: str,
        output_path: Optional[Union[str, Path]] = None,
        apply_effects: bool = True,
    ) -> Path:
        """
        Synthétise le texte et sauvegarde éventuellement le résultat.
        Retourne le chemin du fichier WAV généré.
        """
        text = TextNormalizer.clean_text(text, self.lang)
        if not text:
            raise ValueError("Le texte est vide après normalisation")

        with self._lock:
            tmp_path = TEMP_DIR / f"uvtts_{int(time.time()*1000)}.wav"
            raw_bytes = self._engine.synthesize(text, tmp_path)

            if not tmp_path.exists():
                # Certains moteurs retournent directement les bytes sans écrire
                tmp_path.write_bytes(raw_bytes)

            if apply_effects and self.effects:
                self._apply_effects_to_file(tmp_path)

            if output_path:
                output_path = Path(output_path)
                shutil.copy2(tmp_path, output_path)
                return output_path
            return tmp_path

    def _apply_effects_to_file(self, wav_path: Path):
        """Lit un WAV, applique les effets et réécrit."""
        import numpy as np

        try:
            from pydub import AudioSegment
        except ImportError:
            return

        seg = AudioSegment.from_wav(str(wav_path))
        seg = seg.set_channels(1)
        sample_width = seg.sample_width
        sample_rate = seg.frame_rate
        raw = seg.raw_data

        processor = AudioProcessor(sample_rate)
        data = processor.to_float_array(raw, sample_width)
        data = processor.apply_effects(data, self.effects, self.speed, self.pitch)
        processed_bytes = processor.to_int16_bytes(data)

        new_seg = AudioSegment(
            data=processed_bytes,
            sample_width=2,
            frame_rate=sample_rate,
            channels=1,
        )
        new_seg.export(str(wav_path), format="wav")

    def speak(self, text: str):
        """Synthétise et joue immédiatement le texte."""
        path = self.synthesize(text)
        self.play_audio(path)

    def save(self, text: str, output_path: Union[str, Path], format: str = "wav"):
        """Sauvegarde la synthèse dans le format demandé."""
        path = self.synthesize(text)
        output_path = Path(output_path)
        if format.lower() == "mp3":
            from pydub import AudioSegment
            seg = AudioSegment.from_wav(str(path))
            seg.export(str(output_path), format="mp3", bitrate=DEFAULT_BITRATE)
        elif format.lower() == "ogg":
            from pydub import AudioSegment
            seg = AudioSegment.from_wav(str(path))
            seg.export(str(output_path), format="ogg")
        else:
            shutil.copy2(path, output_path)
        return output_path

    @staticmethod
    def play_audio(path: Union[str, Path]):
        """Joue un fichier audio de manière cross-platform."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)

        system = platform.system().lower()
        import subprocess

        if system == "darwin":
            subprocess.run(["afplay", str(path)], check=False)
        elif system == "linux":
            # Essaye plusieurs lecteurs
            for player in ["paplay", "aplay", "ffplay", "vlc"]:
                if shutil.which(player):
                    cmd = [player, str(path)]
                    if player == "ffplay":
                        cmd += ["-nodisp", "-autoexit", "-loglevel", "quiet"]
                    elif player == "vlc":
                        cmd += ["--play-and-exit", "--qt-start-minimized"]
                    subprocess.run(cmd, check=False, capture_output=True)
                    return
            raise RuntimeError("Aucun lecteur audio trouvé")
        elif system == "windows":
            os.startfile(str(path))
        else:
            raise RuntimeError("Système non supporté pour la lecture audio")

    def get_info(self) -> TTSEngineInfo:
        return TTSEngineInfo(
            name=self.engine_name,
            description=self._engine.__class__.__doc__ or "",
            requires_internet=(self.engine_name == ENGINE_GTTS),
            supports_offline=(self.engine_name != ENGINE_GTTS),
            voices=self._engine.list_voices(),
        )

    @staticmethod
    def available_engines() -> List[str]:
        """Liste les moteurs disponibles sur ce système."""
        available = []
        for engine in ALL_ENGINES:
            try:
                if engine == ENGINE_PYTTSX3:
                    import pyttsx3
                    available.append(engine)
                elif engine == ENGINE_GTTS:
                    import gtts
                    available.append(engine)
                elif engine == ENGINE_ESPEAK:
                    if shutil.which("espeak") or shutil.which("espeak-ng"):
                        available.append(engine)
                elif engine == ENGINE_COQUI:
                    import TTS
                    available.append(engine)
                elif engine == ENGINE_SYSTEM:
                    available.append(engine)
            except Exception:
                pass
        return available


# =============================================================================
# 6. INTERFACE GRAPHIQUE TKINTER AVANCÉE
# =============================================================================

class UltraVoiceApp:
    """Application Tkinter stylisée pour Ultra Voice TTS."""

    BG_COLOR = "#1e1e2e"
    FG_COLOR = "#cdd6f4"
    ACCENT_COLOR = "#89b4fa"
    SECONDARY_COLOR = "#313244"
    SUCCESS_COLOR = "#a6e3a1"
    WARNING_COLOR = "#f9e2af"
    ERROR_COLOR = "#f38ba8"
    FONT_FAMILY = "Segoe UI" if platform.system() == "Windows" else "Helvetica"

    def __init__(self):
        self.root = Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1100x850")
        self.root.configure(bg=self.BG_COLOR)
        self.root.minsize(900, 700)

        self.tts = None
        self.current_wav: Optional[Path] = None
        self.is_playing = False
        self.worker_queue: Queue = Queue()
        self.worker_thread = Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

        self._build_styles()
        self._build_menu()
        self._build_ui()
        self._init_tts()

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TFrame",
            background=self.BG_COLOR,
        )
        style.configure(
            "TLabel",
            background=self.BG_COLOR,
            foreground=self.FG_COLOR,
            font=(self.FONT_FAMILY, 10),
        )
        style.configure(
            "TButton",
            background=self.ACCENT_COLOR,
            foreground=self.BG_COLOR,
            font=(self.FONT_FAMILY, 10, "bold"),
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "TButton",
            background=[("active", "#74c7ec"), ("pressed", "#89b4fa")],
        )
        style.configure(
            "TScale",
            background=self.BG_COLOR,
            troughcolor=self.SECONDARY_COLOR,
            slidercolor=self.ACCENT_COLOR,
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.SECONDARY_COLOR,
            background=self.SECONDARY_COLOR,
            foreground=self.FG_COLOR,
        )

    def _build_menu(self):
        menubar = Menu(self.root, bg=self.SECONDARY_COLOR, fg=self.FG_COLOR, borderwidth=0)
        file_menu = Menu(menubar, tearoff=0, bg=self.SECONDARY_COLOR, fg=self.FG_COLOR)
        file_menu.add_command(label="Importer un texte", command=self._import_text)
        file_menu.add_command(label="Exporter WAV", command=self._export_wav)
        file_menu.add_command(label="Exporter MP3", command=self._export_mp3)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)

        help_menu = Menu(menubar, tearoff=0, bg=self.SECONDARY_COLOR, fg=self.FG_COLOR)
        help_menu.add_command(label="Fiche ICMP... pardon, Fiche TTS", command=self._show_about)
        help_menu.add_command(label="À propos", command=self._show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)
        self.root.config(menu=menubar)

    def _build_ui(self):
        # === En-tête ===
        header = Frame(self.root, bg=self.BG_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))
        Label(
            header,
            text=f"{APP_NAME}",
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            font=(self.FONT_FAMILY, 28, "bold"),
        ).pack(side=LEFT)
        Label(
            header,
            text=f"v{APP_VERSION} — Synthèse vocale avancée & gratuite",
            bg=self.BG_COLOR,
            fg=self.FG_COLOR,
            font=(self.FONT_FAMILY, 11),
        ).pack(side=LEFT, padx=(15, 0), pady=(10, 0))

        # === Panneau principal ===
        main_frame = Frame(self.root, bg=self.BG_COLOR)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # --- Colonne gauche : contrôles ---
        left_frame = Frame(main_frame, bg=self.SECONDARY_COLOR, bd=0, relief="flat")
        left_frame.pack(side=LEFT, fill=BOTH, expand=False, padx=(0, 15))
        self._build_controls(left_frame)

        # --- Colonne droite : texte et logs ---
        right_frame = Frame(main_frame, bg=self.BG_COLOR)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        self._build_text_area(right_frame)

        # === Barre de statut ===
        self.status_var = StringVar(value="Prêt")
        status_bar = Label(
            self.root,
            textvariable=self.status_var,
            bg=self.SECONDARY_COLOR,
            fg=self.FG_COLOR,
            anchor="w",
            font=(self.FONT_FAMILY, 9),
            padx=10,
            pady=5,
        )
        status_bar.pack(side=BOTTOM, fill="x")

    def _build_controls(self, parent: Frame):
        pad = {"padx": 15, "pady": 10}

        # ===== Bouton principal de génération / lecture (EN HAUT) =====
        gen_frame = Frame(parent, bg=self.SECONDARY_COLOR)
        gen_frame.pack(fill="x", padx=15, pady=(15, 5))
        self.speak_btn = Button(
            gen_frame,
            text="▶ GÉNÉRER & LIRE",
            bg=self.SUCCESS_COLOR,
            fg=self.BG_COLOR,
            font=(self.FONT_FAMILY, 14, "bold"),
            bd=0,
            relief="flat",
            height=2,
            command=self._on_speak,
        )
        self.speak_btn.pack(fill="x", pady=5)

        # Sous-boutons rapides
        quick_frame = Frame(gen_frame, bg=self.SECONDARY_COLOR)
        quick_frame.pack(fill="x")
        self.save_btn = Button(
            quick_frame,
            text="💾 Sauver",
            bg=self.ACCENT_COLOR,
            fg=self.BG_COLOR,
            font=(self.FONT_FAMILY, 10, "bold"),
            bd=0,
            relief="flat",
            command=self._on_save,
        )
        self.save_btn.pack(side=LEFT, fill="x", expand=True, padx=(0, 5))
        self.stop_btn = Button(
            quick_frame,
            text="⏹ Stop",
            bg=self.ERROR_COLOR,
            fg=self.BG_COLOR,
            font=(self.FONT_FAMILY, 10, "bold"),
            bd=0,
            relief="flat",
            command=self._on_stop,
        )
        self.stop_btn.pack(side=RIGHT, fill="x", expand=True, padx=(5, 0))

        # Séparateur visuel
        sep = Frame(parent, bg=self.BG_COLOR, height=2)
        sep.pack(fill="x", padx=15, pady=10)

        # Moteur
        Label(parent, text="Moteur TTS", bg=self.SECONDARY_COLOR, fg=self.ACCENT_COLOR, font=(self.FONT_FAMILY, 11, "bold")).pack(anchor="w", **pad)
        self.engine_var = StringVar(value=ENGINE_PYTTSX3)
        engines = UltraVoiceTTS.available_engines() or [ENGINE_GTTS]
        engine_menu = ttk.OptionMenu(parent, self.engine_var, engines[0], *engines, command=self._on_engine_change)
        engine_menu.pack(fill="x", **pad)

        # Langue
        Label(parent, text="Langue", bg=self.SECONDARY_COLOR, fg=self.ACCENT_COLOR, font=(self.FONT_FAMILY, 11, "bold")).pack(anchor="w", **pad)
        self.lang_var = StringVar(value="fr")
        lang_menu = ttk.OptionMenu(parent, self.lang_var, "fr", *list(GTTS_LANGUAGES.keys()), command=self._on_lang_change)
        lang_menu.pack(fill="x", **pad)

        # Voix
        Label(parent, text="Voix / Modèle", bg=self.SECONDARY_COLOR, fg=self.ACCENT_COLOR, font=(self.FONT_FAMILY, 11, "bold")).pack(anchor="w", **pad)
        self.voice_var = StringVar(value="Défaut")
        self.voice_menu = ttk.OptionMenu(parent, self.voice_var, "Défaut", "Défaut")
        self.voice_menu.pack(fill="x", **pad)

        # Vitesse
        Label(parent, text="Vitesse", bg=self.SECONDARY_COLOR, fg=self.ACCENT_COLOR, font=(self.FONT_FAMILY, 11, "bold")).pack(anchor="w", **pad)
        self.speed_var = DoubleVar(value=1.0)
        speed_scale = ttk.Scale(parent, from_=0.5, to=2.5, orient=HORIZONTAL, variable=self.speed_var, command=self._on_speed_change)
        speed_scale.pack(fill="x", **pad)
        self.speed_label = Label(parent, text="1.00x", bg=self.SECONDARY_COLOR, fg=self.FG_COLOR)
        self.speed_label.pack(anchor="w", padx=15)

        # Hauteur
        Label(parent, text="Hauteur (semitons)", bg=self.SECONDARY_COLOR, fg=self.ACCENT_COLOR, font=(self.FONT_FAMILY, 11, "bold")).pack(anchor="w", **pad)
        self.pitch_var = DoubleVar(value=0.0)
        pitch_scale = ttk.Scale(parent, from_=-12, to=12, orient=HORIZONTAL, variable=self.pitch_var, command=self._on_pitch_change)
        pitch_scale.pack(fill="x", **pad)
        self.pitch_label = Label(parent, text="0 st", bg=self.SECONDARY_COLOR, fg=self.FG_COLOR)
        self.pitch_label.pack(anchor="w", padx=15)

        # Effets
        Label(parent, text="Effets audio", bg=self.SECONDARY_COLOR, fg=self.ACCENT_COLOR, font=(self.FONT_FAMILY, 11, "bold")).pack(anchor="w", **pad)
        self.effect_vars: Dict[str, BooleanVar] = {}
        effects_frame = Frame(parent, bg=self.SECONDARY_COLOR)
        effects_frame.pack(fill="x", **pad)
        for key, label in EFFECTS.items():
            var = BooleanVar(value=(key in ["normalize"]))
            self.effect_vars[key] = var
            cb = Checkbutton(
                effects_frame,
                text=label,
                variable=var,
                bg=self.SECONDARY_COLOR,
                fg=self.FG_COLOR,
                selectcolor=self.BG_COLOR,
                activebackground=self.SECONDARY_COLOR,
                activeforeground=self.FG_COLOR,
                anchor="w",
            )
            cb.pack(fill="x", padx=5, pady=2)

    def _build_text_area(self, parent: Frame):
        Label(parent, text="Texte à synthétiser", bg=self.BG_COLOR, fg=self.ACCENT_COLOR, font=(self.FONT_FAMILY, 12, "bold"), anchor="w").pack(fill="x", pady=(0, 10))

        text_frame = Frame(parent, bg=self.BG_COLOR)
        text_frame.pack(fill=BOTH, expand=True)

        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side=RIGHT, fill="y")

        self.text_area = Text(
            text_frame,
            wrap="word",
            bg=self.SECONDARY_COLOR,
            fg=self.FG_COLOR,
            insertbackground=self.FG_COLOR,
            font=(self.FONT_FAMILY, 12),
            padx=10,
            pady=10,
            bd=0,
            relief="flat",
            yscrollcommand=scrollbar.set,
        )
        self.text_area.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        self.text_area.insert(END, "Bonjour et bienvenue dans Ultra Voice TTS. Cette interface vous permet de convertir du texte en parole de manière avancée, gratuite et sans clé API.")

        # Logs
        Label(parent, text="Journal", bg=self.BG_COLOR, fg=self.ACCENT_COLOR, font=(self.FONT_FAMILY, 12, "bold"), anchor="w").pack(fill="x", pady=(15, 10))
        self.log_area = scrolledtext.ScrolledText(
            parent,
            wrap="word",
            bg=self.SECONDARY_COLOR,
            fg=self.FG_COLOR,
            font=("Consolas", 9),
            height=8,
            padx=10,
            pady=10,
            bd=0,
            relief="flat",
            state=DISABLED,
        )
        self.log_area.pack(fill=BOTH, expand=False)

    def _log(self, message: str, level: str = "info"):
        color = self.FG_COLOR
        if level == "success":
            color = self.SUCCESS_COLOR
        elif level == "warning":
            color = self.WARNING_COLOR
        elif level == "error":
            color = self.ERROR_COLOR

        self.log_area.config(state=NORMAL)
        self.log_area.insert(END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.tag_config(level, foreground=color)
        self.log_area.tag_add(level, f"{self.log_area.index('end-2c linestart')}", f"{self.log_area.index('end-2c lineend')}")
        self.log_area.config(state=DISABLED)
        self.log_area.see(END)

    def _init_tts(self):
        try:
            self.tts = UltraVoiceTTS(lang=self.lang_var.get(), engine=self.engine_var.get())
            self._refresh_voices()
            self._log(f"Moteur initialisé: {self.engine_var.get()}", "success")
        except Exception as exc:
            self._log(f"Erreur initialisation TTS: {exc}", "error")
            self.tts = None

    def _refresh_voices(self):
        if self.tts is None:
            return
        try:
            info = self.tts.get_info()
            voices = info.voices or ["Défaut"]
            menu = self.voice_menu["menu"]
            menu.delete(0, END)
            for v in voices:
                menu.add_command(label=v, command=lambda val=v: self.voice_var.set(val))
            self.voice_var.set(voices[0])
        except Exception as exc:
            self._log(f"Impossible de lister les voix: {exc}", "warning")

    def _on_engine_change(self, value: str):
        self.status_var.set(f"Changement moteur: {value}...")
        self.root.update_idletasks()
        try:
            self.tts = UltraVoiceTTS(lang=self.lang_var.get(), engine=value)
            self._refresh_voices()
            self._log(f"Moteur activé: {value}", "success")
        except Exception as exc:
            self._log(f"Moteur {value} indisponible: {exc}", "error")
            self.tts = None
        self.status_var.set("Prêt")

    def _on_lang_change(self, value: str):
        if self.tts:
            self.tts.lang = value
            self._log(f"Langue changée: {GTTS_LANGUAGES.get(value, value)}", "info")

    def _on_speed_change(self, value: str):
        speed = float(value)
        self.speed_label.config(text=f"{speed:.2f}x")
        if self.tts:
            self.tts.set_speed(speed)

    def _on_pitch_change(self, value: str):
        pitch = float(value)
        self.pitch_label.config(text=f"{pitch:.0f} st")
        if self.tts:
            self.tts.set_pitch(pitch)

    def _get_selected_effects(self) -> List[str]:
        return [key for key, var in self.effect_vars.items() if var.get()]

    def _get_text(self) -> str:
        return self.text_area.get("1.0", END).strip()

    def _on_speak(self):
        text = self._get_text()
        if not text:
            messagebox.showwarning("Texte vide", "Veuillez saisir du texte à synthétiser.")
            return
        if self.tts is None:
            messagebox.showerror("Erreur", "Aucun moteur TTS disponible.")
            return

        self.status_var.set("Synthèse en cours...")
        self._log(f"Synthèse de {len(text)} caractères avec {self.engine_var.get()}", "info")
        self.worker_queue.put(("speak", text))

    def _on_save(self):
        text = self._get_text()
        if not text:
            messagebox.showwarning("Texte vide", "Veuillez saisir du texte à synthétiser.")
            return
        if self.tts is None:
            messagebox.showerror("Erreur", "Aucun moteur TTS disponible.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("Fichiers WAV", "*.wav"), ("Fichiers MP3", "*.mp3"), ("Tous fichiers", "*.*")],
        )
        if not path:
            return
        self.status_var.set("Sauvegarde en cours...")
        self._log(f"Export vers: {path}", "info")
        self.worker_queue.put(("save", text, Path(path)))

    def _on_stop(self):
        self.status_var.set("Arrêt demandé")
        self._log("Arrêt (lecture continue jusqu'à la fin du buffer courant)", "warning")

    def _worker_loop(self):
        while True:
            try:
                task = self.worker_queue.get(timeout=1)
            except Empty:
                continue

            try:
                if task[0] == "speak":
                    _, text = task
                    if self.tts is None:
                        continue
                    self.tts.set_effects(self._get_selected_effects())
                    self.current_wav = self.tts.synthesize(text)
                    self.root.after(0, lambda: self.status_var.set("Lecture en cours..."))
                    UltraVoiceTTS.play_audio(self.current_wav)
                    self.root.after(0, lambda: self.status_var.set("Prêt"))
                    self.root.after(0, lambda: self._log("Lecture terminée", "success"))
                elif task[0] == "save":
                    _, text, path = task
                    if self.tts is None:
                        continue
                    self.tts.set_effects(self._get_selected_effects())
                    fmt = "mp3" if str(path).lower().endswith(".mp3") else "wav"
                    self.tts.save(text, path, format=fmt)
                    self.root.after(0, lambda p=path: self._log(f"Fichier sauvegardé: {p}", "success"))
                    self.root.after(0, lambda: self.status_var.set("Prêt"))
            except Exception as exc:
                err = f"{exc}\n{traceback.format_exc()}"
                self.root.after(0, lambda e=err: self._log(e, "error"))
                self.root.after(0, lambda: self.status_var.set("Erreur"))

    def _import_text(self):
        path = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt"), ("Tous fichiers", "*.*")])
        if path:
            try:
                content = Path(path).read_text(encoding="utf-8")
                self.text_area.delete("1.0", END)
                self.text_area.insert(END, content)
                self._log(f"Texte importé: {path}", "success")
            except Exception as exc:
                self._log(f"Erreur import: {exc}", "error")

    def _export_wav(self):
        self._on_save()

    def _export_mp3(self):
        text = self._get_text()
        if not text or self.tts is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("Fichiers MP3", "*.mp3")])
        if path:
            self.worker_queue.put(("save", text, Path(path)))

    def _show_about(self):
        messagebox.showinfo(
            "À propos",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Synthèse vocale avancée, multi-moteurs et sans clé API.\n\n"
            "Moteurs supportés : pyttsx3, gTTS, espeak, Coqui TTS, système natif.\n"
            "Effets audio : normalisation, VAD, égalisation, vitesse, hauteur, réverb, chorus.",
        )

    def run(self):
        self.root.mainloop()


# =============================================================================
# 7. POINT D'ENTRÉE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="ultra_voice_tts.py",
        description=f"{APP_NAME} v{APP_VERSION} — Synthèse vocale avancée en ligne de commande.",
    )
    parser.add_argument("--gui", action="store_true", help="Lancer l'interface graphique")
    parser.add_argument("--speak", "-s", type=str, help="Texte à lire")
    parser.add_argument("--save", type=str, help="Chemin de sortie WAV/MP3")
    parser.add_argument("--engine", "-e", choices=ALL_ENGINES, default=ENGINE_PYTTSX3, help="Moteur TTS")
    parser.add_argument("--lang", "-l", default="fr", help="Code langue")
    parser.add_argument("--speed", type=float, default=1.0, help="Vitesse (0.5 - 2.5)")
    parser.add_argument("--pitch", type=float, default=0.0, help="Hauteur en semitons (-12 à 12)")
    parser.add_argument("--voice", type=str, help="Identifiant de voix (pyttsx3)")
    parser.add_argument("--model", type=str, help="Nom du modèle Coqui TTS")
    parser.add_argument(
        "--effects",
        nargs="+",
        choices=list(EFFECTS.keys()),
        default=["normalize"],
        help="Effets audio à appliquer",
    )
    args = parser.parse_args()

    if args.gui or (not args.speak and not args.save):
        app = UltraVoiceApp()
        app.run()
        return 0

    tts = UltraVoiceTTS(lang=args.lang, engine=args.engine)
    tts.set_speed(args.speed)
    tts.set_pitch(args.pitch)
    if args.voice:
        tts.set_voice(args.voice)
    if args.model:
        tts.set_model(args.model)
    tts.set_effects(args.effects)

    if args.speak:
        tts.speak(args.speak)
    if args.save:
        fmt = "mp3" if args.save.lower().endswith(".mp3") else "wav"
        tts.save(args.save, args.save, format=fmt)
        print(f"Audio sauvegardé: {args.save}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
