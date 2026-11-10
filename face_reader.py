import json
import logging
import os
from dataclasses import dataclass, field

import openai
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from prompts import SYSTEM_PROMPT, USER_PROMPT

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_DETAIL = "auto"  # "low" is cheaper, "high" reads more facial detail
MAX_TOKENS = 1500


class FaceReadError(Exception):
    """Raised with a user-facing message when the API call fails."""


@dataclass
class Reading:
    status: str  # "ok" | "no_face" | "refused" | "raw"
    data: dict = field(default_factory=dict)
    text: str = ""  # refusal message or unparsed model output


def _get_setting(name: str, default: str | None = None) -> str | None:
    """Read a setting from Streamlit secrets first (Cloud), then environment/.env (local)."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass  # no secrets.toml locally
    return os.getenv(name) or default


def get_api_key() -> str | None:
    return _get_setting("OPENAI_API_KEY")


def get_model() -> str:
    return _get_setting("OPENAI_MODEL", DEFAULT_MODEL)


def get_detail() -> str:
    detail = _get_setting("OPENAI_IMAGE_DETAIL", DEFAULT_DETAIL)
    return detail if detail in ("low", "high", "auto") else DEFAULT_DETAIL


def _clamp_score(value) -> int:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 0


def _as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _normalize(data: dict) -> dict:
    """Coerce model output into the shape the UI expects, so odd responses can't crash rendering."""
    data["features"] = _as_dict(data.get("features"))
    data["fortune"] = _as_dict(data.get("fortune"))
    data["scores"] = {k: _clamp_score(v) for k, v in _as_dict(data.get("scores")).items()}
    personality = data.get("personality")
    data["personality"] = [str(p) for p in personality] if isinstance(personality, list) else []
    data["lucky"] = _as_dict(data.get("lucky"))
    return data


def _call_api(image_data_url: str):
    client = OpenAI(api_key=get_api_key())
    try:
        return client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_data_url, "detail": get_detail()},
                        },
                    ],
                },
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=MAX_TOKENS,  # works for gpt-4o and newer reasoning models
        )
    except openai.AuthenticationError:
        logger.exception("OpenAI authentication failed")
        raise FaceReadError("API 키가 올바르지 않아요. 설정된 OPENAI_API_KEY를 확인해 주세요.")
    except openai.RateLimitError:
        logger.exception("OpenAI rate limit / quota")
        raise FaceReadError("요청이 많거나 사용 한도를 넘었어요. 잠시 후 다시 시도해 주세요.")
    except openai.APIConnectionError:
        logger.exception("OpenAI connection error")
        raise FaceReadError("OpenAI 서버에 연결할 수 없어요. 네트워크를 확인하고 다시 시도해 주세요.")
    except openai.APIError:
        logger.exception("OpenAI API error")
        raise FaceReadError("관상 분석 중 오류가 발생했어요. 잠시 후 다시 시도해 주세요.")


def read_face(image_data_url: str) -> Reading:
    """Send the image to the OpenAI vision model and return a parsed Reading."""
    response = _call_api(image_data_url)
    message = response.choices[0].message

    refusal = getattr(message, "refusal", None)
    if refusal:
        return Reading(status="refused", text=refusal)

    content = message.content or ""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        logger.warning("Failed to parse model output as JSON")
        return Reading(status="raw", text=content)

    if not isinstance(data, dict):
        return Reading(status="raw", text=content)
    if not data.get("face_detected", False):
        return Reading(status="no_face")
    if not data.get("summary"):
        # JSON came back but without a reading — treat as a soft refusal
        return Reading(status="raw", text=content)
    return Reading(status="ok", data=_normalize(data))
