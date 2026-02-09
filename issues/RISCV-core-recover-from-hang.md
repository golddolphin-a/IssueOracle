issue_id: JTAG-RISCV-003
title: PLIC 초기화 중 Core0 Hang - CVD Attach 시 복구됨
category: RISC-V Debug
tags: [hang, bus-starvation, plic, multi-core, clock-gating, sram-access]
chipsets: [RISC-V multi-core (custom), FPGA validation environment]
severity: critical
cvd_version: 5.0+
customer: NXP (FPGA validation)
status: unresolved
ai_solvable: false
escalation_required: hw-team
last_updated: 2025-01-29
related_issues: [JTAG-RISCV-001, JTAG-RISCV-002]

### 📄 JTAG-RISCV-003: PLIC 초기화 중 Core0 Hang - CVD Attach 시 복구됨

## 증상

- **시나리오**:
    1. System boot 또는 PLIC (Platform-Level Interrupt Controller) 초기화 진행 중
    2. Core0이 hang 됨 (serial terminal 출력 멈춤)
    3. CVD를 target에 **이미 연결된 상태**에서 `attach` 실행
    4. **Core0이 다시 동작** (hang 상태에서 복구됨)
- **유저 분석**:
    - Core1-15가 SRAM을 계속 읽는 동안 Core0이 SRAM 접근 불가 (bus starvation)
    - Core0의 Program Counter가 멈춰 있음 (instruction fetch 실패)
    - CVD attach 시 일시적으로 starvation 상황이 해소됨 (원인 불명)
- **기존 유사 사례** (과거 정보):
    - JTAG clock으로 인해 hang 상태가 해소되었다는 사례 존재
    - 구체적 메커니즘은 불명확

## 환경 조건

- **SoC 구조**:
    - FPGA 기반 검증 환경
    - Multi-core RISC-V (16 cores: Core0~15)
    - Shared SRAM (interconnect 구조 미상)
    - PLIC 포함
- **재현 조건**:
    - PLIC 초기화 중 발생 (정확한 코드 위치 미상)
    - Core1-15가 SRAM intensive 작업 수행 중
    - Core0이 SRAM 접근 시도 → 접근 실패 → hang
- **디버거**: CVD-RISC-V 5.0+
- **CVD 연결 상태**: 이미 target에 연결되어 있음 (background)

## 진단 절차 (Troubleshooting Tree)

이 이슈는 **HW 설계 레벨 (bus arbitration/clock gating)**의 문제일 가능성이 높습니다.

### Step 1: CVD의 Side-effect 최소화 테스트

**목적**: CVD attach가 아닌 다른 방법으로 복구 가능한지 확인

**시도 1 - `prepare` 명령어 사용**:

```
# attach 대신 prepare 사용
# prepare는 core에 직접 접근하지 않고 DAP debug register만 읽음
prepare

```

**검증**:

- Serial terminal에서 Core0 상태 모니터링
- Core0이 다시 동작하는지 확인

**결과 판단**:

- ✅ `prepare`로 복구됨 → CVD의 debug register 읽기가 trigger (Step 2로)
- ❌ `prepare`로 복구 안 됨 → `attach` 특유의 동작이 trigger (Step 3으로)

---

**시도 2 - Core1-15 수동 Halt**:

```
# CVD attach 없이 Core1-15를 먼저 멈춰보기
# (외부 JTAG 도구 또는 다른 방법 사용)
# Core0 동작 확인

```

**결과 판단**:

- ✅ Core1-15 halt 시 Core0 정상 동작 → **Bus starvation 확정** (Step 4로)
- ❌ 여전히 hang → Clock gating 또는 다른 원인 (Step 5로)

---

### Step 2: Debug Register 읽기 Side-effect 분석

**가설**: CVD가 특정 레지스터를 읽으면서 clock/bus 상태 변경

**CVD attach 시 자동 실행되는 동작**:

1. Core status register 읽기
2. Breakpoint register 읽기
3. Debug module 초기화

**확인 사항**:

- CVD configuration file (`.cfg`) 또는 startup macro 확인
- 특정 CSR (Control and Status Register) 읽기 시 side-effect 존재 여부

