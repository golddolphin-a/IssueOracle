 SELF-APP-001
title: Linux Application Debugging - PIE/Library Link 이슈
category: Linux Application Debug
tags: [non-pie, dynamic-link, symbolic-link, compile-option, entry-point]
chipsets: [Linux (any architecture)]
severity: medium
cvd_version: all
last_updated: 2026-02-03
related_issues: []

### 📄 SELF-APP-001: Linux Application Debugging - PIE/Library Link 이슈

## 증상

### Case 1: Application이 멈추지 않음
- **현상**: Terminal에서 application 실행 시 CVD가 entry point에서 멈추지 않음
- **원인**: PIE (Position Independent Executable)로 컴파일됨

### Case 2: Library 디버깅 불가
- **현상**: CVD library view에 library가 표시되지 않음
- **원인**: Static link로 컴파일되었거나, symbolic link가 없음

---

## 즉시 시도할 해결책

### Case 1: Application이 멈추지 않을 때

**Step 1: PIE 여부 확인**

```bash
file ./my_app
```

**출력 예시:**
```
# PIE로 컴파일된 경우 (문제 있음):
ELF 64-bit LSB pie executable, ...

# non-PIE로 컴파일된 경우 (정상):
ELF 64-bit LSB executable, ... , not stripped
```

**또는:**
```bash
readelf -h ./my_app | grep Type
```

**출력 예시:**
```
# PIE (문제 있음):
Type: DYN (Shared object file)

# non-PIE (정상):
Type: EXEC (Executable file)
```

**Step 2: non-PIE로 재컴파일**

```bash
gcc -no-pie -g -o my_app main.c
```

**⚠️ 주의:**
- `-no-pie` 옵션은 GCC 6.0+ 필요
- 디버깅을 위해 `-g` 옵션 필수

---

### Case 2: Library 디버깅이 안 될 때

**Step 1: Dynamic link 확인**

```bash
ldd ./my_app
```

**출력 예시:**
```
# Dynamically linked (정상):
linux-vdso.so.1 =>  (0x00007ffff7ffa000)
libmylib.so => /usr/lib/libmylib.so (0x00007ffff7dd5000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007ffff7a0b000)

# Static linked (문제 있음):
not a dynamic executable
```

**CVD에서도 확인:**
```bash
info sharedlibrary
```

- Dynamically linked: Library 목록이 표시됨
- Static linked: 아무것도 표시되지 않음

**Step 2: Symbolic link 확인**

```bash
file /usr/lib/libmylib.so
```

**출력 예시:**
```
# Symbolic link 있음 (정상):
/usr/lib/libmylib.so: symbolic link to libmylib.so.1.0

# Symbolic link 없음 (문제 가능):
/usr/lib/libmylib.so: ELF 64-bit LSB shared object, ...
```

**또는:**
```bash
ls -l /usr/lib/libmylib.so
```

**출력 예시:**
```
# Symbolic link (정상):
lrwxrwxrwx 1 root root 15 Jan 29 10:00 libmylib.so -> libmylib.so.1.0

# Real file (symbolic link 없음):
-rwxr-xr-x 1 root root 1234567 Jan 29 10:00 libmylib.so
```

**Step 3: 올바른 방법으로 컴파일**

**Application:**
```bash
gcc -no-pie -g -o my_app main.c -lmylib
```

**Library (shared object):**
```bash
gcc -shared -fPIC -g -o libmylib.so.1.0 mylib.c
ln -s libmylib.so.1.0 libmylib.so  # Symbolic link 생성
```

---

## 근본 원인 (Root Cause)

### PIE (Position Independent Executable)

- **목적**: ASLR (Address Space Layout Randomization) 보안 기능
- **문제**: 실행 시마다 메모리 주소가 바뀜 → CVD가 entry point를 찾지 못함
- **해결**: non-PIE로 컴파일 (디버깅 환경에서는 보안보다 디버깅 가능성 우선)

### Static vs Dynamic Linking

**Static Link:**
- Library 코드가 application 바이너리에 포함됨
- CVD library view에 표시되지 않음
- Library 내부 함수 디버깅 불가

**Dynamic Link:**
- Library가 실행 시 로드됨
- CVD가 library symbol을 별도로 인식
- Library 내부 함수 디버깅 가능

### Symbolic Link

