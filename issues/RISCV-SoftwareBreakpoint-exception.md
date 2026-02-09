## title: SW Breakpoint 설정 시 다른 Cluster 코어들이 예외 발생
category: RISC-V Debug
tags: [breakpoint, sw-breakpoint, cross-cluster, i-cache, exception, multi-cluster]
chipsets: [RISC-V multi-core (custom), FPGA validation environment]
severity: medium
cvd_version: 5.0+
customer: NXP (FPGA validation)
status: unresolved
last_updated: 2025-01-29
related_issues: [JTAG-RISCV-001]

### 📄 JTAG-RISCV-002: SW Breakpoint 설정 시 다른 Cluster 코어들이 예외 발생

## 증상

- **시나리오**:
    1. `jtag_sel 0`으로 Cluster 0 선택
    2. Cluster 0에 SW breakpoint 설정 후 `run`
    3. Breakpoint hit → Cluster 0의 **모든 코어** halted (정상 동작)
    4. **예상치 못한 현상**: Cluster 1의 코어들도 exception 발생하며 멈춤
- **Serial Terminal 로그**:
    - Cluster 1 코어들이 exception 발생
    - Exception이 발생한 address = Cluster 0에 설정한 breakpoint address
- **CVD 관점**:
    - `jtag_sel 0` 상태이므로 CVD는 Cluster 1의 존재를 모름
    - Cluster 1의 exception은 CVD에서 확인/제어 불가

## 환경 조건

- **SoC 구조**:
    - FPGA 기반 검증 환경 (JTAG-RISCV-001과 동일)
    - Multi-cluster: ARM Cluster + RISC-V Cluster 0 + RISC-V Cluster 1
- **재현 조건**:
    - ✅ SW breakpoint (ebreak 명령어 삽입) 사용 시 재현됨
    - ❌ HW breakpoint (trigger register) 사용 시 재현 여부 **미확인** (고객 응답 없음)
    - ✅ Cluster 0의 **모든 코어를 CVD에 assign**했을 때 발생
    - ❌ Cluster 0의 **일부 코어만 assign**했을 때는 재현 안 됨
- **디버거**: CVD-RISC-V 5.0+
- **Breakpoint 타입**: SW breakpoint (메모리 패치 방식)

## 진단 절차 (Troubleshooting Tree)

이 이슈는 **HW 설계 레벨**의 문제일 가능성이 높습니다. 아래 순서로 확인하세요:

### Step 1: Breakpoint 타입 변경 테스트

**목적**: SW breakpoint 특유의 문제인지 확인

**시도**:

```
# HW breakpoint로 동일 address에 breakpoint 설정
hardware_breakpoint 0x80001234
run

```

**검증**:

- Serial terminal에서 Cluster 1 코어 상태 모니터링
- Exception 발생 여부 확인

**결과 판단**:

- ✅ HW breakpoint에서 재현 안 됨 → **I-Cache 이슈 가능성 높음** (Step 2로)
- ❌ HW breakpoint에서도 재현됨 → **Cross-cluster debug event propagation** (Step 3으로)

---

### Step 2: I-Cache Invalidate 확인

**가설**: SW breakpoint = 메모리에 `ebreak` 명령어 쓰기 → Shared I-Cache에 영향

**진단**:

1. **SoC 매뉴얼 확인**:
    - I-Cache가 cluster 간 공유되는 구조인지?
    - Cache coherency protocol 존재 여부?
2. **I-Cache Invalidate 레지스터 확인**:

```
   # CVD에서 CSR 레지스터 확인
   info registers csr
   # 또는 직접 읽기
   read_register 0x??? # I-Cache control register address

```

1. **Manual cache flush 시도**:
    - SoC에 I-Cache invalidate 명령어가 있다면:

```c
     // 예시 (SoC 의존적)
     __asm__ volatile("fence.i");  // RISC-V standard instruction

```

- CVD macro로 breakpoint 전에 cache flush 실행

**Workaround (임시 해결책)**:

