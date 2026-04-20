# GA4 세팅 가이드: 좀비파크

**작성자**: 데이터 분석 파트너
**날짜**: 2026-04-17
**상태**: Framer 기반 단계별 설정 가이드
**대상**: 빌더, 파운더

---

## 1단계: GA4 계정 생성

### 1.1 Google Analytics 4 새 계정 만들기

```
1. analytics.google.com 접속
2. 로그인 (Google 계정)
3. "새로운 Google 애널리틱스 계정 만들기" 클릭

계정 이름:
├─ ZombiePark

설정 옵션:
├─ 데이터 수집 범위: 웹
```

### 1.2 속성(Property) 생성

```
속성 이름: Zombie Park Landing
URL: https://zombiepark.kr (또는 최종 도메인)
시간대: 서울 (UTC+9)
통화: KRW (한국 원)
업종: 엔터테인먼트 → 여행 및 관광

데이터 스트림 설정:
├─ 플랫폼: 웹
├─ URL: zombiepark.kr
├─ 스트림 이름: Zombie Park Web
```

**다음: 측정 ID (G-XXXXXXXXXX) 복사하기**

---

## 2단계: Framer에 추적 코드 설치

### 2.1 추적 코드 복사

GA4 생성 후 받는 코드:
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**G-XXXXXXXXXX 부분을 본인의 측정 ID로 바꾸기**

### 2.2 Framer 설정

```
1. Framer 프로젝트 열기
2. 프로젝트 설정 → "Settings"
3. "Export" 탭 → "Custom code"
4. "Head" 섹션 클릭
5. 위의 GA4 코드 전체 붙여넣기
6. 저장

확인:
├─ 코드가 head 섹션에 잘 들어갔는가?
├─ 측정 ID (G-XXX)가 정확한가?
```

### 2.3 설치 확인

```
방법 1: Framer 실시간 미리보기
├─ 프로젝트 미리보기 → 개발자 도구 (F12)
├─ Network 탭에서 "googletagmanager" 요청 확인
└─ 성공: 200 상태 코드

방법 2: GA4 실시간 리포트
├─ GA4 → "실시간" 클릭
├─ Framer 미리보기 새로고침
└─ 1-2초 후 "활성 사용자 1명" 표시되면 성공
```

---

## 3단계: 기본 이벤트 자동 수집 확인

GA4는 다음 이벤트를 **자동으로** 수집합니다:

| 이벤트명 | 설명 | 파라미터 |
|---------|------|--------|
| **page_view** | 페이지 방문 | page_path, page_title, page_location |
| **session_start** | 세션 시작 | session_id |
| **scroll** | 페이지 스크롤 (50% 이상) | scroll_percentage |
| **click** | 외부 링크 클릭 | link_url, link_domain |
| **video_start** | 임베드 비디오 시작 | video_title, video_duration |
| **file_download** | 파일 다운로드 | file_name, file_extension |

**확인 방법:**
```
GA4 → "실시간" → "이벤트"
└─ 자동 수집 이벤트 리스트 표시됨
```

---

## 4단계: 커스텀 이벤트 설정

### 4.1 주요 추적 이벤트 6개

좀비파크의 핵심 측정 이벤트:

#### 이벤트 1: segment_view (고객층 탭 클릭)

```
이벤트명: segment_view
트리거: 프레퍼/가족/기업 탭 클릭
파라미터:
├─ segment_type: "prepper" | "family" | "corporate"
└─ action: "click"

Framer 구현 방법:
├─ 각 탭 버튼에 onClick 핸들러 추가
└─ 코드:

function handleSegmentClick(segment) {
  gtag('event', 'segment_view', {
    'segment_type': segment,
    'action': 'click'
  });
  // 섹션으로 스크롤
}
```

#### 이벤트 2: cta_click (CTA 버튼 클릭)