**SoC 매뉴얼 확인**:

- Debug module의 register access가 clock gating에 영향을 주는지?
- Power management register와 debug module의 관계?

---

### Step 3: JTAG Clock Activity 분석

**가설**: JTAG clock 자체가 SoC 내부 clock gating을 해제

**과거 유사 사례**:

- "JTAG clock으로 인해 hang 해소" 사례 존재
- 메커니즘: 일부 SoC는 JTAG activity를 감지하면 debug power domain 활성화

**확인 방법**:

```
# CVD에서 JTAG clock frequency 확인
info jtag

# 낮은 frequency로 변경 후 재시도
jtag_frequency 1000000  # 1MHz로 낮춤

```

**또는 외부 JTAG 도구로**:

- OpenOCD, J-Link 등으로 동일한 상황에서 JTAG clock만 활성화
- Core0 복구 여부 확인

---

### Step 4: Bus Starvation Root Cause 분석

**확정 증거**: Core1-15 halt 시 Core0 정상 동작

**수집할 정보**:

1. **SRAM Interconnect 구조**:
    - Single-port? Multi-port?
    - AXI/AHB bus matrix + arbitration policy?
    - 우선순위 설정 가능 여부?
2. **Bus Monitor 로그**:
    - Bus transaction analyzer로 다음 확인:
        - Core0의 memory request가 실제로 발행되는지?
        - Request가 arbitration에서 계속 밀리는지?
        - Core1-15의 SRAM access 패턴?
3. **SRAM Access Priority Register**:
    - SoC에 bus priority 설정 레지스터 존재 여부 확인
    - Core0에 높은 우선순위 부여 가능한지?

**Workaround 시도**:

```c
// Boot code에서 Core1-15를 WFI 상태로 유지
// Core0이 PLIC 초기화 완료한 후 Core1-15 활성화

// Core0 (main boot core)
void boot_sequence() {
    // 1. Core1-15를 WFI로 전환
    for (int i = 1; i < 16; i++) {
        send_ipi(i, IPI_SLEEP);
    }

    // 2. PLIC 초기화
    plic_init();

    // 3. Core1-15 깨우기
    for (int i = 1; i < 16; i++) {
        send_ipi(i, IPI_WAKEUP);
    }
}

```

---

### Step 5: HW 팀 에스컬레이션

**문제 가능성**: SoC integration 버그 또는 설계 제약

**수집할 정보**:

1. **재현 시나리오 정리**:
    - Core0이 hang되는 정확한 코드 위치 (PC address)
    - PLIC 초기화 중 어떤 레지스터 접근 시 hang?
    - Core1-15가 실행 중인 코드 (SRAM access 패턴)
2. **Serial Terminal 로그**:
    - Core0의 마지막 출력 메시지
    - Core1-15의 상태 (가능하다면)
3. **CVD 로그**:

```
   set debug on
   # attach 전후 로그 수집
   attach

```

1. **Bus Monitor 데이터**:
    - SRAM access request/grant 패턴
    - Arbitration delay 측정
2. **SoC 설계 문의사항**:
    - Bus arbitration policy (Round-robin? Priority-based?)
    - Core0에 guaranteed bandwidth 있는지?
    - JTAG/Debug module이 power/clock domain에 미치는 영향?
    - PLIC 초기화 시 특별한 제약사항?

**보고 대상**: HW 설계 팀 + SoC Integration 팀

---

## 근본 원인 분석 (Root Cause Hypothesis)

### 가설 1: Bus Starvation (가능성 가장 높음)

**메커니즘**:

```
1. Core1-15가 SRAM을 intensive하게 읽음 (tight loop or DMA)
   → Bus arbiter가 계속 Core1-15에 grant

2. Core0이 PLIC 초기화를 위해 SRAM 접근 시도
   → Bus request 발행
   → Arbiter가 계속 deny (또는 심각한 지연)

3. Core0의 instruction fetch pipeline stall
   → Program Counter 진행 안 됨
   → Serial terminal 출력 멈춤 (hang으로 보임)

4. CVD attach 시:
   - 옵션 A: Debug module이 특정 power domain 활성화
              → Bus arbitration policy 일시 변경?
   - 옵션 B: Core status 읽기 과정에서 core pipeline flush
              → Instruction fetch retry 성공?
   - 옵션 C: JTAG clock activity → Clock gating 해제
              → 일부 blocked path 복구?

```

