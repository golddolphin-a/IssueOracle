---
date: 2026-02-03
status: solved  # 또는 pending
category: CVD function
priority: medium  # high/medium/low
urgency: high   # 아이젠하워용
importance: high  # 아이젠하워용
tags: [CVD, CodeViser, variable-format,cvd config]
reviewed: []  # 복습 이력 [2026-02-04, 2026-02-07, ...]
next_review: 2026-02-04  # 다음 복습 날짜
review_count: 0
---

### 2026-02-03 | CVD variable format: open / recursive 옵션 기능

#### **1줄 요약**  
CVD 디버거에서 structure 변수나 call stack 표시 시 하위 레이어 확장 범위를 제어하는 `open`/`recursive` 옵션의 동작 정리.

#### **문제**  
디버그 중 복합 구조체(struct)나 중첩된 변수를 볼 때, 모든 필드가 한 번에 펼쳐지거나 너무 적게 보여 불편함 발생.  
CVD 설정 중 `open`과 `recursive` 옵션이 정확히 어떤 동작을 하는지 불명확함.

#### **원인**  
CVD는 변수 표시 형식(variable format)에서 사용자에게 구조체/클래스 등의 하위 멤버를 어느 깊이까지 자동으로 열어(확장해) 보여줄지를 제어할 수 있는 옵션 제공.  
하지만 문서화 부족으로 기능 해석에 혼선 발생.

#### **해결**  
1. **`open`**: 변수를 처음 표시할 때 **자동으로 펼칠 최대 depth** 지정 (예: `open=2` → 상위 2레벨까지 자동 확장)  
2. **`recursive`**: 해당 변수 내부에 **재귀적 구조**(예: linked list, tree node)가 있을 때 무한 확장을 방지하기 위한 **최대 반복 깊이** 제어  

> 💡 **코멘트**: 이 옵션들은 단순히 “펼치기/접기” UI와 관련된 것이 아니라, **디버거가 메모리에서 값을 읽고 표현하는 방식 자체**에 영향을 줌. 특히 대형 구조체나 재귀 구조에서 성능 및 가독성에 직접적인 영향 있음.

#### **왜 이렇게 했나**  
디버거는 기본적으로 모든 구조를 완전히 펼치면 성능 저하 및 UI 과부하 발생 가능.  
`open`/`recursive`는 사용자가 **관심 있는 범위만 효율적으로 탐색**하도록 균형을 잡기 위한 기능.

#### **태그**  
#CodeViser #CVD #debugger #variable-format #structure #recursive #call-stack #open-depth