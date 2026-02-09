---
date: 2026-02-03
status: pending  # solved 또는 pending
category: JTAG
priority: high  # high/medium/low
urgency: high   # 아이젠하워용
importance: high  # 아이젠하워용
tags: [Linux, fu740, module, RTOS, symbol]
reviewed: []  # 복습 이력 [2026-02-04, 2026-02-07, ...]
next_review: 2026-02-04  # 다음 복습 날짜
review_count: 0
---
### 2026-02-03 | SiFive FU740 모듈 디버깅 시 CVD HLL 미표시 (심볼/디버그 정보 누락)

#### **1줄 요약**  
sifive fu-740 termianl 에서 `insmod`로 로드된 커널 모듈에 대해 CVD가 어셈블리 코드는 표시하나 HLL(C 소스) 및 심볼 정보를 보여주지 않음 — 디버그 정보 연동 메커니즘 조사 필요.

#### **문제**  
- SiFive FU740에서 `insmod`로 커널 모듈(`.ko`) 로드 후 CVD로 디버깅  
- CVD가 해당 모듈의 실행 영역 메모리 주소를 인식하고 **어셈블리 코드는 정상 표시**  
- 그러나 **HLL**(C 소스 라인, 변수명, 함수명 등) → 디버그 편의성 크게 저하 

#### **원인 (추정)**  
- 커널 모듈은 런타임에 동적으로 메모리에 로드되며, 그 디버그 정보(DWARF 등)는 `.ko` 파일 내에 포함됨  
- CVD가 모듈 로드 후 **새로운 ELF/DWARF 섹션을 자동으로 탐지·연동하지 못함**  
- 또는 Linux 커널이 모듈의 debug section을 메모리에 유지하지 않아 디버거 접근 불가 가능성 있음  

> 💡 **코멘트**: 이전에는 “raw address만 나온다”고 착각했으나, 정확히는 **어셈블리는 나옴 → 즉, 코드 위치는 파악됨**.  
> 문제는 **HLL ↔ 어셈블리 간 매핑 정보**(debug symbol + line table)가 CVD에 전달되지 않는 것.

#### **해결 (진행 중)**  
- [ ] `.ko` 파일에 DWARF debug info 포함 여부 확인 (`readelf -wi module.ko`)  
- [ ] Linux 커널이 모듈 로드 시 debug section을 메모리에 유지하는지 조사 (`CONFIG_KALLSYMS_ALL`, `VMLINUX_SYMBOLS`)  
- [ ] CVD가 runtime-loaded module의 symbol/debug info를 수동/자동으로 추가할 수 있는지 확인  
- [ ] GDB와 비교: GDB는 `add-symbol-file -s .text <addr>`로 수동 연동 가능 → CVD 유사 기능 존재 여부 확인  

#### **왜 이렇게 했나**  
HLL 없이 어셈블리만 보면 논리 추적이 매우 어렵고, 특히 커널 모듈은 최적화 수준이 높아서 C 코드와 어셈블리 간 대응이 비직관적임.  
디버그 효율성을 위해 반드시 HLL 복원이 필요함.

#### **태그**  
#CodeViser #CVD #SiFive #FU740 #RISC-V #kernel-module #HLL #debug-info #DWARF #pending