**증거**:

- 유저 분석: "Core1-15 keep reading → Core0 starved"
- Core1-15 멈추면 Core0 정상 동작 (추정)

---

### 가설 2: Clock Gating + JTAG Activity

**메커니즘**:

```
1. PLIC 초기화 중 특정 clock domain이 gated됨
   → Core0의 일부 회로 동작 중단

2. CVD attach 시:
   - JTAG TAP 활성화 → Debug power domain ON
   - Debug module이 clock enable signal 발생
   → Gated clock 복구

3. Core0 다시 동작 시작

```

**과거 사례 증거**:

- HW 수석: "JTAG clock으로 인해 해소됐다는 사례 있음"

**확인 필요**:

- SoC의 clock gating policy
- Debug module과 clock controller의 관계

---

### 가설 3: Debug Register Read Side-effect

**메커니즘**:

```
1. Core0 hang 시 debug status register가 특정 상태로 고정
   (예: "halted" 비트가 실수로 set됨)

2. CVD attach 시:
   - Debug status register 읽기
   - 읽기 동작 자체가 register 상태를 clear (HW bug)
   → Core0 복구

3. 이는 SoC HW 버그에 해당

```

**확인 방법**:

- CVD가 읽는 정확한 register address 로깅
- 해당 register의 read side-effect 확인 (RTL 또는 매뉴얼)

---

## CVD의 역할 분석

### CVD `attach` 명령어의 내부 동작

```
attach

```

실행 시 CVD가 수행하는 동작:

1. **Debug module access**:
    - DMCONTROL register 읽기/쓰기
    - DMSTATUS register 읽기
2. **Core status 확인**:
    - 각 core의 halt/running 상태 polling
    - PC (Program Counter) 읽기
3. **Breakpoint register 읽기**:
    - Hardware breakpoint 설정 확인
    - Trigger module 상태 읽기
4. **Side-effect 가능성**:
    - 위 레지스터 접근 시 SoC 내부 state machine 변화?
    - Clock gating, power management 영향?

### CVD `prepare` 명령어와의 차이

```
prepare

```

- **Core에 직접 접근하지 않음**
- **DAP (Debug Access Port) debug register만 읽음**
- Side-effect 최소화

**진단 활용**:

- `prepare`로 복구되면 → DAP register 읽기가 trigger
- `prepare`로 복구 안 되면 → `attach`의 core access가 trigger

---

## 해결 방법

### 임시 해결책 (Workaround)

### Option 1: Boot Sequence 수정

```c
// Core0 main boot code
void main() {
    // 1. Core1-15를 WFI 상태로 유지
    halt_secondary_cores();

    // 2. PLIC 초기화 (Core0만 동작)
    plic_init();

    // 3. Core1-15 활성화
    wakeup_secondary_cores();

    // 4. 정상 동작 시작
    // ...
}

```

### Option 2: CVD를 Boot Process에 포함

```bash
# Boot script에서 CVD attach 자동 실행
#!/bin/bash
target_boot &
sleep 2  # PLIC init 시점까지 대기
cvd -batch "attach; detach"  # Trigger만 주고 detach

```

### Option 3: Bus Priority 조정 (가능한 경우)

```c
// SoC에 bus priority register가 있다면
void init_bus_priority() {
    BUS_PRIORITY_REG = 0x00;  // Core0에 최고 우선순위
}

```

---

### 근본 해결 (HW 수정 필요)

1. **Bus Arbitration Policy 개선**:
    - Core0 (boot core)에 guaranteed bandwidth 할당
    - Starvation 방지 메커니즘 추가 (timeout 기반 우선순위 상승)
2. **Clock Gating Logic 수정**:
    - Debug module이 항상 clock enable 유지
    - PLIC 초기화 중 critical path는 clock gating 제외
3. **PLIC Design Review**:
    - 초기화 sequence가 bus starvation에 취약한지 검토
    - Timeout 메커니즘 추가 (초기화 실패 시 reset)