```
이벤트명: cta_click
트리거: 모든 CTA 버튼 클릭
파라미터:
├─ cta_text: "사전예약하기" | "기업 문의하기" | "등급 올리러 가기" 등
├─ cta_location: "hero_section" | "prepper_section" | "family_section" 등
└─ target_segment: "prepper" | "family" | "corporate" | "all"

Framer 구현:
function handleCTAClick(text, location) {
  gtag('event', 'cta_click', {
    'cta_text': text,
    'cta_location': location,
    'target_segment': 'all'
  });
}

사용 예시:
- 히어로 "사전예약하기" 클릭 → cta_location: "hero_section"
- 프레퍼 섹션 "프레퍼 스페셜 보기" → cta_location: "prepper_section"
- 푸터 "VIP 멤버십 문의" → cta_location: "footer"
```

#### 이벤트 3: form_start (폼 시작)

```
이벤트명: form_start
트리거: 폼이 화면에 보이거나 첫 입력 필드 포커스
파라미터:
├─ form_type: "reservation" | "corporate_inquiry"
└─ form_name: "좀비파크 사전예약" | "기업 패키지 문의"

Framer 구현:
document.querySelector('[data-form="reservation"]')?.addEventListener('focus', () => {
  gtag('event', 'form_start', {
    'form_type': 'reservation',
    'form_name': '좀비파크 사전예약'
  });
});
```

#### 이벤트 4: form_submit (폼 제출 완료)

```
이벤트명: form_submit
트리거: 폼 제출 성공
파라미터:
├─ form_type: "reservation" | "corporate_inquiry"
├─ form_name: "좀비파크 사전예약" | "기업 패키지 문의"
└─ segment_selected: "prepper" | "family" | "corporate" (예약 폼만)

Framer 구현:
function handleFormSubmit(event) {
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

#### 이벤트 5: scroll_depth (스크롤 깊이)

```
이벤트명: scroll_depth
트리거: 페이지의 25%, 50%, 75%, 100% 도달
파라미터:
├─ scroll_percentage: "25" | "50" | "75" | "100"
└─ page_path: 현재 페이지

Framer 구현:
const tracked = { 25: false, 50: false, 75: false, 100: false };

window.addEventListener('scroll', () => {
  const scrollPercent = Math.round((window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100);

  [25, 50, 75, 100].forEach(threshold => {
    if (scrollPercent >= threshold && !tracked[threshold]) {
      gtag('event', 'scroll_depth', {
        'scroll_percentage': threshold.toString(),
        'page_path': window.location.pathname
      });
      tracked[threshold] = true;
    }
  });
});
```

#### 이벤트 6: section_reach (섹션 도달)

```
이벤트명: section_reach
트리거: 특정 섹션까지 스크롤하여 도달
파라미터:
└─ section_name: "hero" | "prepper" | "family" | "corporate" | "lifeline" | "grade" | "vip" | "faq" | "footer"

Framer 구현:
const sections = ['prepper', 'family', 'corporate', 'lifeline', 'grade', 'vip'];
const observed = {};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !observed[entry.target.id]) {
      gtag('event', 'section_reach', {
        'section_name': entry.target.id
      });
      observed[entry.target.id] = true;
    }
  });
});

sections.forEach(section => {
  const element = document.getElementById(section);
  if (element) observer.observe(element);
});
```

### 4.2 이벤트 설정 체크리스트

```
[ ] segment_view: 고객층 탭 클릭 추적
[ ] cta_click: 모든 CTA 버튼 클릭 추적
[ ] form_start: 폼 인게이지먼트 추적
[ ] form_submit: 예약/문의 폼 제출 추적 ⭐ 핵심 전환
[ ] scroll_depth: 사용자 관심도 분석
[ ] section_reach: 세그먼트별 섹션 도달 추적
```

---

## 5단계: UTM 파라미터 자동 수집

GA4는 URL의 UTM 파라미터를 **자동으로** 수집합니다.

### 5.1 수집되는 파라미터

| 파라미터 | GA4 필드 | 예시 |
|---------|---------|------|
| utm_source | source | instagram, youtube, google |
| utm_medium | medium | social_organic, paid_social, cpc |
| utm_campaign | campaign | zombiepark_launch, zombiepark_prepper |
| utm_content | content | hero_video, lifeline_infographic |
| utm_term | term | survival_experience |

**자동 수집 확인:**
```
GA4 → "보고서" → "획득" → "트래픽 소스"
└─ source, medium, campaign 데이터 표시됨
```

### 5.2 마케터가 제공한 링크 사용

마케터의 utm-sheet.md에서 링크를 복사하여 사용:

```
예: Instagram 프레퍼층 광고
https://zombiepark.kr?utm_source=instagram&utm_medium=paid_social&utm_campaign=zombiepark_prepper&utm_content=hero_video

