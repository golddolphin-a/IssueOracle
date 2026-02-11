@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo.
echo ============================================
echo   📚 Knowledge Review System
echo ============================================
echo.

REM Step 1: 새 파일 자동 등록
echo [Step 1] 새 파일 자동 등록 중...
echo.
for %%f in (knowledge\*.md) do (
    python review.py add %%~nxf 2>nul
)

echo.
echo ============================================
echo.

REM Step 2: 오늘 복습할 파일 확인
echo [Step 2] 오늘 복습할 내용 확인
echo.
python review.py check

REM Step 3: 복습할 파일 목록 가져오기
python review.py check --files-only > temp_review_list.txt 2>nul

REM 파일이 있는지 확인
for /f %%a in ('type temp_review_list.txt ^| find /c /v ""') do set count=%%a

if %count%==0 (
    echo.
    echo 복습할 파일이 없습니다!
    del temp_review_list.txt
    pause
    exit /b
)

echo.
echo ============================================
echo [Step 3] 복습 시작
echo ============================================
echo.

REM Step 4: 파일 하나씩 처리
set /a num=0
for /f "usebackq tokens=*" %%f in ("temp_review_list.txt") do (
    set /a num+=1
    echo.
    echo [!num!] 파일 열기: %%f
    echo.
    
    REM 파일 열기 (기본 프로그램으로)
    start "" /wait "knowledge\%%f"
    
    echo.
    set /p done="복습 완료했나요? (y/n): "
    
    if /i "!done!"=="y" (
        python review.py done %%f
        echo.
    ) else (
        echo ⏭️  스킵했습니다.
        echo.
    )
)

REM 임시 파일 삭제
del temp_review_list.txt

echo.
echo ============================================
echo 🎉 복습 세션 완료!
echo ============================================
echo.
pause