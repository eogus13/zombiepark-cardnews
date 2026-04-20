# 핸드오프 노트: 빌더 → 데이터 분석가

**작성자**: 빌더 파트너
**날짜**: 2026-04-17
**대상**: 데이터 분석가
**상태**: 사이트 구조 및 기술 스택 확정 → GA4 추적 설정 요청

---

## 요약

빌더가 설계한 **사이트 구조 및 기술 스펙**을 데이터 분석가가 인계받습니다. 이제 **GA4 추적 코드 설치, 세그먼트 분류, 리포팅 로직**을 구축해야 합니다.

---

## 빌더가 완성한 산출물

### 1. 사이트 구조 (`mission-board/build/site-structure.md`)
- 10개 섹션 (Hero ~ Footer)
- 3가지 고객 세그먼트 (Prepper, Family, Corporate)
- 주요 CTA 버튼 5개 지점

### 2. 기술 세팅 가이드 (`mission-board/build/tech-setup-guide.md`)
- GA4 설정 가이드 (섹션 5.1)
- 이벤트 추적 스펙
- UTM 파라미터 구조

---

## 데이터 분석가의 주요 임무

### 1단계: GA4 계정 생성 및 설정

#### 1.1 GA4 프로젝트 생성

```
플랫폼: Google Analytics 4 (GA4)
계정명: ZombiePark
속성명: Zombie Park Landing (또는 Zombie Park Korea)
URL: zombiepark.kr (또는 최종 도메인)
시간대: 서울 (UTC+9)
통화: KRW (한국 원)
```

**작업 체크리스트:**
```
[ ] Google Analytics 계정 생성
[ ] GA4 속성 생성
[ ] 데이터 스트림 설정 (웹)
[ ] 측정 ID (G-XXXXXXXXXX) 획득
[ ] 추적 코드 (gtag.js) 복사
```

#### 1.2 추적 코드 설치 위치

**Framer 사용 시:**
```
Framer 프로젝트 → Settings → SEO → Custom Code
→ Head 섹션에 GA4 코드 삽입

코드:
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**아임웹 사용 시:**
```
아임웹 관리자 → 설정 → 웹 분석
→ GA4 ID 입력
(자동 연동)
```

---

### 2단계: 이벤트 추적 설정

#### 2.1 주요 추적 이벤트 정의

**이벤트 계층 구조:**

```
Page View (자동)
├─ page_view
│  └─ page_title, page_location, page_path
│
Event Tracking (커스텀)
├─ segment_view (고객층 탭 클릭)
├─ cta_click (CTA 버튼 클릭)
├─ form_start (폼 시작)
├─ form_submit (폼 제출 완료)
├─ scroll (섹션별 스크롤)
└─ video_play (비디오 재생 - 향후)
```

#### 2.2 이벤트 상세 스펙

##### 이벤트 1: Page View (자동)
```
이벤트명: page_view (자동 수집)

파라미터:
- page_title: 페이지 제목
  예: "좀비파크 | 이걸 할 줄 알면 산다"

- page_location: 전체 URL
  예: "https://zombiepark.kr/"

- page_path: 페이지 경로
  예: "/"

수집 범위: 모든 페이지 방문
```

##### 이벤트 2: Segment View
```
이벤트명: segment_view
트리거: "프레퍼" / "가족" / "기업" 탭 클릭

파라미터:
- segment_type (문자열)
  값: "prepper" | "family" | "corporate"

- action (문자열)
  값: "click"

- timestamp (숫자)
  설명: 클릭 시간 (자동)

코드 예시 (JavaScript):
function handleSegmentClick(segmentType) {
  gtag('event', 'segment_view', {
    'segment_type': segmentType,
    'action': 'click'
  });
}
```

##### 이벤트 3: CTA Click
```
이벤트명: cta_click
트리거: 모든 CTA 버튼 클릭

파라미터:
- cta_text (문자열)
  값: "사전예약하기" | "기업 문의하기" | "더 알아보기" 등

