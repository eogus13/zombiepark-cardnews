# 이벤트 정의서: 좀비파크

**작성자**: 데이터 분석 파트너
**날짜**: 2026-04-17
**목적**: 모든 추적 이벤트의 상세 정의 및 구현 스펙
**대상**: 개발자, QA, 분석가

---

## 개요

좀비파크 랜딩페이지에서 수집할 총 **7개 이벤트**를 정의합니다.
- 자동 이벤트 1개 (page_view)
- 커스텀 이벤트 6개

---

## 이벤트 계층 구조

```
사용자 방문
│
├─ page_view (자동)
│  └─ 모든 페이지 방문 시 기록
│
├─ 세그먼트 탐색
│  ├─ segment_view ⭐
│  │  └─ 고객층 탭 클릭
│  │
├─ 콘텐츠 상호작용
│  ├─ cta_click ⭐
│  │  └─ CTA 버튼 클릭
│  │
│  ├─ scroll_depth
│  │  └─ 페이지 스크롤 (25%, 50%, 75%, 100%)
│  │
│  └─ section_reach
│     └─ 특정 섹션 도달
│
└─ 전환 (Conversion)
   ├─ form_start ⭐
   │  └─ 폼 시작 (의도 신호)
   │
   └─ form_submit ⭐⭐
      └─ 폼 제출 (최종 전환)
```

---

## 상세 이벤트 정의

### 이벤트 1: page_view (자동 수집)

| 항목 | 내용 |
|------|------|
| **이벤트명** | page_view |
| **트리거** | 모든 페이지 방문 (자동) |
| **수집 범위** | 전체 사이트 모든 페이지 |
| **수집 주기** | 페이지 로드 시 1회 |
| **우선순위** | 필수 |

#### 파라미터

| 파라미터 | 타입 | 예시 | 설명 |
|---------|------|------|------|
| page_location | 문자열 | `https://zombiepark.kr/` | 전체 페이지 URL |
| page_path | 문자열 | `/` | 경로 (/about, /booking 등) |
| page_title | 문자열 | `좀비파크 \| 이걸 할 줄 알면 산다` | 페이지 제목 (HTML `<title>`) |
| referrer | 문자열 | `google.com` | 참조 소스 (자동) |
| language | 문자열 | `ko` | 사용자 언어 (자동) |

#### 사용 사례

```
1. 사용자가 zombiepark.kr 방문
   → page_view 기록 (page_path: "/")

2. 사용자가 /about 페이지 방문
   → page_view 기록 (page_path: "/about")

3. 새로고침
   → page_view 다시 기록 (세션 유지)
```

#### 검증 방법

```
GA4 실시간 리포트:
├─ "이벤트" 탭 클릭
├─ "page_view" 확인
└─ page_path 파라미터 확인
```

---

### 이벤트 2: segment_view ⭐

| 항목 | 내용 |
|------|------|
| **이벤트명** | segment_view |
| **트리거** | 고객층 탭 클릭 (프레퍼/가족/기업) |
| **수집 범위** | 메인 랜딩페이지의 3개 탭 |
| **수집 주기** | 각 탭 클릭 시 1회 |
| **목적** | 고객층별 관심도 측정 |
| **우선순위** | 핵심 |

#### 파라미터

| 파라미터 | 타입 | 필수 | 예시 | 설명 |
|---------|------|------|------|------|
| segment_type | 문자열 | 예 | prepper / family / corporate | 선택된 고객층 |
| action | 문자열 | 예 | click | 사용자 행동 |

#### 값 정의

**segment_type**
```
- "prepper": 프레퍼층 (밀리터리, 생존 애호가)
- "family": 가족층 (교육적 체험)
- "corporate": 기업층 (팀빌딩 프로그램)
```

#### 구현 예시

```javascript
function handleSegmentClick(segment) {
  gtag('event', 'segment_view', {
    'segment_type': segment,
    'action': 'click'
  });
  // 해당 섹션으로 스크롤
}

// HTML: <button onclick="handleSegmentClick('prepper')">프레퍼</button>
```

#### 분석 사용 사례

