---
created: 2026-02-11
last_reviewed: null
review_count: 0
next_review: null
tags: [CVD, timeout, DAP, JTAG, memory-dump, ARM-debug]
---

# CVD Emulator Response Timeout Mechanism

## 핵심: Timeout이 발생하는 이유

**Emulator response timeout = OK/FAULT ACK 응답을 기다리는 시간 초과**

- Target이 debugger 요청한 task에 대해 3bit ACK 응답
  - `OK (0b010)`: 준비 완료
  - `FAULT (0b001)`: 에러
  - `WAIT (0b001)`: 아직 준비 안됨
  
- **WAIT ACK 받으면**: Debugger는 계속 polling하며 OK/FAULT 대기
- **일정 시간 후에도 WAIT 지속**: Response timeout → CVD sysdown

---

## Large Memory Dump 시 통신 흐름

### 1. AP 선택 (DPACC)
- IR을 통해 DPACC/APACC 선택
- DPACC에서 어느 AP 사용할지 결정 (memory access → Memory AP)

### 2. Memory Access 설정 (APACC)
- **TAR register**: Access할 address 설정
- **CSW register**: Auto increment mode 활성화 (large memory용)
  - Address 자동 update로 연속 읽기 가능

### 3. Data 읽기 루프
```
DRW/DB0-3로 데이터 요청
  ↓
ACK 확인
  ↓
WAIT? → 다시 확인 (polling)
  ↓
OK? → 다음 address 읽기
  ↓
반복...
```

---

## Timeout 발생 조건

**WAIT 상태가 지속되는 경우:**
1. **JTAG clock이 너무 낮음** → Target 응답 느림
2. **Target bus error** → Memory access 실패
3. **Target hang** → 응답 자체가 안 옴

→ CVD는 설정된 response timeout 시간까지 대기 후 sysdown

---

## 해결 방법

1. Response timeout 값 증가 (CVD Config)
2. JTAG clock 속도 조정
3. Memory dump size 줄이기 (chunk 단위)

---

## 관련 이슈
- ISS-XXX: JTAG clock 낮을 때 large memory dump timeout

## 참고
- ARM Debug Interface Architecture (ADI)
- DAP register 구조 (DPACC, APACC, TAR, CSW, DRW)