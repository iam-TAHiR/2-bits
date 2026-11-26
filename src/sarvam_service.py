"""SAKHI — Sarvam AI Speech-to-Text & Text-to-Speech Service.

Uses official Sarvam AI REST endpoints:
- STT: POST https://api.sarvam.ai/speech-to-text (model: saaras:v4)
- TTS: POST https://api.sarvam.ai/text-to-speech (model: bulbul:v3)

Credentials are read strictly from environment (.env -> SARVAM_API_KEY).
Never fabricates transcripts or audio when credentials are missing or API fails.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("sakhi.sarvam")

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"
SARVAM_CHAT_URL = "https://api.sarvam.ai/v2/chat/completions"

DEFAULT_STT_MODEL = os.environ.get("SARVAM_STT_MODEL", "saaras:v4")
DEFAULT_TTS_MODEL = os.environ.get("SARVAM_TTS_MODEL", "bulbul:v3")
DEFAULT_TRANSLATE_MODEL = os.environ.get("SARVAM_TRANSLATE_MODEL", "mayura:v1")
DEFAULT_CHAT_MODEL = os.environ.get("SARVAM_CHAT_MODEL", "sarvam-105b")

SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".aac", ".flac", ".ogg", ".opus", ".m4a", ".mp4", ".webm", ".amr", ".wma"
}
SUPPORTED_LANGUAGES = {
    "en-IN", "hi-IN", "kn-IN", "ta-IN", "te-IN", "ml-IN", "mr-IN", "gu-IN", "bn-IN", "pa-IN", "od-IN", "unknown"
}
MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB safety limit
MAX_TTS_CHARS = 2500  # Official Sarvam REST limit


def get_sarvam_api_key() -> str:
    return (os.environ.get("SARVAM_API_KEY") or "").strip()


class SarvamSpeechService:
    """Modular Sarvam AI STT/TTS client with validation, timeouts, and safe retries."""

    def __init__(self, timeout_seconds: float = 20.0):
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def is_configured() -> bool:
        return bool(get_sarvam_api_key())

    def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "recording.webm",
        content_type: str = "audio/webm",
        language_code: str = "unknown",
        mode: str = "transcribe",
    ) -> Dict[str, Any]:
        """Transcribe audio via Sarvam AI STT REST API."""
        api_key = get_sarvam_api_key()
        if not api_key:
            return {
                "success": False,
                "configured": False,
                "provider": "Sarvam AI",
                "error": "SARVAM_API_KEY is not configured in environment/.env. Cannot transcribe audio without API credentials.",
            }

        if not audio_bytes:
            return {
                "success": False,
                "configured": True,
                "provider": "Sarvam AI",
                "error": "Empty audio recording received. Please record again.",
            }

        if len(audio_bytes) > MAX_AUDIO_BYTES:
            return {
                "success": False,
                "configured": True,
                "provider": "Sarvam AI",
                "error": f"Audio file exceeds {MAX_AUDIO_BYTES // (1024 * 1024)} MB limit.",
            }

        ext = Path(filename or "recording.webm").suffix.lower() or ".webm"
        if ext not in SUPPORTED_AUDIO_EXTENSIONS:
            return {
                "success": False,
                "configured": True,
                "provider": "Sarvam AI",
                "error": f"Unsupported audio format '{ext}'. Supported: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}",
            }

        lang = language_code if language_code in SUPPORTED_LANGUAGES else "unknown"
        safe_mode = mode if mode in {"transcribe", "translate", "verbatim", "translit", "codemix"} else "transcribe"

        headers = {"api-subscription-key": api_key}
        data = {
            "model": DEFAULT_STT_MODEL,
            "language_code": lang,
            "mode": safe_mode,
        }
        files = {
            "file": (filename or "recording.webm", audio_bytes, content_type or "audio/webm")
        }

        last_err: Optional[str] = None
        for attempt in range(2):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    resp = client.post(SARVAM_STT_URL, headers=headers, data=data, files=files)
                if resp.status_code == 200:
                    payload = resp.json()
                    transcript = (payload.get("transcript") or "").strip()
                    detected_lang = payload.get("language_code") or lang
                    if not transcript:
                        return {
                            "success": False,
                            "configured": True,
                            "provider": "Sarvam AI",
                            "error": "Sarvam STT returned an empty transcript. Please speak clearly and try again.",
                        }
                    return {
                        "success": True,
                        "configured": True,
                        "provider": "Sarvam AI",
                        "model": DEFAULT_STT_MODEL,
                        "transcript": transcript,
                        "language_code": detected_lang,
                        "request_id": payload.get("request_id"),
                    }

                if resp.status_code in (429, 500, 502, 503, 504) and attempt == 0:
                    last_err = f"Sarvam STT temporary error (HTTP {resp.status_code})"
                    continue

                err_detail = resp.text[:250]
                logger.warning("Sarvam STT failed with HTTP %s", resp.status_code)
                return {
                    "success": False,
                    "configured": True,
                    "provider": "Sarvam AI",
                    "error": f"Sarvam STT API error (HTTP {resp.status_code}): {err_detail}",
                }
            except httpx.TimeoutException:
                last_err = "Sarvam STT request timed out."
                if attempt == 0:
                    continue
            except Exception as e:
                logger.error("Sarvam STT transport error: %s", type(e).__name__)
                last_err = f"Sarvam STT connection error: {type(e).__name__}"
                break

        return {
            "success": False,
            "configured": True,
            "provider": "Sarvam AI",
            "error": last_err or "Sarvam STT failed.",
        }

    def synthesize_speech(
        self,
        text: str,
        language_code: str = "en-IN",
        speaker: str = "ritu",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convert text to speech via Sarvam AI TTS REST API."""
        clean_text = (text or "").strip()
        if not clean_text:
            return {
                "success": False,
                "configured": self.is_configured(),
                "provider": "Sarvam AI",
                "error": "Text for TTS cannot be empty.",
            }

        api_key = get_sarvam_api_key()
        if not api_key:
            return {
                "success": False,
                "configured": False,
                "provider": "Sarvam AI",
                "error": "SARVAM_API_KEY is not configured in environment/.env.",
            }

        if len(clean_text) > MAX_TTS_CHARS:
            clean_text = clean_text[:MAX_TTS_CHARS]

        lang = language_code if (language_code in SUPPORTED_LANGUAGES and language_code != "unknown") else "en-IN"
        tts_model = model or DEFAULT_TTS_MODEL

        headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json",
        }
        body = {
            "text": clean_text,
            "target_language_code": lang,
            "language_code": lang,
            "model": tts_model,
            "speaker": speaker or "ritu",
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.post(SARVAM_TTS_URL, headers=headers, json=body)
            if resp.status_code == 200:
                payload = resp.json()
                audios = payload.get("audios") or []
                if not audios or not isinstance(audios, list):
                    return {
                        "success": False,
                        "configured": True,
                        "provider": "Sarvam AI",
                        "error": "Sarvam TTS returned no audio data.",
                    }
                return {
                    "success": True,
                    "configured": True,
                    "provider": "Sarvam AI",
                    "model": tts_model,
                    "language_code": lang,
                    "audio_base64": audios[0],
                    "mime_type": "audio/wav",
                }
            logger.warning("Sarvam TTS failed with HTTP %s", resp.status_code)
            return {
                "success": False,
                "configured": True,
                "provider": "Sarvam AI",
                "error": f"Sarvam TTS API error (HTTP {resp.status_code}): {resp.text[:200]}",
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "configured": True,
                "provider": "Sarvam AI",
                "error": "Sarvam TTS request timed out.",
            }
        except Exception as e:
            logger.error("Sarvam TTS error: %s", type(e).__name__)
            return {
                "success": False,
                "configured": True,
                "provider": "Sarvam AI",
                "error": f"Sarvam TTS connection error: {type(e).__name__}",
            }

    def translate_text(
        self,
        text: str,
        source_language_code: str = "auto",
        target_language_code: str = "en-IN",
        mode: str = "modern-colloquial",
    ) -> Dict[str, Any]:
        """Translate text via Sarvam AI Translate REST API (mayura:v1)."""
        clean_text = (text or "").strip()
        if not clean_text:
            return {"success": False, "configured": self.is_configured(), "error": "Empty text"}

        api_key = get_sarvam_api_key()
        if not api_key:
            return {
                "success": False,
                "configured": False,
                "provider": "Sarvam AI",
                "error": "SARVAM_API_KEY is not configured.",
            }

        src = source_language_code if source_language_code in SUPPORTED_LANGUAGES or source_language_code == "auto" else "auto"
        if src == "unknown":
            src = "auto"
        tgt = target_language_code if (target_language_code in SUPPORTED_LANGUAGES and target_language_code != "unknown") else "en-IN"

        headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json",
        }
        body = {
            "input": clean_text[:1000],
            "source_language_code": src,
            "target_language_code": tgt,
            "model": DEFAULT_TRANSLATE_MODEL,
            "mode": mode,
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.post(SARVAM_TRANSLATE_URL, headers=headers, json=body)
            if resp.status_code == 200:
                payload = resp.json()
                translated = (payload.get("translated_text") or "").strip()
                if translated:
                    return {
                        "success": True,
                        "configured": True,
                        "provider": "Sarvam AI",
                        "model": DEFAULT_TRANSLATE_MODEL,
                        "translated_text": translated,
                        "source_language_code": payload.get("source_language_code") or src,
                        "target_language_code": tgt,
                    }
            logger.warning("Sarvam Translate failed with HTTP %s", resp.status_code)
            return {
                "success": False,
                "configured": True,
                "provider": "Sarvam AI",
                "error": f"Sarvam Translate HTTP {resp.status_code}",
            }
        except Exception as e:
            logger.warning("Sarvam Translate error: %s", type(e).__name__)
            return {
                "success": False,
                "configured": True,
                "provider": "Sarvam AI",
                "error": f"Sarvam Translate error: {type(e).__name__}",
            }

    def chat_completion(
        self,
        messages: list,
        temperature: float = 0.2,
        max_tokens: int = 350,
    ) -> Dict[str, Any]:
        """Grounded chat completion via Sarvam AI (sarvam-105b)."""
        api_key = get_sarvam_api_key()
        if not api_key:
            return {"success": False, "configured": False, "error": "SARVAM_API_KEY not configured"}

        headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json",
        }
        body = {
            "model": DEFAULT_CHAT_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.post(SARVAM_CHAT_URL, headers=headers, json=body)
            if resp.status_code == 200:
                payload = resp.json()
                choices = payload.get("choices") or []
                if choices:
                    content = (choices[0].get("message", {}).get("content") or "").strip()
                    if content:
                        return {
                            "success": True,
                            "configured": True,
                            "model": DEFAULT_CHAT_MODEL,
                            "content": content,
                        }
            return {"success": False, "configured": True, "error": f"Sarvam Chat HTTP {resp.status_code}"}
        except Exception as e:
            logger.warning("Sarvam Chat error: %s", type(e).__name__)
            return {"success": False, "configured": True, "error": f"Sarvam Chat error: {type(e).__name__}"}
