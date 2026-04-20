# 핸드오프 노트: 마케터 → 데이터 분석가

**작성자**: 마케터
**날짜**: 2026-04-17
**대상**: 데이터 분석가
**상태**: 마케팅 카피, 콘텐츠 캘린더, UTM 전략 완료 → 데이터 추적 설정 요청

---

## 📋 요약

마케터가 완성한 3개 산출물을 인계받습니다:

1. **카피 시트** (`mission-board/marketing/copy-variants.md`)
   - 3가지 고객 세그먼트별 A/B 카피 (헤드라인, CTA 등)
   - 각 채널/캠페인별 메시지 톤 정의

2. **콘텐츠 캘린더** (`mission-board/marketing/content-calendar.md`)
   - 4주간 SNS 계획 (인스타, 유튜브, 페이스북, 이메일)
   - 채널별 포스팅 시간, 형식, 메시지

3. **UTM 관리 시트** (`mission-board/marketing/utm-sheet.md`)
   - 모든 마케팅 채널의 링크에 붙일 UTM 파라미터
   - 캠페인 구조 및 추적 방식 정의

---

## 🎯 데이터 분석가가 해야 할 일

### 1단계: GA4 기본 설정

#### 1-1. GA4 속성 생성
```
[ ] 구글 애널리틱스 4 계정 생성
[ ] 좀비파크 웹사이트 속성 생성
[ ] 측정 ID (G-XXXXXXXX) 획득
[ ] Google Tag Manager (GTM) 컨테이너 생성 (선택)
```

#### 1-2. 추적 코드 설치
```
[ ] GA4 추적 코드를 웹사이트에 설치
    - 모든 페이지에 글로벌 추적 (head 또는 GTM 통해)
    - 확인: 실시간 리포트에서 트래픽 보임?

[ ] 이벤트 추적 설정:
    - Page View (자동 수집)
    - Scroll Depth (스크롤 깊이)
    - Click Events (CTA 버튼 클릭)
    - Form Submit (예약 폼 제출)
    - Video Engagement (유튜브 임베드 영상)
```

---

### 2단계: UTM 파라미터 추적 설정

#### 2-1. 파라미터 매핑
```
[ ] UTM 매개변수 확인
    - utm_source (출처: instagram, youtube, google 등)
    - utm_medium (매체: social_organic, paid_social, cpc 등)
    - utm_campaign (캠페인: zombiepark_launch, zombiepark_prepper 등)
    - utm_content (콘텐츠: hero_video, lifeline_infographic 등)
    - utm_term (검색어: 유료 검색만 사용)

[ ] GA4에서 자동 인식 확인
    - Reports → Acquisition → Traffic source 확인
    - 모든 UTM 파라미터가 정확히 분류되었는지 확인
```

#### 2-2. 사용자 정의 정의
```
[ ] Dimensions 추가 (선택):
    - utm_source
    - utm_medium
    - utm_campaign
    - utm_content
    - utm_term

[ ] Metrics 추가 (선택):
    - Conversions by UTM (각 캠페인별 전환수)
```

---

### 3단계: 고객 세그먼트 분류 로직 설정

#### 3-1. Audience 정의 (Segment)

```
Segment 1: Prepper 고객층
├─ utm_source IN (instagram, youtube, community)
├─ utm_content LIKE (prepper, survival, forum)
├─ 또는 방문 페이지에 "prepper" 섹션 도달

Segment 2: Family 고객층
├─ utm_source IN (facebook, instagram, email)
├─ utm_campaign = zombiepark_family
├─ 또는 방문 페이지에 "family" 섹션 도달
├─ 또는 참조 사이트 CONTAINS (parent, parent_community)

Segment 3: Corporate 고객층
├─ utm_source IN (linkedin, email, partner)
├─ utm_campaign = zombiepark_corporate
├─ 또는 방문 페이지에 "corporate" 섹션 도달
├─ 또는 참조 사이트 CONTAINS (hr, corporate)

Segment 4: New vs Returning
├─ 신규: First-time users
├─ 재방문: Returning users (보여주기: 등급 올리러 오는 고객)

Segment 5: High-Intent (예약 고객)
├─ 예약 폼 완성
├─ 결제 완료
```