```
1. "프레퍼층이 가장 많이 클릭하는가?"
   → segment_view 필터: segment_type = "prepper" 카운트

2. "각 세그먼트 탭의 인기도 비교"
   → 세그먼트별 segment_view 이벤트 수 비교

3. "이 세그먼트 방문자의 전환율은?"
   → segment_view 이벤트 있는 사용자 중 form_submit 비율
```

---

### 이벤트 3: cta_click ⭐

| 항목 | 내용 |
|------|------|
| **이벤트명** | cta_click |
| **트리거** | 모든 CTA(Call-to-Action) 버튼 클릭 |
| **수집 범위** | 사이트 전체 CTA |
| **수집 주기** | 각 CTA 클릭 시 1회 |
| **목적** | 사용자 의도 파악 및 병목 진단 |
| **우선순위** | 핵심 |

#### 파라미터

| 파라미터 | 타입 | 필수 | 예시 | 설명 |
|---------|------|------|------|------|
| cta_text | 문자열 | 예 | "사전예약하기" | 버튼 텍스트 |
| cta_location | 문자열 | 예 | "hero_section" | CTA 위치 |
| target_segment | 문자열 | 선택 | "prepper" | 타겟 고객층 (없으면 "all") |

#### CTA 위치 맵핑

| 위치 | cta_location | 설명 |
|------|-------------|------|
| 히어로 섹션 | hero_section | 메인 화면 상단 |
| 프레퍼 섹션 | prepper_section | 프레퍼층 전용 CTA |
| 가족 섹션 | family_section | 가족층 전용 CTA |
| 기업 섹션 | corporate_section | 기업층 전용 CTA |
| 라이프라인 섹션 | lifeline_section | 4대 라이프라인 설명 후 |
| 등급 섹션 | grade_section | 등급 시스템 설명 후 |
| VIP 섹션 | vip_section | VIP 프로그램 섹션 |
| 푸터 | footer | 페이지 하단 |

#### CTA 텍스트 예시

```
- "사전예약하기"
- "지금 예약하기"
- "프레퍼 스페셜 보기"
- "가족 패키지 예약하기"
- "기업 패키지 문의하기"
- "등급 올리러 가기"
- "VIP 멤버십 문의"
- "더 알아보기"
```

#### 구현 예시

```javascript
function handleCTAClick(text, location, segment = 'all') {
  gtag('event', 'cta_click', {
    'cta_text': text,
    'cta_location': location,
    'target_segment': segment
  });
}

// 사용 예: 히어로 섹션 CTA
// <button onclick="handleCTAClick('사전예약하기', 'hero_section')">사전예약하기</button>

// 프레퍼 섹션 CTA
// <button onclick="handleCTAClick('프레퍼 스페셜 보기', 'prepper_section', 'prepper')">보기</button>
```

#### 분석 사용 사례

```
1. "어느 CTA가 가장 클릭을 많이 받는가?"
   → cta_location별 cta_click 수 비교

2. "어느 세그먼트가 특정 CTA를 가장 많이 클릭하는가?"
   → cta_location + segment_type 교차 분석

3. "CTA 클릭 후 폼까지 가는가?" (이탈 지점 진단)
   → cta_click → form_start 퍼널 분석

4. "hero_section CTA의 클릭-전환 효율"
   → hero_section CTA 클릭자 중 form_submit 비율
```

---

### 이벤트 4: form_start ⭐

| 항목 | 내용 |
|------|------|
| **이벤트명** | form_start |
| **트리거** | 폼이 화면에 표시되거나 첫 입력필드에 포커스 |
| **수집 범위** | 예약 폼, 기업 문의 폼 |
| **수집 주기** | 폼 표시/첫 포커스 시 1회 |
| **목적** | 사용자 의도 신호, 폼 시작 점 추적 |
| **우선순위** | 핵심 |

#### 파라미터

| 파라미터 | 타입 | 필수 | 예시 | 설명 |
|---------|------|------|------|------|
| form_type | 문자열 | 예 | "reservation" | 폼 유형 |
| form_name | 문자열 | 예 | "좀비파크 사전예약" | 사용자 친화적 이름 |

#### form_type 정의

