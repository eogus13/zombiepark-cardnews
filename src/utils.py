"""공통 유틸리티 함수"""

import json
from pathlib import Path


def load_json(filepath: str) -> dict:
    """JSON 파일 로드. 없으면 빈 dict 반환."""
    path = Path(filepath)
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return {}


def save_json(filepath: str, data) -> None:
    """JSON 파일 저장."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