이 링크는 GA4에 자동으로:
├─ source: instagram
├─ medium: paid_social
├─ campaign: zombiepark_prepper
└─ content: hero_video
로 기록됨
```

---

## 6단계: 세그먼트 분류 설정

### 6.1 GA4 커스텀 세그먼트 생성

3가지 고객층을 자동으로 분류하기:

**세그먼트 1: Prepper Visitors**
```
GA4 → "데이터" → "세그먼트" → "새 세그먼트 만들기"

조건:
├─ source contains "instagram" 또는
├─ source contains "youtube" 또는
├─ source contains "community" 또는
└─ event parameter segment_type equals "prepper"

이름: Prepper Layer
```

**세그먼트 2: Family Visitors**
```
조건:
├─ source contains "facebook" 또는
├─ source contains "family" 또는
├─ event parameter campaign contains "family" 또는
└─ event parameter segment_type equals "family"

이름: Family Layer
```

**세그먼트 3: Corporate Visitors**
```
조건:
├─ source contains "linkedin" 또는
├─ source contains "corporate" 또는
├─ event parameter campaign contains "corporate" 또는
└─ event parameter segment_type equals "corporate"

이름: Corporate Layer
```

**세그먼트 4: Form Submitters (전환자)**
```
조건:
└─ event form_submit = true

이름: Form Submitters (Conversions)
```

### 6.2 세그먼트 활용

모든 리포트에서 세그먼트 필터 사용:
```
예: 프레퍼층 방문자만의 이탈율
→ "Prepper Layer" 세그먼트 선택
→ 이탈율 리포트 확인
```

---

## 7단계: 전환 목표(Goals) 설정

### 7.1 핵심 4가지 목표

**목표 1: Newsletter 구독** ⭐
```
GA4 → "데이터" → "전환" → "전환 이벤트 만들기"

이벤트 이름: newsletter_signup
조건: form_type = "newsletter"
추적 값: 3,000원 (CPA 기준)
```

**목표 2: 예약 신청** ⭐⭐ 핵심
```
이벤트 이름: form_submit
조건: form_type = "reservation"
추적 값: 50,000원 (당일 패키지 평균가)
```

**목표 3: VIP 문의** ⭐
```
이벤트 이름: corporate_inquiry
조건: form_type = "corporate_inquiry"
추적 값: 100,000원 (기업 패키지 상담가)
```

**목표 4: 페이지 도달 (고객층별)**
```
이벤트 이름: section_reach
조건:
├─ section_name = "prepper"
├─ section_name = "family"
└─ section_name = "corporate"
추적 값: 없음 (행동 지표)
```

---

## 8단계: 데이터 검증 테스트

### 8.1 테스트 체크리스트

```
[ ] GA4 실시간 리포트에서 트래픽 보이는가?
[ ] 각 CTA 버튼 클릭하면 "cta_click" 이벤트 기록되는가?
[ ] 세그먼트 탭 클릭하면 "segment_view" 이벤트 기록되는가?
[ ] 폼 시작/제출하면 "form_start", "form_submit" 이벤트 기록되는가?
[ ] 페이지 스크롤하면 "scroll_depth" 이벤트 기록되는가?
[ ] 섹션 도달하면 "section_reach" 이벤트 기록되는가?
[ ] 파라미터 값이 정확하게 기록되는가?
```

### 8.2 테스트 방법

```
1. Framer 미리보기 열기
2. 개발자 도구 (F12) 열기
3. Console 탭에서:
   window.dataLayer를 입력하여 gtag 호출 확인