- cta_location (문자열)
  값: "hero_section" | "prepper_section" | "family_section"
      | "corporate_section" | "lifelinr_section" | "grade_section"
      | "vip_section" | "footer"

- target_segment (문자열, 선택)
  값: "prepper" | "family" | "corporate" | "all"

코드 예시:
function handleCTAClick(text, location) {
  const urlParams = new URLSearchParams(window.location.search);
  const segment = urlParams.get('utm_source') || 'direct';

  gtag('event', 'cta_click', {
    'cta_text': text,
    'cta_location': location,
    'target_segment': segment
  });
}
```

##### 이벤트 4: Form Start
```
이벤트명: form_start
트리거: 폼이 화면에 나타나거나, 사용자가 첫 입력 필드에 포커스

파라미터:
- form_type (문자열)
  값: "reservation" | "corporate_inquiry"

- form_name (문자열)
  값: "좀비파크 사전예약" | "기업 패키지 문의"

코드 예시:
window.addEventListener('load', function() {
  // 폼이 보이는 순간
  const formElement = document.querySelector('[data-form="reservation"]');
  if (formElement) {
    gtag('event', 'form_start', {
      'form_type': 'reservation',
      'form_name': '좀비파크 사전예약'
    });
  }
});
```

##### 이벤트 5: Form Submit
```
이벤트명: form_submit
트리거: 폼 제출 성공

파라미터:
- form_type (문자열)
  값: "reservation" | "corporate_inquiry"

- form_name (문자열)
  값: "좀비파크 사전예약" | "기업 패키지 문의"

- segment_selected (문자열, 예약 폼만)
  값: "prepper" | "family" | "corporate"

코드 예시:
function handleFormSubmit(event) {
  event.preventDefault();

  const formType = event.target.getAttribute('data-form-type');
  const segmentSelected = document.querySelector('[name="segment"]')?.value;

  gtag('event', 'form_submit', {
    'form_type': formType,
    'form_name': formType === 'reservation' ? '좀비파크 사전예약' : '기업 패키지 문의',
    'segment_selected': segmentSelected || 'unknown'
  });

  // 폼 제출 진행
  event.target.submit();
}
```

##### 이벤트 6: Scroll (심화 분석)
```
이벤트명: scroll (선택사항)
트리거: 특정 섹션까지 스크롤

파라미터:
- scroll_depth (문자열)
  값: "25%" | "50%" | "75%" | "100%"

- section_reached (문자열, 선택)
  값: "hero" | "prepper" | "family" | "corporate"
      | "lifeline" | "grade" | "vip" | "faq" | "footer"

용도: 사용자 관심도 분석
```

---

### 3단계: 고객 세그먼트 분류 및 커스텀 세그먼트

#### 3.1 UTM 파라미터 기반 세그먼트화

```
URL 구조:
https://zombiepark.kr?utm_source=[segment]&utm_medium=[channel]&utm_campaign=[campaign]

예시 1: 프레퍼 소셜 캠페인
https://zombiepark.kr?utm_source=prepper&utm_medium=instagram&utm_campaign=survival_tech

예시 2: 가족 커뮤니티 캠페인
https://zombiepark.kr?utm_source=family&utm_medium=community&utm_campaign=parent_education

예시 3: 기업 영업 캠페인
https://zombiepark.kr?utm_source=corporate&utm_medium=direct_sales&utm_campaign=teambuilding
```

#### 3.2 GA4 커스텀 세그먼트 생성

**세그먼트 1: Prepper Visitors**
```
조건:
- utm_source = "prepper" (또는)
- event name contains "prepper" (또는)
- segment_type = "prepper"

용도: 프레퍼층 행동 분석
```

**세그먼트 2: Family Visitors**
```
조건:
- utm_source = "family" (또는)
- event name contains "family" (또는)
- segment_type = "family"

용도: 가족층 행동 분석
```

**세그먼트 3: Corporate Visitors**
```
조건:
- utm_source = "corporate" (또는)
- event name contains "corporate" (또는)
- segment_type = "corporate"

