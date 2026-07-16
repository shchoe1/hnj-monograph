#!/usr/bin/env python3
"""
verify_historical.py · 조선 사료 원전 검증 · historical-verifier Skill용

허용 원전 DB:
- sillok.history.go.kr (조선왕조실록)
- sjw.history.go.kr (승정원일기)
- db.itkc.or.kr (한국고전번역원 · 난중일기 국역)
- oasis.kiom.re.kr (KTKP · 동의보감 등)
- kyudb.snu.ac.kr (규장각)

사용법:
    python scripts/verify_historical.py --file chapters/ch02-joseon-yi-sunsin.md \
        --output references/historical-verification-ch2.md
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

APPROVED_DBS = [
    "sillok.history.go.kr",
    "sjw.history.go.kr",
    "db.itkc.or.kr",
    "oasis.kiom.re.kr",
    "kyudb.snu.ac.kr",
    "hcs.chungmugong.go.kr",
    "db.history.go.kr",
]

BLACKLIST_KEYWORDS = [
    "불멸의 이순신", "명량", "한산", "노량",   # 드라마·영화
    "namu.wiki", "위키피디아", "wikipedia",
    "김훈", "칼의 노래",                        # 소설
]

def check_historical_citation(citation):
    """사료 인용 검증"""
    result = {"verified": False, "reason": None, "sources_found": []}

    # Blacklist 검사
    for kw in BLACKLIST_KEYWORDS:
        if kw.lower() in citation.lower():
            result["reason"] = f"BLACKLISTED: {kw} (소설/드라마/위키)"
            return result

    # 허용 DB URL 확인
    for db in APPROVED_DBS:
        if db in citation:
            result["sources_found"].append(db)

    if not result["sources_found"]:
        result["reason"] = "NO_APPROVED_DB_URL_FOUND"
        return result

    # 최소 요건: 사료명·연월일·원문·URL 4가지
    has_source_name = any(x in citation for x in ["난중일기", "동의보감", "향약집성방", "본초강목", "조선왕조실록", "승정원일기", "이충무공전서", "의방유취", "의림촬요"])
    has_date = bool(re.search(r'\d{4}|갑오|을미|병신|정유|무술', citation))
    has_url = bool(re.search(r'https?://', citation))

    if not (has_source_name and has_date and has_url):
        missing = []
        if not has_source_name: missing.append("사료명")
        if not has_date: missing.append("연월일")
        if not has_url: missing.append("URL")
        result["reason"] = f"MISSING_REQUIRED_FIELDS: {', '.join(missing)}"
        return result

    result["verified"] = True
    return result

def process_file(file_path, output_md):
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    pattern = re.compile(r'\[H(\d+)\](.+?)\[PENDING-HISTORICAL-VERIFY\]', re.DOTALL)
    matches = pattern.findall(content)

    print(f"조선 사료 인용 검증: {len(matches)}개")
    verified_count = 0
    report_lines = [f"# 조선 사료 검증 리포트 · {datetime.now().date()}\n\n"]

    for hid, ctext in matches:
        result = check_historical_citation(ctext)
        if result["verified"]:
            verified_count += 1
            print(f"  [H{hid}] ✓ VERIFIED ({', '.join(result['sources_found'])})")
            report_lines.append(f"- [H{hid}] ✓ VERIFIED · 소스: {', '.join(result['sources_found'])}\n")
        else:
            print(f"  [H{hid}] ✗ FAILED: {result['reason']}")
            report_lines.append(f"- [H{hid}] ✗ FAILED · 이유: {result['reason']}\n")

    print(f"\n검증 완료: {verified_count}/{len(matches)}")
    if output_md:
        Path(output_md).write_text("".join(report_lines), encoding="utf-8")
        print(f"리포트 저장: {output_md}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--output", help="검증 리포트 Markdown 저장 경로")
    args = parser.parse_args()
    process_file(args.file, args.output)