- Linux는 library 버전 관리를 위해 symbolic link 사용
- 예: `libmylib.so` → `libmylib.so.1` → `libmylib.so.1.0.2`
- CVD는 symbolic link를 따라가며 실제 파일 경로를 찾음
- Symbolic link가 없으면 CVD가 library를 못 찾을 수 있음

---

## Compile Option 체크리스트

### Application Debugging
```bash
gcc -no-pie -g -o my_app main.c
```
- `-no-pie`: PIE 비활성화 (필수)
- `-g`: Debug symbol 포함 (필수)

### Library Debugging
```bash
# Library 컴파일
gcc -shared -fPIC -g -o libmylib.so.1.0 mylib.c

# Symbolic link 생성
ln -s libmylib.so.1.0 libmylib.so

# Application 컴파일 (library와 dynamic link)
gcc -no-pie -g -o my_app main.c -lmylib -L.
```

### 검증
```bash
# Application PIE 확인
file ./my_app | grep -q "pie executable" && echo "PIE (문제)" || echo "non-PIE (정상)"

# Dynamic link 확인
ldd ./my_app | grep -q "libmylib.so" && echo "Dynamic (정상)" || echo "Static (문제)"

# Symbolic link 확인
file libmylib.so | grep -q "symbolic link" && echo "Symlink (정상)" || echo "Real file (확인 필요)"
```

---

## 관련 CVD 명령어

```bash
# Library 목록 확인
info sharedlibrary

# Application entry point 확인
info program

# Symbol 로드 상태 확인
info sources
```

---

## Common Mistakes

❌ **PIE로 컴파일**: CVD가 entry point를 찾지 못함  
❌ **Static link**: Library 디버깅 불가 (CVD library view에 안 뜸)  
❌ **Stripped binary**: Symbol 정보 없음 (`-g` 옵션 빠짐)  
❌ **Symbolic link 없음**: CVD가 library 경로를 못 찾음  

---

## 기술적 배경

### GCC의 PIE 기본값 변화

- **GCC 5.x 이전**: 기본값 non-PIE
- **GCC 6.0+**: 기본값 PIE (보안 강화)
- **영향**: 명시적으로 `-no-pie` 지정하지 않으면 PIE로 컴파일됨

### CVD의 동작 원리

1. **Application 로드 시**:
   - ELF header에서 entry point 주소 확인
   - PIE인 경우: 실행 시마다 주소 변경 → CVD가 breakpoint 설정 실패

2. **Library 로드 시**:
   - `info sharedlibrary`로 dynamic linker가 로드한 library 목록 확인
   - Static linked library는 application에 포함되어 별도로 인식 안 됨

---

## Known Limitations

1. **GCC 버전 의존성**:
   - `-no-pie` 옵션은 GCC 6.0+ 필요
   - 이전 버전은 `-fno-pie -fno-PIE` 사용

2. **Distribution 차이**:
   - Ubuntu 18.04+: 기본 PIE
   - CentOS 7: 기본 non-PIE
   - → 같은 소스도 distribution에 따라 결과 다름

3. **보안 vs 디버깅**:
   - Production: PIE 권장 (보안)
   - Development: non-PIE 필요 (디버깅)
   - → 별도 빌드 설정 권장

---

## 참고 자료

- GCC Manual: `-no-pie` option
- Linux Manual: `ld.so` (dynamic linker)
- CVD Command Reference: `info sharedlibrary`

---

## 이슈 히스토리

- **2026-02-03**: 초기 작성 (실무 경험 기반)

---

## AI 진단 제안 (메타 정보)

**이 이슈를 AI가 판단할 때:**

1. **증상 분류**:
   - "CVD가 안 멈춰요" → Case 1 (PIE 이슈)
   - "Library가 안 보여요" → Case 2 (Link 이슈)

2. **즉시 제시할 명령어**:
```bash
# PIE 확인
file ./my_app

# non-PIE로 재컴파일
gcc -no-pie -g -o my_app main.c
```

3. **Library 이슈 시 순차 확인**:
   - ldd로 dynamic link 확인
   - file로 symbolic link 확인
   - CVD `info sharedlibrary`로 최종 확인

**AI가 제시할 1차 조치:**
```
먼저 확인:
```bash
file ./my_app
```

"pie executable" 나오면 non-PIE로 재컴파일:
```bash
gcc -no-pie -g -o my_app main.c
```

결과 알려주세요.