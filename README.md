# IssueLibrary 
##Phase 1: 개인 검색용 (지금 ~ 30개)
##Phase 2: 답변 퀄리티 검증 (30~100개)
### 해야 할 작업:
Self-test: 본인이 과거 이슈 보고 3초 안에 답 찾아지는지
패턴 발견: 자주 검색하는 키워드 top 10
GPT 연동 테스트:
MD를 context로 넣고 답변 생성
답변 정확도 체크
##Phase 3: User Open (100개+)
전환 시점 신호:
동료가 "이거 어떻게 해?" 물을 때 DB 보고 3초 내 답변
GPT 답변 정확도 80% 이상
User Open 시 필요:
Web UI (간단한 검색 인터페이스)
권한 관리 (회사 기밀 vs 공개 가능)


### 실전 대응력 3대 축
1. **CVD 내부 동작 완전 정복**
   - sysup/prepare/attach/sysdown flow 문서화
   - USB capture log 분석 능력 확보

2. **반복 이슈 패턴 DB화** (IssueOracle Project)
   - MD 파일 기반 Knowledge Base 구축
   - 증상-원인-해결-학습 통합 문서

3. **Architecture별 차이점 체계화**
   - ARM/RISC-V/TriCore CVD 설정 차이 정리