---

## 관련 CVD 명령어

```
# attach (core에 직접 접근)
attach

# prepare (DAP register만 읽기, side-effect 최소화)
prepare

# JTAG frequency 조정
jtag_frequency <Hz>

# Debug log 활성화
set debug on

# Core status 확인
info cores

```

---

## Known Limitations

1. **재현 조건 불명확**:
    - 정확히 어떤 코드 실행 시 발생하는지 미상
    - Bus starvation 조건이 확정적인지 확률적인지 불명
2. **CVD의 복구 메커니즘 불명**:
    - JTAG clock? Register read? Debug module activation?
    - 여러 가설 존재하나 확정 불가
3. **유저 분석 진행 중**:
    - "Simulation environment 구축 중"
    - 결과 공유 없음 → Root cause 미확정
4. **SoC 설계 정보 부족**:
    - Bus interconnect topology 미상
    - Clock gating policy 미상
    - Debug module과 power management 관계 미상

---

## 참고 자료

- RISC-V PLIC Specification
- RISC-V Debug Spec 0.13.2 - Debug Module 동작
- AMBA AXI/AHB Protocol - Bus Arbitration
- CVD 명령어 레퍼런스: `help attach`, `help prepare`

---

## 이슈 히스토리

- **2025-01-29**: 초기 작성 (NXP 고객 케이스)
- **Status**: 미해결 (유저 root cause 분석 중, HW 팀 지원 필요)
- **해결 가능성**:
    - Workaround (boot sequence 수정): 70%
    - 근본 해결 (HW 설계 수정): 30%

---

## AI 진단 제안 (메타 정보)

**⚠️ 주의: 이 이슈는 AI 단독 해결 불가능**

- HW 설계 지식 필수
- Bus arbitration/clock gating은 SoC 의존적
- Root cause 확정 불가 (가설만 존재)

**AI가 제시할 질문**:

1. "`prepare` 명령어로도 복구되나요?"
2. "Core1-15를 먼저 halt 시켜보셨나요?"
3. "PLIC 초기화 중 정확히 어느 레지스터 접근 시 hang인가요?"
4. "SoC 매뉴얼에서 bus priority 설정 가능한지 확인 가능한가요?"

**AI가 제안할 1차 조치**:

```
이 증상은 multi-core 환경의 bus starvation으로 추정됩니다.
CVD attach가 복구하는 메커니즘은 불명확하며, HW 설계 레벨 분석이 필요합니다.

[즉시 시도 가능]
1. `attach` 대신 `prepare` 명령어로 복구 시도
2. Boot code 수정: Core1-15를 WFI 상태로 유지 후 PLIC 초기화

[확인 필요]
- SRAM interconnect 구조 (매뉴얼 확인)
- Bus priority 설정 레지스터 존재 여부
- Core1-15가 실행 중인 코드 패턴

[HW 팀 에스컬레이션 조건]
- Workaround로도 해결 안 되거나
- Root cause 확정 필요 시

```

---

## 추가 진단 체크리스트

엔지니어가 이 이슈 대응 시 확인할 사항:
[ ] Serial terminal에서 Core0의 마지막 출력 메시지 확인
[ ] Core0의 PC (Program Counter) 읽기 - 같은 주소에 머물러 있는지?
[ ] `prepare` 명령어로 복구 시도
[ ] `attach` 명령어로 복구 확인
[ ] Core1-15 수동 halt 후 Core0 동작 테스트 (가능하다면)
[ ] CVD debug log 활성화 (`set debug on`)
[ ] SoC 매뉴얼에서 다음 검색:
    - "bus arbitration"
    - "bus priority"
    - "clock gating"
    - "debug module clock"
[ ] PLIC 초기화 코드에서 접근하는 레지스터 주소 목록 작성
[ ] Bus monitor 도구로 SRAM access 패턴 분석 (가능하다면)
[ ] HW 팀에 다음 문의:
    - Bus starvation 방지 메커니즘 존재 여부
    - Debug module의 clock/power domain 구조
    - JTAG activity가 SoC 내부에 미치는 영향