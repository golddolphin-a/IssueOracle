#!/usr/bin/env python3
"""
Knowledge Review System - 망각곡선 기반 복습 관리
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 설정
DATA_FILE = ".review-data.json"
KNOWLEDGE_DIR = "knowledge"
INTERVALS = [1, 3, 7, 14, 30, 60]  # 복습 간격 (일)

def load_data():
    """review data 로드"""
    if not Path(DATA_FILE).exists():
        return {}
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """review data 저장"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_file(filename):
    """새 파일 추가"""
    data = load_data()
    
    # knowledge/ 경로 확인
    file_path = Path(KNOWLEDGE_DIR) / filename
    if not file_path.exists():
        print(f"❌ 파일이 없습니다: {file_path}")
        return
    
    if filename in data:
        print(f"⚠️  이미 등록된 파일입니다: {filename}")
        return
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    data[filename] = {
        "created": str(today),
        "last_reviewed": None,
        "review_count": 0,
        "next_review": str(tomorrow),
        "ease_factor": 2.5
    }
    
    save_data(data)
    print(f"✅ 등록 완료: {filename}")
    print(f"   첫 복습: {tomorrow}")

def check_today():
    """오늘 복습할 파일 리스트"""
    data = load_data()
    today = datetime.now().date()
    
    due_files = []
    for filename, info in data.items():
        next_review = datetime.strptime(info['next_review'], '%Y-%m-%d').date()
        if next_review <= today:
            days_overdue = (today - next_review).days
            due_files.append((filename, info, days_overdue))
    
    if not due_files:
        print("🎉 오늘 복습할 파일이 없습니다!")
        return
    
    # 오래된 순으로 정렬
    due_files.sort(key=lambda x: x[2], reverse=True)
    
    print(f"📚 오늘 복습할 파일 ({len(due_files)}개):\n")
    for i, (filename, info, overdue) in enumerate(due_files, 1):
        count = info['review_count']
        overdue_str = f" (⚠️ {overdue}일 지남)" if overdue > 0 else ""
        print(f"  {i}. {filename} (복습 {count}회차){overdue_str}")

def check_today_files_only():
    """오늘 복습할 파일명만 출력 (bat 파일용)"""
    data = load_data()
    today = datetime.now().date()
    
    for filename, info in data.items():
        next_review = datetime.strptime(info['next_review'], '%Y-%m-%d').date()
        if next_review <= today:
            print(filename)

def mark_done(filename):
    """복습 완료 처리"""
    data = load_data()
    
    if filename not in data:
        print(f"❌ 등록되지 않은 파일입니다: {filename}")
        return
    
    info = data[filename]
    today = datetime.now().date()
    
    # 복습 횟수 증가
    info['review_count'] += 1
    info['last_reviewed'] = str(today)
    
    # 다음 복습 날짜 계산
    count = info['review_count']
    if count <= len(INTERVALS):
        interval = INTERVALS[count - 1]
    else:
        # 마지막 간격 * 2 (60일 → 120일 → ...)
        interval = INTERVALS[-1] * (2 ** (count - len(INTERVALS)))
    
    next_review = today + timedelta(days=interval)
    info['next_review'] = str(next_review)
    
    save_data(data)
    
    print(f"✅ 복습 완료: {filename}")
    print(f"   복습 횟수: {count}회")
    print(f"   다음 복습: {next_review} (+{interval}일)")

def list_all():
    """전체 복습 상태"""
    data = load_data()
    
    if not data:
        print("📝 등록된 파일이 없습니다.")
        print(f"\n사용법: python review.py add <filename>")
        return
    
    today = datetime.now().date()
    
    print(f"📊 전체 복습 상태 ({len(data)}개)\n")
    
    items = []
    for filename, info in data.items():
        next_review = datetime.strptime(info['next_review'], '%Y-%m-%d').date()
        days_until = (next_review - today).days
        items.append((filename, info, days_until))
    
    # 다음 복습일 순으로 정렬
    items.sort(key=lambda x: x[2])
    
    for filename, info, days_until in items:
        count = info['review_count']
        next_review = info['next_review']
        
        if days_until < 0:
            status = f"⚠️  {abs(days_until)}일 지남"
        elif days_until == 0:
            status = "📌 오늘"
        else:
            status = f"⏰ {days_until}일 후"
        
        print(f"  {filename}")
        print(f"    복습: {count}회 | 다음: {next_review} ({status})")
        print()

def show_help():
    """사용법 출력"""
    help_text = """
📚 Knowledge Review System

사용법:
  python review.py add <filename>     새 파일 등록
  python review.py check              오늘 복습할 파일 확인
  python review.py done <filename>    복습 완료 처리
  python review.py list               전체 상태 보기

예시:
  python review.py add cvd-timeout.md
  python review.py check
  python review.py done cvd-timeout.md
"""
    print(help_text)

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("❌ 파일명을 입력하세요: python review.py add <filename>")
            return
        add_file(sys.argv[2])
    
    elif command == "check":
        if len(sys.argv) > 2 and sys.argv[2] == "--files-only":
            check_today_files_only()
        else:
            check_today()
    
    elif command == "done":
        if len(sys.argv) < 3:
            print("❌ 파일명을 입력하세요: python review.py done <filename>")
            return
        mark_done(sys.argv[2])
    
    elif command == "list":
        list_all()
    
    else:
        print(f"❌ 알 수 없는 명령어: {command}")
        show_help()

if __name__ == "__main__":
    main()