4. GA4 실시간 리포트에서 이벤트 확인
```

---

## 9단계: 자동 리포트 설정

### 9.1 주간 자동 이메일 리포트

```
GA4 → "보고서" → "공유" → "이메일로 예약된 리포트"

리포트 이름: Weekly Zombie Park Report
빈도: 매주 월요일 오전 9시
수신자: 팀 이메일 주소들
포함 항목:
├─ 총 방문자수 (주간)
├─ 세그먼트별 방문자수 분포
├─ 전환율 (form_submit)
├─ 상위 5개 트래픽 소스
└─ CTA 클릭수 (상위 5개)
```

---

## 10단계: Looker Studio 대시보드 연결

### 10.1 기본 대시보드 생성

```
looker.studio (또는 datastudio.google.com) 접속
→ "새 보고서" → "GA4 속성 선택"

기본 차트:
├─ 총 방문자수 (스코어카드)
├─ 세그먼트별 분포 (원형 차트)
├─ 일일 트래픽 추이 (시계열)
├─ 상위 소스 (막대 차트)
├─ 전환율 (게이지)
└─ CTA 클릭 상위 5개 (테이블)
```

---

## 최종 체크리스트

```
[ ] GA4 계정 & 속성 생성
[ ] 측정 ID (G-XXX) 확보
[ ] Framer에 추적 코드 설치
[ ] 6개 커스텀 이벤트 구현 완료
[ ] GA4 실시간 리포트에서 데이터 확인
[ ] 4개 세그먼트 생성 및 활성화
[ ] 4개 전환 목표 설정
[ ] UTM 파라미터 자동 수집 확인
[ ] 주간 자동 리포트 설정
[ ] Looker Studio 대시보드 연결
[ ] 전체 데이터 검증 완료
```

---

## 마케터/빌더와의 조율

### 확인 사항

```
빌더에게:
- [ ] 최종 도메인 URL 확정 (zombiepark.kr)
- [ ] Framer 프로젝트 접근 권한 확보
- [ ] 모든 CTA 버튼의 정확한 텍스트 & 위치 확인
- [ ] 폼 제출 완료 페이지 또는 감사 메시지 확인

마케터에게:
- [ ] UTM 링크 최종 확정 (utm-sheet.md)
- [ ] 모든 채널의 링크 정확성 검증
- [ ] SNS 채널 계정 정보 (Instagram, YouTube, Facebook 등)
- [ ] 콘텐츠 캘린더의 링크 동기화 일정
```

---

## 문제 해결 가이드

### Q: GA4에서 데이터가 안 보여요
**A:** 추적 코드 설치 후 **24시간 소요**됩니다. 실시간 리포트("실시간" 탭)에서는 즉시 보입니다.

### Q: 커스텀 이벤트가 기록되지 않습니다
**A:**
1. 이벤트명이 정확한지 확인 (대소문자 구분)
2. gtag 함수 호출이 정상인지 확인 (Console 확인)
3. Framer에서 JavaScript 실행이 허용되는지 확인

### Q: 세그먼트가 제대로 작동하지 않습니다
**A:**
1. 조건 로직 다시 확인 (AND vs OR)
2. 파라미터 값이 정확한지 확인 (예: "prepper" vs "Prepper")
3. 세그먼트 미리보기에서 예상 크기 확인

---

## 다음 단계

1. **설정 완료 후**: 이벤트 정의서 검토 시작
2. **데이터 수집 24시간 후**: 주간 리포트 템플릿 작성
3. **런칭 1주 전**: 마케터와 UTM 링크 최종 검증
4. **런칭 당일**: 실시간 모니터링 시작
