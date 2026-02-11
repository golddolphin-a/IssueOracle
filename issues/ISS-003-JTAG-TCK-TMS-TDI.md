---
ID: ISS-003
date: 2026-02-03
status: solved  # 또는 pending
category: JTAG
priority: high  # high/medium/low
tags: [JTAG, CodeViser, TAP-controller, TCK, signal-timing]
flags: user-issue # or self-study
---

### 2026-02-03 | JTAG 초기화 시 TCK/TMS/TDI 신호 타이밍

#### **1줄 요약**  
CodeViser(JTAG 디버거) 초기화 시 TCK와 다른 신호(TMS/TDI/TDO)의 타이밍 동작 확인.

#### **문제**  
SoC 설계팀에서 CodeViser가 JTAG 초기화 시 TCK를 먼저 보내고 이후 다른 신호를 내보내는지, 아니면 동시에 신호를 변경하는지 문의함.  
특히 SoC의 TAP 컨트롤러는 초기에 TCK 2클록 동안 다른 신호가 토글되지 않아야 정상 동작함.

#### **원인**  
초기 상태 불확실성으로 인해 CodeViser는 Test Logic Reset 진입을 위해 TMS=1 상태에서 TCK를 5클록 발생시킴.  
이때 TDI는 토글되지 않으며, TMS는 고정(1), TCK만 토글됨.

> 💡 **코멘트**: 나는 TCK 2클록 동안 다른 신호들이 반드시 ‘0’이어야 한다고 착각했으나, 실제로는 ‘토글되지 않음’(즉, 기존 상태 유지 – 0이든 1이든 상관없음)이 핵심 조건임을 알게 됨.

#### **해결**  
1. CodeViser의 초기 JTAG 시퀀스 동작을 명확히 설명: TMS=1 유지 + TCK 5회 토글, TDI는 inactive (변화 없음).  
2. SoC 설계팀에 해당 동작이 TAP 컨트롤러 요구사항(2클록 동안 신호 토글 없음)과 충돌하지 않음을 확인 요청.