```
- "reservation": 사전예약 폼 (Typeform 또는 Google Form)
- "corporate_inquiry": 기업 문의 폼 (Formspree)
- "newsletter": 뉴스레터 구독 (선택)
```

#### 구현 예시

```javascript
// 폼이 화면에 나타나거나 스크롤되어 보일 때
const reservationForm = document.querySelector('[data-form="reservation"]');
if (reservationForm) {
  reservationForm.addEventListener('focus', () => {
    gtag('event', 'form_start', {
      'form_type': 'reservation',
      'form_name': '좀비파크 사전예약'
    });
  }, true); // Capture phase 사용
}

// 또는 폼 섹션까지 스크롤했을 때
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      gtag('event', 'form_start', {
        'form_type': 'reservation',
        'form_name': '좀비파크 사전예약'
      });
      observer.unobserve(entry.target); // 1회만 추적
    }
  });
});
observer.observe(reservationForm);
```

#### 분석 사용 사례

```
1. "폼 표시까지 다다르는 방문자 비율"
   → form_start / page_view 비율

2. "폼까지는 왔지만 제출하지 않은 사용자"
   → form_start - form_submit = 포기한 사용자

3. "CTA 클릭 후 몇 %가 폼을 시작하는가?"
   → cta_click → form_start 전환율
```

---

### 이벤트 5: form_submit ⭐⭐ 핵심 전환

| 항목 | 내용 |
|------|------|
| **이벤트명** | form_submit |
| **트리거** | 폼 제출 완료 (서버 확인) |
| **수집 범위** | 예약 폼, 기업 문의 폼 |
| **수집 주기** | 폼 제출 성공 시 1회 |
| **목적** | 최종 전환 추적 (가장 중요한 지표) |
| **우선순위** | 필수 |
| **전환값** | 50,000원 (예약), 100,000원 (기업) |

#### 파라미터

| 파라미터 | 타입 | 필수 | 예시 | 설명 |
|---------|------|------|------|------|
| form_type | 문자열 | 예 | "reservation" | 폼 유형 |
| form_name | 문자열 | 예 | "좀비파크 사전예약" | 폼 이름 |
| segment_selected | 문자열 | 선택 | "prepper" | 예약 폼: 선택한 고객층 |

#### 구현 예시

```javascript
// Typeform 제출 감지
function handleFormSubmit(event) {
  event.preventDefault();

  // 폼 유형 확인
  const formType = event.target.getAttribute('data-form-type') || 'reservation';
  const formName = event.target.getAttribute('data-form-name') || '좠비파크 사전예약';

  // 선택된 세그먼트 (예약 폼만)
  const segmentSelected = document.querySelector('[name="segment"]')?.value || 'unknown';

  // GA4 이벤트 발송
  gtag('event', 'form_submit', {
    'form_type': formType,
    'form_name': formName,
    'segment_selected': segmentSelected
  });

  // 폼 제출 진행 (Typeform API 또는 Google Forms)
  event.target.submit();
}

// Typeform 임베드 시 제출 감지:
// <iframe src="https://zombiepark.typeform.com/to/xxx"
//         onload="window.addEventListener('message', (e) => {
//           if (e.data.type === 'submit') handleFormSubmit(e);
//         })"></iframe>
```

#### 분석 사용 사례

```
1. "주간 예약 수"
   → form_submit 이벤트 count (form_type = "reservation")

2. "기업 문의 수"
   → form_submit 이벤트 count (form_type = "corporate_inquiry")

3. "전체 전환율"
   → form_submit / page_view × 100%

4. "세그먼트별 전환율"
   → segment_selected별 form_submit 비율 비교

5. "채널별 전환 효율 (CPA)"
   → utm_campaign별 form_submit 수 / 광고 비용
```

---

### 이벤트 6: scroll_depth

| 항목 | 내용 |
|------|------|
| **이벤트명** | scroll_depth |
| **트리거** | 페이지 스크롤 깊이 도달 (25%, 50%, 75%, 100%) |
| **수집 범위** | 전체 페이지 |
| **수집 주기** | 각 깊이마다 1회 (중복 없음) |
| **목적** | 사용자 관심도 / 읽음 깊이 추적 |
| **우선순위** | 권장 |