```
# SW breakpoint 대신 HW breakpoint 사용
hardware_breakpoint <address>

```

**결과**:

- ✅ HW breakpoint로 우회 성공 → **I-Cache 이슈 확정**
- ❌ 여전히 재현됨 → **Step 3으로**

---

### Step 3: HW 팀 에스컬레이션

**문제 가능성**: Cross-cluster debug event propagation 또는 HW 설계 버그

**수집할 정보**:

1. **재현 조건 정리**:
    - Cluster 0에 assign한 코어 개수: **전체** vs **일부**
    - SW breakpoint address: 0x????????
    - Cluster 1 exception address: 0x???????? (동일한지 확인)
2. **Serial Terminal 로그**:
    - Cluster 1 exception code
    - Exception PC (Program Counter)
    - Exception cause register 값
3. **SoC 설계 문의사항**:
    - Cross-cluster debug event 전파 메커니즘 존재 여부?
    - I-Cache 공유 구조? (L1/L2 topology)
    - Cache coherency protocol 구현 여부?
    - Debug module의 "halt all cores" 옵션이 cluster 경계를 넘나드는지?
4. **CVD 로그**:

```
   set debug on
   # 위 시나리오 재현 후 로그 수집

```

**보고 대상**: HW 설계 팀 + FPGA 검증 팀

---

## 근본 원인 분석 (Root Cause Hypothesis)

### 가설 1: Shared I-Cache + Cache Coherency 미흡 (가능성 높음)

**메커니즘**:

```
1. CVD가 Cluster 0 address 0x80001234에 SW breakpoint 설정
   → 메모리 내용: 원래 명령어 → ebreak (0x00100073)

2. Cluster 0 코어가 fetch
   → I-Cache miss → 메모리에서 ebreak 명령어 읽기 → Cache에 저장

3. Cluster 1 코어들도 동일 address 실행 중
   → **Shared I-Cache hit** → ebreak 명령어 fetch
   → Breakpoint exception 발생!

4. CVD는 jtag_sel 0 상태
   → Cluster 1의 exception은 인지하지 못함

```

**증거**:

- HW breakpoint (trigger register 사용)는 메모리를 수정하지 않음
→ 만약 HW breakpoint에서 재현 안 되면 이 가설 유력

**근본 원인**:

- Cache coherency protocol이 debug 시나리오를 고려하지 않음
- 또는 SW breakpoint 설정 시 I-Cache invalidate를 명시적으로 수행하지 않음

---

### 가설 2: Cross-cluster Debug Event Propagation (가능성 낮음)

**메커니즘**:

```
1. Cluster 0의 **모든 코어**가 halt됨 (재현 조건)
   → Debug module이 "all cores halted" 신호 발생?

2. 일부 SoC는 debug module이 cluster 경계를 넘어 신호 전파
   → Cluster 1도 영향받음

3. 하지만 Cluster 1은 breakpoint address가 아닌 곳에서 exception?
   → 이 가설로는 설명 안 됨

```

**증거 부족**:

- "일부 코어만 assign 시 재현 안 됨" → 이건 가설 1로 설명 가능
    - 일부 코어만 halt → "all cores halted" 조건 미충족

---

### 가설 3: Shared Memory Region + Concurrent Execution

**메커니즘**:

```
1. Cluster 0과 Cluster 1이 **동일한 코드 영역** 실행 중
   (예: shared ROM, shared library)

2. SW breakpoint 설정 = 해당 영역의 명령어를 ebreak으로 패치
   → 모든 cluster에 영향

3. CVD는 Cluster 0만 제어 중이므로 Cluster 1의 exception은 예상 못 함

```

**확인 방법**:

- Breakpoint 설정한 address가 shared memory 영역인지 확인
- Memory map 분석 필요

---

## 재현 패턴 분석

### ✅ 재현 조건

| 조건 | 값 |
| --- | --- |
| Breakpoint 타입 | SW breakpoint (ebreak) |
| Cluster 0 assign | **모든 코어** assign |
| Cluster 1 상태 | 동일 address 실행 중 (추정) |