#### 3-2. Audience 설정 방법
```
[ ] GA4에서 Audiences 탭 이동
[ ] 각 세그먼트 조건 입력
[ ] 조건 조합 (AND/OR) 적용
[ ] 예상 크기 확인 (너무 작거나 크지 않은지)
[ ] 저장 및 활성화
```

---

### 4단계: 전환 목표(Goals) 설정

#### 4-1. 주요 전환 목표

```
Goal 1: Newsletter 구독
├─ 트리거: 이메일 폼 제출
├─ 값: 3,000원 (CPA 목표)
├─ 추적: Form Submit 이벤트

Goal 2: 예약 신청 (첫 예약)
├─ 트리거: 예약 폼 제출 → 결제 완료
├─ 값: 50,000원 (평균 당일 패키지 가격)
├─ 추적: Purchase 이벤트

Goal 3: VIP 문의
├─ 트리거: "VIP 멤버십 문의" CTA 클릭 또는 연락처 폼 제출
├─ 값: 100,000원 (예상 VIP 상담 가치)
├─ 추적: Contact 이벤트

Goal 4: 페이지 도달 (각 세그먼트)
├─ Prepper 섹션 도달
├─ Family 섹션 도달
├─ Corporate 섹션 도달
├─ 값: 없음 (행동 지표)
```

#### 4-2. 전환 이벤트 설정
```
[ ] GA4에서 Events 탭 이동
[ ] 다음 이벤트 설정:

이벤트 1: form_submit (예약 폼)
├─ 조건: Click on #book_now_button
├─ 또는 폼 완성 감지
└─ 매개변수: form_type = "booking"

이벤트 2: purchase
├─ 조건: 결제 완료
├─ 매개변수: transaction_id, value, currency

이벤트 3: contact_inquiry (VIP 문의)
├─ 조건: Click on #vip_inquiry_button
└─ 매개변수: inquiry_type = "vip"

이벤트 4: scroll_depth
├─ 조건: 페이지의 특정 위치 (25%, 50%, 75%, 90%) 스크롤
└─ 매개변수: percent_scrolled

이벤트 5: segment_reach
├─ 조건: 특정 섹션 도달
└─ 매개변수: segment = "prepper" | "family" | "corporate"
```

---

### 5단계: 리포트 및 대시보드 설정

#### 5-1. 핵심 리포트 템플릿

```
[ ] Daily Report (매일 오전 10시 자동 생성)
    내용:
    ├─ 어제 트래픽 (방문수, 세션, 사용자)
    ├─ 예약 신청 (전일 대비)
    ├─ 상위 5개 트래픽 소스
    ├─ 상위 5개 콘텐츠
    └─ 주요 이벤트 (폼 제출, 결제 등)

[ ] Weekly Report (매주 월요일 오전 10시)
    내용:
    ├─ 주간 총 방문수 및 세그먼트별 분포
    ├─ 캠페인별 성과 (CPA, 예약 수, ROI)
    ├─ 세그먼트별 행동 분석
    │  ├─ Prepper: 평균 머물이 시간, 콘텐츠 선호도
    │  ├─ Family: 스크롤 깊이, 이탈률
    │  └─ Corporate: VIP 문의율
    ├─ 콘텐츠 성과 (SNS별 클릭, 전환)
    ├─ 기술 지표 (로드 타임, 이탈률)
    └─ 최적화 기회 (낮은 성과 채널)

[ ] Monthly Report (매월 1일)
    내용:
    ├─ 월간 종합 성과
    ├─ KPI 대비 실적 (방문, 예약, 수익)
    ├─ 캠페인별 ROI
    ├─ 장기 트렌드 분석
    └─ 다음 달 권장 사항
```

