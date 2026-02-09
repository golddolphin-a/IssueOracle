---
date: 2026-02-03
status: solved  # 또는 pending
category: flash 
priority: high  # high/medium/low
urgency: high   # 아이젠하워용
importance: high  # 아이젠하워용
tags: [flash, cyt4bf, traveo, dual bank, cyt]
reviewed: []  # 복습 이력 [2026-02-04, 2026-02-07, ...]
next_review: 2026-02-04  # 다음 복습 날짜
review_count: 0
---

### 2026-02-03 | CYT4BF Dual Bank Flash: Map B 선택 및 프로그래밍 방법

#### **1줄 요약**  
CYT4BF는 리셋 후 기본 Single Bank (Map A)로 부팅되며, Map B 실행 또는 프로그래밍을 위해선 **Dual Bank Enable** 및 **Bank Swap** 레지스터 설정 필요.

#### **문제**  
- CYT4BF에서 Dual Bank Mode 사용 시, **리셋 후 항상 Map A**(Single Bank 기준)  
- Map B 영역을 실행하거나 프로그래밍하려면 추가 설정이 필요하지만, 관련 레지스터 및 주소 정보가 문서에서 흩어져 있음

#### **원인**  
CYT4BF의 flash controller는 다음 두 레지스터로 bank 동작 제어:
- **FLASHC_FLASH_CTL register**: Dual Bank Mode 활성화 여부 설정  
- **FLASHC_BK_SWAP register**: 현재 active bank를 Map A ↔ Map B로 전환  

리셋 직후 이들 레지스터는 기본값(= Dual Bank 비활성, Map A 고정)으로 초기화됨.

#### **해결**  
1. **Dual Bank Mode 활성화**:  
   
   FLASHC->FLASH_CTL |= FLASHC_FLASH_CTL_DB_ENABLE_Msk; // DB_ENABLE = 1
Map B를 active bank로 선택:
FLASHC->BK_SWAP = 0x5A5A0001UL; // Key + BK_SWAP_EN=1 → Map B mapped to 0x10000000
Flash 프로그래밍 방법 선택:
✅ 방법 A (레지스터 활용):
Bank swap 후 동일 물리 주소(0x10000000～)에 프로그램 → 실제 Map B 영역에 기록
✅ 방법 B (직접 접근):
Map B 물리 주소(0x18000000～)에 직접 프로그램 → swap 불필요
💡 코멘트: 레지스터 설정 없이 Map B에 직접 쓰는 것도 가능하지만, 실행 시점에는 반드시 swap 설정이 필요함. 프로그래밍 ≠ 실행임을 유의!
참고 정보 (Traveo II CYT4BF 기준)
Dual Bank Enable 레지스터: FLASHC_FLASH_CTL[DB_ENABLE] (bit 31)
Bank Swap 레지스터: FLASHC_BK_SWAP (write-only, key=0x5A5A 필요)
공통 실행 영역 (logical): 0x10000000 – 0x101FFFFF (2MB)
Map A 물리 주소: 0x10000000 – 0x101FFFFF
Map B 물리 주소: 0x18000000 – 0x181FFFFF
📌 주의: BK_SWAP은 한 번 설정하면 전원 리셋까지 유지되며, 잘못된 값 쓰기 시 lock-up 가능성 있음 → 반드시 key 값(0x5A5A) 포함 필수.
왜 이렇게 했나
Dual Bank는 A/B 이미지 간 fail-safe 업데이트를 위해 설계됨.
런타임 중 bank 전환을 안전하게 하기 위해 register-based logical remapping 방식 채택.
태그
#CYT4BF #TraveoII #DualBank #Flash #BankSwap #FLASHC #MapB #Infineon #embedded-flash