용도: 기업층 행동 분석
```

**세그먼트 4: Form Submitters**
```
조건:
- Event: form_submit = true

용도: 전환 고객 분석
```

**세그먼트 5: High-Intent Users**
```
조건:
- Event: cta_click >= 2 (또는)
- scroll_depth >= 75% AND cta_click >= 1

용도: 고관심 고객 식별
```

---

### 4단계: 리포팅 및 대시보드 설정

#### 4.1 핵심 지표 (KPI) 정의

| 지표 | 정의 | 목표 | 측정 주기 |
|------|------|------|----------|
| **총 방문자수** | 고유 사용자 수 | 월 1,000명 | 실시간 |
| **세그먼트별 방문자수** | Prepper / Family / Corporate | 각 300, 300, 400명 | 주간 |
| **전체 전환율** | form_submit / 총 방문 | 5% 이상 | 주간 |
| **세그먼트별 전환율** | 세그먼트별 form_submit 비율 | 각 5% 이상 | 주간 |
| **평균 세션 시간** | 평균 체류 시간 | 2분 30초 이상 | 주간 |
| **이탈율** | 한 페이지만 보고 나간 비율 | 40% 이하 | 주간 |
| **CTA 클릭율** | cta_click / 방문 | 20% 이상 | 주간 |
| **모바일 전환율** | 모바일 기기 form_submit 비율 | 5% 이상 | 주간 |
| **유입 채널별 전환율** | 채널별 form_submit 비율 | 각 채널 3% 이상 | 주간 |

#### 4.2 Google Looker Studio 대시보드 구성

**대시보드 1: 전체 성과 (Executive Dashboard)**
```
구성 요소:
[ ] 총 방문자수 (카드)
[ ] 총 전환율 (카드)
[ ] 평균 세션 시간 (카드)
[ ] 이탈율 (카드)
[ ] 일일 방문자수 (시계열 차트)
[ ] 세그먼트별 방문자수 분포 (파이 차트)
[ ] 채널별 유입 (막대 차트)
[ ] 상위 랜딩 페이지 (표)

갱신: 일간
대상: 파운더, 전체 팀
```

**대시보드 2: 세그먼트 성과**
```
구성 요소:
[ ] Prepper 세그먼트
    - 방문자수
    - 전환율
    - 평균 세션 시간
    - 주요 CTA

[ ] Family 세그먼트 (동일)

[ ] Corporate 세그먼트 (동일)

[ ] 세그먼트별 비교 (테이블)

갱신: 주간
대상: 마케터
```

**대시보드 3: 기술 성과 (Performance)**
```
구성 요소:
[ ] 페이지 로드 시간 (카드)
[ ] Core Web Vitals 상태
    - LCP (Largest Contentful Paint)
    - FID (First Input Delay)
    - CLS (Cumulative Layout Shift)

[ ] 모바일 vs 데스크톱 비교
[ ] 브라우저별 이탈율
[ ] 기기별 전환율

갱신: 주간
대상: 빌더 (개발자)
```

**대시보드 4: 사용자 행동 (Behavior Flow)**
```
구성 요소:
[ ] 이벤트 흐름
    page_view → segment_view → cta_click → form_start → form_submit

[ ] 섹션별 스크롤 깊이
[ ] 가장 많이 클릭된 CTA
[ ] 폼 이탈률 (form_start vs form_submit)

갱신: 주간
대상: 마케터, 빌더
```

#### 4.3 Google Analytics Report 템플릿 (자동 이메일)

```
발송 대상: 팀 전체
발송 주기: 주간 (매주 월요일 오전 9시)
리포트 포함 항목:

---
주간 성과 리포트 (2026-04-07 ~ 04-13)

1. 핵심 수치 (한눈에 보기)
   - 방문자수: 342명 (주간)
   - 전환율: 4.8%
   - 주요 전환: 예약 폼 16건, 기업 문의 2건