#### 5-2. 대시보드 구성
```
[ ] Main Dashboard
    ├─ 실시간 트래픽 (큰 숫자로 표시)
    ├─ 예약 신청 현황 (카운터)
    ├─ 상위 5개 트래픽 소스 (막대 그래프)
    ├─ 세그먼트별 분포 (원형 차트)
    └─ 캠페인별 CPA 추이 (꺾은선 그래프)

[ ] Campaign Performance Dashboard
    ├─ 각 캠페인별 메트릭스
    ├─ utm_campaign별 비교
    ├─ 목표 대비 실적
    └─ 추천 최적화 항목

[ ] Segment Analytics Dashboard
    ├─ Prepper 고객층 분석
    ├─ Family 고객층 분석
    ├─ Corporate 고객층 분석
    └─ 각 세그먼트별 페이지 행동 흐름

[ ] Conversion Funnel Dashboard
    ├─ Landing → Browse → Signup → Payment
    ├─ 각 단계별 이탈 분석
    └─ 세그먼트별 이탈 비교
```

---

### 6단계: A/B 테스트 설정

#### 6-1. 테스트 목표

```
Test 1: 헤드라인 A/B 테스트
├─ A 버전: "이걸 할 줄 알면 산다"
├─ B 버전: "유튜브로는 배울 수 없는 것들을 직접 해본다"
├─ 메트릭: 클릭율, 예약 전환율
├─ 샘플: 트래픽의 50% 각각

Test 2: CTA 버튼 텍스트 테스트
├─ A: "지금 예약하기"
├─ B: "첫 도전 신청하기"
├─ 메트릭: 클릭율, 폼 완성율

Test 3: 세그먼트별 메시지 테스트
├─ Prepper: "생존 기술 배우러 가기" vs "등급 올리기 시작"
├─ Family: "가족 패키지 예약" vs "아이와 함께 배우기"
├─ Corporate: "팀빌딩 제안받기" vs "기업 프로그램 상담"
```

#### 6-2. 테스트 구성
```
[ ] Google Optimize 또는 GA4 A/B Testing
[ ] 각 테스트별:
    ├─ 변형 요소 정의
    ├─ 트래픽 배분 (보통 50:50)
    ├─ 테스트 기간 (최소 2주, 통계적 유의성 확보)
    ├─ 성공 메트릭 정의
    └─ 예상 효과 크기 계산
```

---

### 7단계: 보고 및 최적화 프로세스

#### 7-1. 주간 리뷰 회의
```
매주 월요일 10:00 ~ 11:00 (팀 전체)

참석:
- 데이터 분석가 (리포트 발표)
- 마케터 (캠페인 설명 및 개선 논의)
- 빌더 (페이지 최적화 항목 검토)
- 파운더 (의사결정)

내용:
1. 전주 성과 발표 (5분)
2. 세그먼트별 인사이트 공유 (10분)
3. 낮은 성과 항목 분석 (10분)
4. 추천 최적화 사항 논의 (15분)
5. 다음주 우선순위 결정 (5분)
```

#### 7-2. 최적화 우선순위

```
Priority 1 (즉시):
├─ CPA가 목표보다 30% 이상 높은 캠페인
├─ 예약 전환율이 1% 미만인 채널
└─ 로드 타임이 3초 이상인 페이지

Priority 2 (1주일 내):
├─ 특정 세그먼트의 이탈율이 높은 페이지
├─ 클릭율이 목표보다 낮은 콘텐츠
└─ A/B 테스트 결과 유의미한 차이 발생

Priority 3 (2주일 내):
├─ 미세한 성과 개선 기회
├─ UX 최적화
└─ 장기 트렌드 분석
```

---

## 📊 데이터 분석가가 마케터에게 제공할 정보

### 주간 인사이트 (매주)
```
1. "세그먼트별 성과 스냅샷"
   ├─ Prepper: 몇 명? CPA는? 주요 채널은?
   ├─ Family: 몇 명? 클릭율은? 가장 효과적인 시간대?
   └─ Corporate: 몇 건 문의? 리드 퀄리티는?

2. "콘텐츠 성과 분석"
   ├─ 최고 성과 콘텐츠 (인스타 포스팅, 유튜브 영상)
   ├─ 최저 성과 콘텐츠
   └─ 개선 권장사항

3. "채널별 효율성"
   ├─ 각 채널의 CPA, CTR, 전환율
   ├─ ROI 분석
   └─ 예산 배분 권장사항

4. "트렌드 및 기회"
   ├─ 급상승 트래픽 소스 (왜?)
   ├─ 갑작스러운 이탈 증가 (무엇 때문?)
   └─ 다음주 주의사항
```

