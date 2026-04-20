"""Step 0-A: 옵시디언 폴더 스캔 — MD5 해시로 변경 감지"""

import os
import hashlib
import json
from pathlib import Path
from src.utils import load_json, save_json


def scan_obsidian_folder(obsidian_path: str = "obsidian/좀비파크 프로젝트") -> dict:
    """옵시디언 폴더를 스캔하여 변경사항 감지.

    Returns:
        {
            "new_files": [{"path": str, "content": str}],
            "modified_files": [{"path": str, "content": str}],
            "unchanged_files": [str],
            "deleted_files": [str]
        }
    """
    obsidian_root = Path(obsidian_path)
    scan_log_path = Path("data/scan_log.json")

    # 이전 스캔 기록 로드
    prev_scan = load_json(str(scan_log_path))

    # 현재 파일 스캔
    current_scan = {}
    if obsidian_root.exists():
        for md_file in obsidian_root.rglob("*.md"):
            rel_path = str(md_file.relative_to(obsidian_root))
            try:
                content = md_file.read_text(encoding='utf-8')
            except Exception:
                continue
            file_hash = hashlib.md5(content.encode()).hexdigest()
            current_scan[rel_path] = {
                "hash": file_hash,
                "size": len(content),
                "content": content
            }

    # 변경사항 감지
    changes = {
        "new_files": [],
        "modified_files": [],
        "unchanged_files": [],
        "deleted_files": []
    }

    for path, info in current_scan.items():
        if path not in prev_scan:
            changes["new_files"].append({
                "path": path,
                "content": info["content"]
            })
        elif info["hash"] != prev_scan[path].get("hash", ""):
            changes["modified_files"].append({
                "path": path,
                "content": info["content"]
            })
        else:
            changes["unchanged_files"].append(path)

    for path in prev_scan:
        if path not in current_scan:
            changes["deleted_files"].append(path)

    # 현재 스캔 기록 저장 (content 제외, hash만)
    save_data = {p: {"hash": i["hash"], "size": i["size"]}
                 for p, i in current_scan.items()}
    save_json(str(scan_log_path), save_data)

    print(f"   스캔 완료: 전체 {len(current_scan)}개 파일")
    print(f"   새 파일: {len(changes['new_files'])}, "
          f"수정: {len(changes['modified_files'])}, "
          f"삭제: {len(changes['deleted_files'])}")

    return changes
