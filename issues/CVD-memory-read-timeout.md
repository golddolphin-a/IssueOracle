# JTAG-RISCV-004: Memory Read Timeout with Slow Target Clock

## 🔍 증상 매칭 키워드
- memory read failed
- response timeout
- unknown error 0x00000002
- target clock slow
- 0.05 이하 클럭
- memory dump error
- read timeout

## ⚡ 즉시 시도할 해결책

### 1차 해결책: Response Timeout 조정 (성공률: 100% - 1/1 케이스)

```
DEBUG.ResponseTimeOut <value_in_ms>
```

**설정 방법:**
1. CVD 메뉴: `Menu -> Config -> Debugger`에서 현재 값 확인
2. Target clock 속도에 맞춰 timeout 값 증가
3. 테스트하면서 최적값 찾기 (target마다 다름)

**예시:**
- Target clock 0.05 이하인 경우: 10000ms (10초)부터 시작
- 여전히 timeout 발생 시: 20000ms, 30000ms로 점진적 증가

### 2차 해결책: JTAG Clock 조정 (보조 방법)

**참고사항:**
- 대부분의 사용자가 이미 최대값 사용 중
- Target clock이 극도로 느린 경우 효과 제한적
- Response timeout 조정이 더 효과적

## 🌳 트러블슈팅 트리

```
Target clock 0.05 이하 & Memory read timeout 발생
    ↓
[1차] DEBUG.ResponseTimeOut 증가 (10000ms부터 시작)
    ↓
    ├─ 성공 → 문제 해결
    └─ 실패 → timeout 값 추가 증가 (20000ms, 30000ms...)
        ↓
        ├─ 성공 → 문제 해결
        └─ 지속 실패 → 에스컬레이션 (메일 문의)
```

## 📋 환경 조건

**발생 조건:**
- Target clock: 0.05 이하 (매우 느린 클럭)
- Debug mode 진입: 정상
- Memory read 시도: Timeout 발생

**에러 메시지 예시:**
```
Error - Memory read failed from 0x[ADDRESS] - unknown error (0x00000002)
```

**확인 필요 정보:**
- CVD 버전
- Firmware 버전
- Target mode (sysup / attach / prepare 중 어느 모드에서 발생했는지)

## 🔧 상세 CVD 명령어

### Timeout 값 조회
```
DEBUG.ResponseTimeOut?
```

### Timeout 값 설정
```
DEBUG.ResponseTimeOut <value_in_ms>
```
- 단위: ms (밀리초)
- 예: `DEBUG.ResponseTimeOut 10000` (10초)

### GUI에서 확인
- Menu → Config → Debugger
- Response Timeout 항목 확인

## 🚨 에스컬레이션 기준

**메일 문의가 필요한 경우:**
1. Response timeout을 충분히 증가시켰음에도 (30000ms 이상) 지속 실패
2. 다른 memory address에서도 동일 증상 발생

**메일 문의 시 필수 정보:**
- [ ] CVD 버전
- [ ] Firmware 버전  
- [ ] Target mode (sysup / attach / prepare)
- [ ] 시도한 timeout 값들
- [ ] 실패한 memory address 범위
- [ ] Target clock 정확한 값

## 📊 이슈 메타데이터

- **Issue ID:** JTAG-RISCV-004
- **최초 발견일:** 2026-02-09
- **해결 성공률:** 100% (1/1)
- **평균 해결 시간:** 5분 이내
- **재발 가능성:** 낮음 (timeout 설정 유지 시)
- **심각도:** 중 (workaround 존재)

## 🔗 관련 문서

- CVD Script Reference Manual: DEBUG.ResponseTimeOut 명령어
- JTAG-RISCV-002.md: JTAG clock 설정 관련