### 월간 종합 리포트 (매월)
```
1. KPI 성과
   ├─ 목표 대비 달성도 (%)
   ├─ MoM 성장률
   └─ 세그먼트별 LTV

2. 캠페인 성과표
   ├─ 모든 캠페인의 CPA, ROI
   ├─ 가장 효율적인 캠페인
   └─ 중단 권장 캠페인

3. 예측 및 추천
   ├─ 다음달 예상 성과
   ├─ 예산 배분 최적화
   └─ 새로운 기회 식별
```

---

## 🔗 연동 요청사항

### 마케터 ← → 데이터 분석가

```
마케터가 제공:
├─ 모든 UTM 링크 목록 (utm-sheet.md)
├─ 콘텐츠 캘린더 (content-calendar.md)
├─ SNS 채널 정보 (계정명, 링크)
└─ 광고 플랫폼 정보 (Google Ads, Facebook Ads 계정)

데이터 분석가가 제공:
├─ 주간 리포트 (매주 월요일)
├─ 월간 분석 리포트 (매월 1일)
├─ A/B 테스트 결과 (테스트 종료 시)
└─ 긴급 인사이트 (예상 밖의 성과 변화)
```

---

## 📋 체크리스트

### 론칭 전 (4월 20-30일)
```
[ ] GA4 설정 완료
[ ] 추적 코드 설치 및 테스트
[ ] UTM 파라미터 매핑 확인
[ ] 전환 목표 설정 (4개)
[ ] 이벤트 추적 설정 (5개 이상)
[ ] Audience 세그먼트 정의 (5개)
[ ] 대시보드 프로토타입 완성
[ ] A/B 테스트 설정 완료
[ ] 자동 리포트 일정 설정
[ ] 데이터 정확성 최종 검증
```

### 론칭 후 (5월)
```
[ ] 일일 실시간 모니터링
[ ] 주간 리포트 발행 (매주 월요일)
[ ] 캠페인 성과 추적
[ ] 세그먼트별 행동 분석
[ ] A/B 테스트 결과 분석
[ ] 최적화 권장사항 제시
[ ] 데이터 기반 의사결정 지원
```

---

## 다음 단계

1. **4월 20일**: 데이터 분석가와 초기 킥오프 미팅
   - 추적 목표 최종 확인
   - 기술 제약사항 논의
   - 리포트 형식 확정

2. **4월 25일**: GA4 설정 완료 및 테스트
   - 실제 트래픽 추적 시작
   - 샘플 데이터 검증

3. **4월 30일**: 런칭 준비 최종 점검
   - 모든 추적 코드 동작 확인
   - 리포트 템플릿 테스트

4. **5월 1일**: 론칭 및 실시간 모니터링 시작

---

## 파운더 확인 필요 사항

```
[ ] GA4 및 추적 도구 예산 승인 (보통 무료)
[ ] 데이터 분석 도구 선택 (GA4, Mixpanel, Amplitude 등)
[ ] 주간 리포트 검토 시간 확보 (매주 월요일 1시간)
[ ] 데이터 기반 의사결정 프로세스 확정
[ ] A/B 테스트 예산 승인 (보통 포함)
```

---

## 문의 및 지원

데이터 분석가가 이 단계에서 질문이 있으면:

**마케터에게**:
- UTM 파라미터 의미 및 캠페인 구조
- 콘텐츠 캘린더 및 타이밍
- 세그먼트 정의 및 타게팅 기준

**빌더에게**:
- 웹사이트 기술 구조
- 폼 및 결제 시스템 연동
- 페이지 요소 ID (클래스, 등) 확인

**파운더에게**:
- 비즈니스 목표 및 우선순위
- 예산 및 리소스 확보
- 정책 및 컴플라이언스 확인