#### 파라미터

| 파라미터 | 타입 | 필수 | 예시 | 설명 |
|---------|------|------|------|------|
| scroll_percentage | 문자열 | 예 | "25" / "50" / "75" / "100" | 스크롤 깊이 (%) |
| page_path | 문자열 | 예 | "/" | 해당 페이지 |

#### 구현 예시

```javascript
const trackedScrolls = { 25: false, 50: false, 75: false, 100: false };

window.addEventListener('scroll', () => {
  const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
  const scrollPercent = Math.round((window.scrollY / totalHeight) * 100);

  [25, 50, 75, 100].forEach(threshold => {
    if (scrollPercent >= threshold && !trackedScrolls[threshold]) {
      gtag('event', 'scroll_depth', {
        'scroll_percentage': threshold.toString(),
        'page_path': window.location.pathname
      });
      trackedScrolls[threshold] = true;
    }
  });
});
```

#### 분석 사용 사례

```
1. "사용자가 페이지를 끝까지 읽는가?"
   → scroll_depth "100%" 이벤트 비율

2. "어디서 가장 많이 나가는가?" (이탈 지점)
   → scroll_depth "50%"은 많지만 "75%"은 적음 → 50%~75% 콘텐츠 검토

3. "세그먼트별 관심도"
   → 프레퍼층은 깊게 스크롤, 가족층은 얕게 → 콘텐츠 위치 개선
```

---

### 이벤트 7: section_reach

| 항목 | 내용 |
|------|------|
| **이벤트명** | section_reach |
| **트리거** | 특정 섹션까지 스크롤하여 도달 |
| **수집 범위** | 6개 섹션 (프레퍼, 가족, 기업, 라이프라인, 등급, VIP) |
| **수집 주기** | 각 섹션 도달 시 1회 (중복 없음) |
| **목적** | 고객층별 섹션 관심도 추적 |
| **우선순위** | 권장 |

#### 파라미터

| 파라미터 | 타입 | 필수 | 예시 | 설명 |
|---------|------|------|------|------|
| section_name | 문자열 | 예 | "prepper" | 섹션 ID |

#### section_name 정의

```
- "hero": 히어로 섹션 (자동 수집)
- "prepper": 프레퍼층 섹션
- "family": 가족층 섹션
- "corporate": 기업층 섹션
- "lifeline": 4대 라이프라인 섹션
- "grade": 등급 시스템 섹션
- "vip": VIP 프로그램 섹션
- "faq": FAQ 섹션
- "footer": 푸터
```

#### 구현 예시

```javascript
const sections = ['prepper', 'family', 'corporate', 'lifeline', 'grade', 'vip', 'faq'];
const observedSections = {};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !observedSections[entry.target.id]) {
      gtag('event', 'section_reach', {
        'section_name': entry.target.id
      });
      observedSections[entry.target.id] = true;
    }
  });
}, { threshold: 0.3 }); // 섹션의 30% 이상 보일 때

sections.forEach(section => {
  const element = document.getElementById(section);
  if (element) observer.observe(element);
});
```

#### 분석 사용 사례

```
1. "프레퍼층이 corporate 섹션까지 가는가?"
   → prepper segment 방문자 중 section_reach "corporate" 비율

2. "VIP 섹션에 도달하는 사용자 비율"
   → section_reach "vip" / page_view

3. "이 섹션 도달 후 폼까지 가는가?"
   → section_reach → form_submit 퍼널

4. "어느 섹션이 가장 많은 트래픽을 받는가?"
   → section_reach 이벤트 count by section_name
```

---

## 이벤트 요약 테이블

| 이벤트명 | 트리거 | 주요 파라미터 | 목적 | 우선순위 |
|---------|--------|-------------|------|---------|
| page_view | 페이지 로드 | page_path, page_title | 방문 추적 | 필수 |
| segment_view | 고객층 탭 클릭 | segment_type | 고객층 관심도 | 핵심 |
| cta_click | CTA 버튼 클릭 | cta_text, cta_location | 사용자 의도 | 핵심 |
| form_start | 폼 시작 | form_type, form_name | 의도 신호 | 핵심 |
| form_submit | 폼 제출 ✓ | form_type, segment_selected | 최종 전환 | 필수 |
| scroll_depth | 스크롤 25/50/75/100% | scroll_percentage | 관심도 | 권장 |
| section_reach | 섹션 도달 | section_name | 섹션별 인기도 | 권장 |