2. 세그먼트 성과
   - Prepper: 142명 방문, 5.6% 전환율
   - Family: 118명 방문, 4.2% 전환율
   - Corporate: 82명 방문, 4.9% 전환율

3. 채널 성과
   - Organic (검색): 156명 (45%)
   - Direct: 98명 (29%)
   - Social: 88명 (26%)

4. 주목할 점
   - Prepper 세그먼트 전환율 상승 (전주 4.2% → 5.6%)
   - Family 채널 (Instagram) 유입 증가

5. 개선 추천사항
   - CTA 버튼 텍스트 A/B 테스트 검토
   - Family 세그먼트 특정 섹션 체류 시간 단계

---
```

---

### 5단계: 고급 분석 설정 (향후 확장)

#### 5.1 Conversion Funnel 분석

```
목표: 사용자 여정 추적

Funnel 단계:
1. Landing (page_view)
   → 모든 방문자

2. Segment Selection (segment_view)
   → 고객층을 선택한 방문자

3. CTA Engagement (cta_click)
   → CTA 클릭한 방문자

4. Form Initiation (form_start)
   → 폼에 진입한 방문자

5. Form Completion (form_submit)
   → 폼을 완료한 방문자 (전환)

측정 항목:
- 각 단계별 드롭율 (abandonment rate)
- 단계별 병목 지점 식별
- 세그먼트별 Funnel 비교
```

#### 5.2 Cohort 분석 (향후)

```
목표: 첫 방문 시기별 사용자 행동 추적

예시:
- 4월 첫주 방문자의 재방문율
- 4월 2주차 방문자의 전환율 추이
- 세그먼트별 재방문 패턴
```

#### 5.3 A/B 테스트 설정 (향후)

```
GA4 Experiments (또는 Optimize) 활용

테스트 1: CTA 버튼 색상
- Control: 주황색 (기존)
- Variant: 빨강색 (새로운)
- 측정 지표: cta_click rate

테스트 2: 헤드라인 카피
- Control: "이걸 할 줄 알면 산다"
- Variant: "당신의 생존을 준비합니다"
- 측정 지표: form_submit rate

테스트 3: CTA 위치
- Control: Hero + 하단 (기존)
- Variant: Hero + 중간 + 하단 (새로운)
- 측정 지표: cta_click rate
```

---

### 6단계: 데이터 내보내기 및 백업

#### 6.1 BigQuery 연동 (고급)

```
목적: 장기 데이터 저장 및 고급 분석

설정:
1. Google Cloud Project 생성
2. BigQuery 활성화
3. GA4 속성과 BigQuery 연결
4. 자동 데이터 내보내기 활성화

이점:
- 무제한 데이터 저장
- SQL 쿼리로 고급 분석
- 다른 Google Cloud 서비스와 통합
```

#### 6.2 수동 보고서 내보내기

```
주간 내보내기:
- GA4 리포트 → CSV 내보내기
- 구글 드라이브에 저장
- 마케터와 공유

월간 내보내기:
- 전체 성과 리포트 생성
- 파워포인트 또는 PDF로 정리
- 팀 회의 자료로 활용
```

---

## 데이터 분석가의 역할

### 주요 책임

```
[ ] GA4 계정 생성 및 추적 코드 설치
[ ] 이벤트 추적 설정 (6개 이벤트)
[ ] 세그먼트 분류 및 커스텀 세그먼트 생성
[ ] Looker Studio 대시보드 4개 구축
[ ] 자동 리포트 설정 (주간 이메일)
[ ] KPI 정의 및 목표 설정
[ ] A/B 테스트 계획 수립 (향후)
[ ] 데이터 품질 모니터링
```

### 마케터/빌더와의 협업

```
마케터에게 제공:
- 세그먼트별 성과 리포트
- 채널별 유입 및 전환 분석
- CTA 성과 분석
- 개선 추천사항