### ❌ 재현 안 되는 조건

| 조건 | 값 |
| --- | --- |
| Breakpoint 타입 | HW breakpoint (미확인, 추정) |
| Cluster 0 assign | **일부 코어**만 assign |

**패턴 해석**:

- "모든 코어 assign" → Cache flush 범위와 관련?
- 또는 "all cores halted" 신호 발생 조건?

---

## 해결 방법 (Workaround)

### 임시 해결책

```
# Option 1: HW breakpoint 사용
hardware_breakpoint <address>
run

# Option 2: Cluster 1도 명시적으로 제어
jtag_sel 1
halt  # 먼저 멈춰놓기
jtag_sel 0
software_breakpoint <address>
run

```

### 근본 해결 (HW 수정 필요)

1. **I-Cache invalidate 자동화**:
    - CVD가 SW breakpoint 설정 시 자동으로 I-Cache flush
    - 또는 사용자에게 명시적 cache flush 가이드
2. **Cross-cluster debug isolation**:
    - Debug event가 cluster 경계를 넘지 않도록 HW 설계 수정
    - 각 cluster에 독립적인 debug module 할당

---

## 관련 CVD 명령어

```
# HW breakpoint 설정
hardware_breakpoint <address>

# SW breakpoint 설정 (문제 발생 가능)
software_breakpoint <address>

# Cluster 선택
jtag_sel <cluster_num>

# Cache 관련 (SoC 의존적)
# 예시 - 실제 명령어는 SoC 매뉴얼 참고
write_register 0x??? 0x1  # I-Cache invalidate

```

---

## Known Limitations

1. **재현 불가능**:
    - 원격 지원 환경에서만 재현됨
    - 로컬 테스트 환경에서는 재현 안 됨
    - → 특정 FPGA bitstream 또는 타이밍 의존적일 가능성
2. **HW breakpoint 미확인**:
    - 고객이 HW breakpoint 테스트 결과 회신 안 함
    - → 가설 검증 불완전
3. **SoC 설계 정보 부족**:
    - I-Cache topology 미확인
    - Cross-cluster debug event 메커니즘 미확인
    - → 근본 원인 확정 불가

---

## 참고 자료

- RISC-V Debug Spec 0.13.2 - Section 4.8 (Software Breakpoints)
- RISC-V Privileged Spec - `fence.i` instruction (I-Cache invalidate)
- CVD 명령어 레퍼런스: `help breakpoint`, `help hardware_breakpoint`

---

## 이슈 히스토리

- **2025-01-29**: 초기 작성 (NXP 고객 케이스, JTAG-RISCV-001과 동시 발견)
- **Status**: 미해결 (고객 응답 없음, HW 팀 에스컬레이션 필요)
- **해결 가능성**:
    - Workaround (HW breakpoint 사용): 80%
    - 근본 해결 (HW 수정): 20% (SoC 설계 변경 필요)

---

## AI 진단 제안 (메타 정보)

**이 이슈를 AI가 판단할 때 제시할 질문**:

1. "SW breakpoint를 HW breakpoint로 바꿔보셨나요?"
2. "Cluster 0에 몇 개 코어를 assign 하셨나요? (전체 vs 일부)"
3. "Serial terminal에서 Cluster 1의 exception address를 확인 가능한가요?"
4. "SoC 매뉴얼에서 I-Cache 구조를 찾아볼 수 있나요? (shared vs private)"

**AI가 제안할 1차 조치**:
이 증상은 SW breakpoint의 부작용으로, Shared I-Cache 환경에서
다른 cluster가 영향받는 것으로 추정됩니다.

[즉시 시도 가능]
1. HW breakpoint로 변경 후 재현 여부 확인
2. Cluster 0 일부 코어만 assign 후 재현 여부 확인

[확인 필요]
- SoC 매뉴얼에서 I-Cache topology 확인
- Serial terminal 로그에서 exception cause 코드 확인

[에스컬레이션 조건]
- HW breakpoint로도 재현되면 HW 팀 지원 필요