---

## 구현 체크리스트

### 개발자용

```
[ ] 6개 커스텀 이벤트 함수 작성
[ ] 각 CTA 버튼에 cta_click 핸들러 연결
[ ] 각 segment 탭에 segment_view 핸들러 연결
[ ] form_start 트리거 구현 (폼 focus 또는 스크롤 감지)
[ ] form_submit 트리거 구현 (폼 제출 감지)
[ ] scroll_depth 리스너 구현 (throttle 권장)
[ ] section_reach IntersectionObserver 구현
[ ] 모든 파라미터 값 정확성 검증
```

### QA용

```
[ ] 각 이벤트 트리거가 정상 작동하는가?
[ ] 파라미터 값이 정의서와 일치하는가?
[ ] 중복 이벤트가 발생하지 않는가?
[ ] 모든 기기(모바일/PC)에서 정상 작동하는가?
[ ] GA4 실시간 리포트에서 이벤트 보이는가?
[ ] 유효하지 않은 파라미터가 없는가?
```

### 분석가용

```
[ ] GA4에서 모든 이벤트 확인 (24시간 후)
[ ] 파라미터 값 분포 확인
[ ] 이벤트 간 흐름 (퍼널) 검증
[ ] 세그먼트별 이벤트 패턴 분석
[ ] 이상 값(outlier) 확인
```

---

## 데이터 품질 기준

### 필수 검증

| 항목 | 기준 | 측정 방법 |
|------|------|---------|
| 이벤트 정확성 | 파라미터 값이 정의서와 100% 일치 | GA4 실시간 리포트 |
| 이벤트 완성도 | 모든 필수 파라미터 포함 | GA4 이벤트 분석 |
| 이벤트 타이밍 | 사용자 행동 직후 1초 이내 기록 | Network 탭 확인 |
| 중복 방지 | 같은 사용자의 중복 이벤트 없음 | 사용자 ID 기반 확인 |

---

## 향후 확장 (선택사항)

```
1. 비디오 추적 (video_start, video_complete)
   └─ 유튜브 임베드 영상 재생 시간 추적

2. 다운로드 추적 (file_download)
   └─ 생존 매뉴얼 PDF 다운로드 추적

3. 외부 링크 추적 (click)
   └─ 소셜 미디어 링크 클릭 추적 (기본값)

4. 결제 추적 (purchase)
   └─ 예약 결제 완료 추적 (향후 결제 시스템 연동)

5. 이메일 추적 (email_signup)
   └─ 뉴스레터 구독 (선택사항)
```

---

## 문제 해결 가이드

### Q: 이벤트가 GA4에서 안 보여요
**A:**
1. 추적 코드 설치 확인 (GA4 실시간 리포트)
2. 이벤트 발송 코드 실행 확인 (Console 확인)
3. 이벤트명 대소문자 확인 (gtag에서 소문자)
4. 24시간 대기 후 "이벤트" 탭 확인

### Q: 파라미터 값이 수집되지 않습니다
**A:**
1. 파라미터 이름 정확성 확인 (공식 네이밍 사용)
2. 파라미터 값이 null/undefined 아닌지 확인
3. 따옴표 사용 (문자열은 " " 사용)

### Q: 특정 세그먼트만 이벤트가 안 나옵니다
**A:**
1. 해당 버튼/요소가 정상 렌더링되는지 확인
2. 이벤트 핸들러가 올바르게 바인딩되었는지 확인
3. 개발자 도구에서 클릭 시 콘솔 메시지 확인

---

## 다음 단계

1. **구현**: 개발자가 이벤트 정의서 기반 코드 작성
2. **테스트**: QA가 GA4 실시간 리포트에서 이벤트 검증
3. **분석**: 데이터 분석가가 이벤트 기반 대시보드 구성
4. **최적화**: 주간 리포트 기반 이벤트 개선