빌더에게 제공:
- 기술 성능 분석 (페이지 속도, 이탈율)
- 모바일 vs PC 성능 비교
- 오류 및 버그 리포트
```

---

## 타이밍 및 데이터 준비

### 런칭 전 준비 (2026-05-15 전)

```
[ ] GA4 계정 생성 (1주)
[ ] 추적 코드 설치 (3~5일)
[ ] 이벤트 추적 구현 (1주)
[ ] 세그먼트 설정 (2~3일)
[ ] Looker Studio 대시보드 구축 (1주)
[ ] 자동 리포트 설정 (1~2일)
[ ] 데이터 검증 테스트 (2~3일)
```

### 런칭 후 모니터링 (2026-05-15 이후)

```
첫 1주 (일간 확인)
- 추적 코드 정상 작동 확인
- 이벤트 데이터 수집 여부
- 오류 메시지 모니터링

첫 1개월 (주간 확인)
- 세그먼트별 성과 분석
- 채널별 유입 분석
- 전환율 추세 파악

지속적 (월간 확인)
- 장기 트렌드 분석
- 개선 영역 식별
- A/B 테스트 준비
```

---

## 도움말 및 리소스

### GA4 학습 자료

```
공식 문서:
- Google Analytics 도움말: support.google.com/analytics
- GA4 설정 가이드: support.google.com/analytics/answer/10089681

YouTube 튜토리얼:
- "GA4 완벽 설정 가이드"
- "GA4 이벤트 추적 자세히"
- "Looker Studio 대시보드 만들기"

커뮤니티:
- Google Analytics Community: analytics.google.com/analytics/community
- Measure Slack Community
```

### 자주 묻는 질문

```
Q: GA4 데이터가 보이지 않습니다.
A: 추적 코드 설치 후 24시간 후 데이터가 나타납니다. 실시간 리포트를 확인하세요.

Q: 기존 Google Analytics (UA)와의 차이점은?
A: GA4는 이벤트 기반이며 더 유연합니다. UA 대신 GA4로 전환해야 합니다.

Q: 세그먼트를 잘못 설정했습니다.
A: GA4 → 데이터 → 세그먼트 → 수정 가능합니다. (기존 데이터는 영향 없음)

Q: 모든 방문자의 개인정보를 추적할 수 있습니까?
A: 아니요. 개인정보(이름, 이메일 등)는 명시적 동의 후 추적해야 합니다.
```

---

## 데이터 분석가 체크리스트

```
[ ] GA4 계정 및 속성 생성
[ ] 추적 코드 복사 (G-XXXXXXXXXX)
[ ] Framer/아임웹에 추적 코드 설치
[ ] 6개 이벤트 정의 및 구현
[ ] 3개 세그먼트 생성 (Prepper, Family, Corporate)
[ ] 5개 커스텀 세그먼트 생성
[ ] 4개 Looker Studio 대시보드 구축
[ ] KPI 및 목표 설정
[ ] 자동 주간 리포트 설정
[ ] 데이터 검증 테스트 완료
[ ] 팀 교육 실시 (대시보드 사용법)
[ ] Slack 또는 Google Chat 알림 설정
[ ] 데이터 백업 계획 수립
```

---

## 다음 단계

런칭 후:
1. **주간 리포트**: 세그먼트별 성과 분석
2. **월간 회의**: 전체 성과 검토 및 개선안 논의
3. **분기 분석**: 장기 트렌드 및 A/B 테스트 계획
4. **반기 리뷰**: KPI 달성도 검토 및 목표 조정

---

## 최종 체크포인트

```
마케터와 조율:
- [ ] 마케팅 채널 및 UTM 파라미터 확정
- [ ] SNS 계정 정보 (Instagram, YouTube 등)
- [ ] 이메일 자동 응답 설정

빌더와 조율:
- [ ] 최종 도메인 URL 확정
- [ ] 추적 코드 설치 완료 확인
- [ ] 모든 CTA 버튼의 이벤트 트리거 테스트

파운더와 조율:
- [ ] KPI 목표 검토 및 승인
- [ ] 리포팅 빈도 및 방식 확인
- [ ] 데이터 기반 의사결정 프로세스 수립
```

