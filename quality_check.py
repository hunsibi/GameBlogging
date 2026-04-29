#!/usr/bin/env python3
"""
quality_check.py — QER 포스팅 품질 자동 검증기
Usage: python quality_check.py --file shared/current_post.html
"""
import re
import json
import argparse
from pathlib import Path
from datetime import datetime


def strip_html(html: str) -> str:
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<[^>]+>', ' ', html)
    for ent, ch in [('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>')]:
        html = html.replace(ent, ch)
    return re.sub(r'\s+', ' ', html).strip()


def load_banned_words() -> list[str]:
    try:
        p = Path(__file__).parent / 'knowledge' / 'banned-words.json'
        data = json.loads(p.read_text(encoding='utf-8'))
        words = []
        for cat in data.get('categories', {}).values():
            words.extend(cat.get('words', []))
        return words
    except Exception:
        return []


def check(html: str, filename: str = '') -> dict:
    text = strip_html(html)
    results = []

    # 1. HTML 태그 닫힘
    block_tags = ['div', 'h1', 'h2', 'h3', 'p', 'span']
    unclosed = []
    for tag in block_tags:
        opens = len(re.findall(rf'<{tag}[\s>]', html, re.IGNORECASE))
        closes = len(re.findall(rf'</{tag}>', html, re.IGNORECASE))
        if opens != closes:
            unclosed.append(f'<{tag}> {opens}개/{closes}개')
    results.append({
        'name': 'HTML 태그 닫힘',
        'pass': len(unclosed) == 0,
        'detail': 'HTML 구조 정상' if not unclosed else f'불일치: {", ".join(unclosed)}'
    })

    # 2. 이미지 수
    img_count = len(re.findall(r'<img\s', html, re.IGNORECASE))
    results.append({
        'name': '이미지 수',
        'pass': img_count >= 3,
        'detail': f'{img_count}장 포함 (권장 ≥ 3장)'
    })

    # 3. 챕터 수 (h3 기준)
    chapter_count = len(re.findall(r'<h3[\s>]', html, re.IGNORECASE))
    results.append({
        'name': '챕터 수',
        'pass': chapter_count >= 3,
        'detail': f'{chapter_count}개 챕터 (권장 ≥ 3)'
    })

    # 4. 한글 비율
    korean_chars = len(re.findall(r'[가-힣]', text))
    total_chars = len(re.sub(r'\s', '', text))
    korean_ratio = (korean_chars / total_chars * 100) if total_chars > 0 else 0
    results.append({
        'name': '한글 비율',
        'pass': korean_ratio >= 70,
        'detail': f'한글 {korean_ratio:.1f}% (권장 ≥ 70%)'
    })

    # 5. 글자수 (공백 제외)
    char_count = total_chars
    results.append({
        'name': '글자수',
        'pass': char_count >= 500,
        'detail': f'공백제외 {char_count}자 (권장 ≥ 500자)'
    })

    # 6. 금칙어
    banned = load_banned_words()
    hits = [w for w in banned if w in text]
    results.append({
        'name': '금칙어',
        'pass': len(hits) == 0,
        'detail': '없음' if not hits else f'발견: {", ".join(hits[:5])}'
    })

    # 7. Base64 이미지 유효성
    b64_imgs = re.findall(
        r'data:image/[^;]+;base64,([A-Za-z0-9+/=]{100,})', html
    )
    results.append({
        'name': 'Base64 이미지 유효성',
        'pass': len(b64_imgs) >= 1,
        'detail': f'유효한 Base64 이미지 {len(b64_imgs)}장'
    })

    warnings = sum(1 for r in results if not r['pass'])
    return {
        'file': filename,
        'checked_at': datetime.now().isoformat(),
        'char_count': char_count,
        'image_count': img_count,
        'chapter_count': chapter_count,
        'results': results,
        'warnings': warnings,
        'passed': warnings == 0,
    }


def main():
    parser = argparse.ArgumentParser(description='QER 포스팅 품질 검증기')
    parser.add_argument('--file', required=True, help='검사할 HTML 파일 경로')
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f'파일 없음: {args.file}')
        return

    html = path.read_text(encoding='utf-8')
    report = check(html, args.file)

    print(f'\n📋 QER 품질 리포트')
    print(f'파일: {args.file}')
    print(f'글자수: {report["char_count"]}자  이미지: {report["image_count"]}장  챕터: {report["chapter_count"]}개\n')

    for r in report['results']:
        mark = '✅ PASS' if r['pass'] else '⚠️  WARN'
        print(f'{mark}  {r["name"]:<20} — {r["detail"]}')

    status = '모든 검사 통과' if report['passed'] else f'{report["warnings"]}개 경고'
    print(f'\n결과: {status}\n')

    report_path = path.parent / 'quality-report.json'
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(f'리포트 저장: {report_path}')


if __name__ == '__main__':
    main()
