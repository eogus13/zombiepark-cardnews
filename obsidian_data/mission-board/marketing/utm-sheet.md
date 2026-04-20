# UTM 관리 시트: 좀비파크

**작성자**: 마케터
**날짜**: 2026-04-17
**목표**: 모든 마케팅 채널의 트래픽 추적 및 성과 분석

---

## 📊 UTM 구조

### UTM 파라미터 정의

```
기본 구조:
https://zombiepark.kr?
  utm_source=[출처: 채널]&
  utm_medium=[매체: 광고 유형]&
  utm_campaign=[캠페인명: 시기/테마]&
  utm_content=[콘텐츠: 구체적 소재]&
  utm_term=[검색어: 유료 검색 전용]
```

### 네이밍 규칙
- 소문자만 사용 (예: Instagram, not INSTAGRAM)
- 언더스코어(`_`)로 단어 구분
- 공백 사용 금지 (언더스코어 또는 하이픈 사용)
- 명확하고 일관된 용어

---

## 🔗 채널별 UTM 전략

### 1. 소셜 미디어 (유기 + 유료)

#### 1-1. 인스타그램 (Organic)

| 콘텐츠 | 소스 | 매체 | 캠페인 | 콘텐츠 | 전체 URL |
|--------|------|------|--------|--------|----------|
| 4대 라이프라인 슬라이드 | instagram | social_organic | zombiepark_launch | lifeline_infographic | https://zombiepark.kr?utm_source=instagram&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=lifeline_infographic |
| 프레퍼 특집 포스팅 | instagram | social_organic | zombiepark_launch | prepper_testimonial | https://zombiepark.kr?utm_source=instagram&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=prepper_testimonial |
| 가족층 스토리 | instagram | social_organic | zombiepark_launch | family_bonding | https://zombiepark.kr?utm_source=instagram&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=family_bonding |
| 릴스: 5초 생존 기술 | instagram | social_organic | zombiepark_launch | reels_survival_5sec | https://zombiepark.kr?utm_source=instagram&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=reels_survival_5sec |
| 릴스: Before/After | instagram | social_organic | zombiepark_launch | reels_transformation | https://zombiepark.kr?utm_source=instagram&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=reels_transformation |
| 프로필 링크 | instagram | social_organic | zombiepark_launch | profile_link | https://zombiepark.kr?utm_source=instagram&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=profile_link |

#### 1-2. 인스타그램 (Paid Ads)

| 광고 세그먼트 | 소스 | 매체 | 캠페인 | 콘텐츠 | 예산 | 전체 URL |
|---------------|------|------|--------|--------|------|----------|
| 프레퍼층 타게팅 | instagram | paid_social | zombiepark_prepper | hero_video | 500,000원 | https://zombiepark.kr?utm_source=instagram&utm_medium=paid_social&utm_campaign=zombiepark_prepper&utm_content=hero_video |
| 가족층 타게팅 | instagram | paid_social | zombiepark_family | family_hero | 400,000원 | https://zombiepark.kr?utm_source=instagram&utm_medium=paid_social&utm_campaign=zombiepark_family&utm_content=family_hero |
| 기업층 타게팅 (LinkedIn) | linkedin | paid_social | zombiepark_corporate | corporate_hero | 300,000원 | https://zombiepark.kr?utm_source=linkedin&utm_medium=paid_social&utm_campaign=zombiepark_corporate&utm_content=corporate_hero |
| 리타겟팅 (방문 후 미전환) | instagram | paid_social | zombiepark_retargeting | testimonial_video | 200,000원 | https://zombiepark.kr?utm_source=instagram&utm_medium=paid_social&utm_campaign=zombiepark_retargeting&utm_content=testimonial_video |

#### 1-3. 페이스북

| 콘텐츠 | 소스 | 매체 | 캠페인 | 콘텐츠 | 전체 URL |
|--------|------|------|--------|--------|----------|
| 유기 포스팅 | facebook | social_organic | zombiepark_launch | page_post | https://zombiepark.kr?utm_source=facebook&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=page_post |
| 유료 광고: 부모 커뮤니티 | facebook | paid_social | zombiepark_family | parent_carousel | https://zombiepark.kr?utm_source=facebook&utm_medium=paid_social&utm_campaign=zombiepark_family&utm_content=parent_carousel |
| 유료 광고: 기업 HR | facebook | paid_social | zombiepark_corporate | hr_benefits | https://zombiepark.kr?utm_source=facebook&utm_medium=paid_social&utm_campaign=zombiepark_corporate&utm_content=hr_benefits |

---

### 2. 유튜브

#### 2-1. 유튜브 Organic

| 영상 | 소스 | 매체 | 캠페인 | 콘텐츠 | 전체 URL |
|------|------|------|--------|--------|----------|
| 소개 영상 (4분) | youtube | social_organic | zombiepark_launch | intro_video | https://zombiepark.kr?utm_source=youtube&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=intro_video |
| 물: 정수 시스템 | youtube | social_organic | zombiepark_launch | water_purification | https://zombiepark.kr?utm_source=youtube&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=water_purification |
| 식량: 갯벌 채집 | youtube | social_organic | zombiepark_launch | food_gathering | https://zombiepark.kr?utm_source=youtube&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=food_gathering |
| 에너지: 발전기 | youtube | social_organic | zombiepark_launch | energy_generator | https://zombiepark.kr?utm_source=youtube&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=energy_generator |
| 의료: 응급 처치 | youtube | social_organic | zombiepark_launch | medical_firstaid | https://zombiepark.kr?utm_source=youtube&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=medical_firstaid |
| 협업: 유튜버 리뷰 | youtube | social_organic | zombiepark_launch | collab_review | https://zombiepark.kr?utm_source=youtube&utm_medium=social_organic&utm_campaign=zombiepark_launch&utm_content=collab_review |

#### 2-2. 유튜브 Ads (YouTube Pre-roll)

| 광고 | 소스 | 매체 | 캠페인 | 콘텐츠 | 예산 | 전체 URL |
|------|------|------|--------|--------|------|----------|
| 15초 동영상 광고 | youtube | paid_video | zombiepark_launch | hero_15sec | 1,000,000원 | https://zombiepark.kr?utm_source=youtube&utm_medium=paid_video&utm_campaign=zombiepark_launch&utm_content=hero_15sec |
| 생존 유튜버 채널 광고 | youtube | paid_video | zombiepark_prepper | prepper_audience_15sec | 500,000원 | https://zombiepark.kr?utm_source=youtube&utm_medium=paid_video&utm_campaign=zombiepark_prepper&utm_content=prepper_audience_15sec |

---

### 3. 검색 엔진 (Google Ads)

#### 3-1. Google Search Ads (SEM)

| 검색어 | 소스 | 매체 | 캠페인 | 콘텐츠 (헤드라인) | 키워드 | 전체 URL |
|--------|------|------|--------|------------------|--------|----------|
| 생존 체험 | google | cpc | zombiepark_search | survival_experience | 생존_체험 | https://zombiepark.kr?utm_source=google&utm_medium=cpc&utm_campaign=zombiepark_search&utm_content=survival_experience&utm_term=survival_experience |
| 서바이벌 훈련 | google | cpc | zombiepark_search | survival_training | 서바이벌_훈련 | https://zombiepark.kr?utm_source=google&utm_medium=cpc&utm_campaign=zombiepark_search&utm_content=survival_training&utm_term=survival_training |
| 생존 기술 배우기 | google | cpc | zombiepark_search | learn_survival | 생존_기술_배우기 | https://zombiepark.kr?utm_source=google&utm_medium=cpc&utm_campaign=zombiepark_search&utm_content=learn_survival&utm_term=learn_survival |
| 팀빌딩 프로그램 | google | cpc | zombiepark_search | teambuilding | 팀빌딩_프로그램 | https://zombiepark.kr?utm_source=google&utm_medium=cpc&utm_campaign=zombiepark_search&utm_content=teambuilding&utm_term=teambuilding |
| 가족 체험 관광 | google | cpc | zombiepark_search | family_experience | 가족_체험_관광 | https://zombiepark.kr?utm_source=google&utm_medium=cpc&utm_campaign=zombiepark_search&utm_content=family_experience&utm_term=family_experience |

#### 3-2. Google Display Ads

| 배너 크기 | 소스 | 매체 | 캠페인 | 콘텐츠 | 예산 | 전체 URL |
|-----------|------|------|--------|--------|------|----------|
| 300×250 | google | display | zombiepark_display | hero_square | 400,000원 | https://zombiepark.kr?utm_source=google&utm_medium=display&utm_campaign=zombiepark_display&utm_content=hero_square |
| 728×90 | google | display | zombiepark_display | hero_leaderboard | 300,000원 | https://zombiepark.kr?utm_source=google&utm_medium=display&utm_campaign=zombiepark_display&utm_content=hero_leaderboard |

---

### 4. 이메일 마케팅

| 이메일 | 소스 | 매체 | 캠페인 | 콘텐츠 | 전체 URL |
|--------|------|------|--------|--------|----------|
| 오픈 소식 | email | newsletter | zombiepark_launch | launch_announcement | https://zombiepark.kr?utm_source=email&utm_medium=newsletter&utm_campaign=zombiepark_launch&utm_content=launch_announcement |
| 주차별 팁 | email | newsletter | zombiepark_education | weekly_survival_tip | https://zombiepark.kr?utm_source=email&utm_medium=newsletter&utm_campaign=zombiepark_education&utm_content=weekly_survival_tip |
| 베타 결과 공유 | email | newsletter | zombiepark_launch | beta_results | https://zombiepark.kr?utm_source=email&utm_medium=newsletter&utm_campaign=zombiepark_launch&utm_content=beta_results |
| 마지막 기회 (리마인더) | email | newsletter | zombiepark_launch | final_reminder | https://zombiepark.kr?utm_source=email&utm_medium=newsletter&utm_campaign=zombiepark_launch&utm_content=final_reminder |
| 기업 특화 정보 | email | newsletter | zombiepark_corporate | hr_special | https://zombiepark.kr?utm_source=email&utm_medium=newsletter&utm_campaign=zombiepark_corporate&utm_content=hr_special |

---

### 5. 오프라인 / 파트너십

#### 5-1. PR & 미디어

| 매체 | 소스 | 매체 | 캠페인 | 콘텐츠 | 전체 URL |
|------|------|------|--------|--------|----------|
| 뉴스 기사 | press | pr | zombiepark_launch | news_article | https://zombiepark.kr?utm_source=press&utm_medium=pr&utm_campaign=zombiepark_launch&utm_content=news_article |
| 블로그 리뷰 | blog | referral | zombiepark_launch | influencer_review | https://zombiepark.kr?utm_source=blog&utm_medium=referral&utm_campaign=zombiepark_launch&utm_content=influencer_review |
| 팟캐스트 언급 | podcast | audio | zombiepark_launch | podcast_mention | https://zombiepark.kr?utm_source=podcast&utm_medium=audio&utm_campaign=zombiepark_launch&utm_content=podcast_mention |

#### 5-2. 파트너십

| 파트너 | 소스 | 매체 | 캠페인 | 콘텐츠 | 전체 URL |
|--------|------|------|--------|--------|----------|
| 여행사 제휴 | partner | referral | zombiepark_launch | travel_agency | https://zombiepark.kr?utm_source=partner&utm_medium=referral&utm_campaign=zombiepark_launch&utm_content=travel_agency |
| 팀빌딩 에이전시 | partner | referral | zombiepark_corporate | teambuild_agency | https://zombiepark.kr?utm_source=partner&utm_medium=referral&utm_campaign=zombiepark_corporate&utm_content=teambuild_agency |
| 부모 커뮤니티 | partner | referral | zombiepark_family | parent_community | https://zombiepark.kr?utm_source=partner&utm_medium=referral&utm_campaign=zombiepark_family&utm_content=parent_community |

---

### 6. 기타 채널

#### 6-1. QR 코드

| 위치 | 소스 | 매체 | 캠페인 | 콘텐츠 | 전체 URL |
|------|------|------|--------|--------|----------|
| 전단지 | offline | qrcode | zombiepark_launch | flyer_qr | https://zombiepark.kr?utm_source=offline&utm_medium=qrcode&utm_campaign=zombiepark_launch&utm_content=flyer_qr |
| 포스터 | offline | qrcode | zombiepark_launch | poster_qr | https://zombiepark.kr?utm_source=offline&utm_medium=qrcode&utm_campaign=zombiepark_launch&utm_content=poster_qr |

#### 6-2. 커뮤니티 (비유료)

| 커뮤니티 | 소스 | 매체 | 캠페인 | 콘텐츠 | 전체 URL |
|---------|------|------|--------|--------|----------|
| 프레퍼 포럼 | community | organic | zombiepark_launch | prepper_forum | https://zombiepark.kr?utm_source=community&utm_medium=organic&utm_campaign=zombiepark_launch&utm_content=prepper_forum |
| 밀리터리 커뮤니티 | community | organic | zombiepark_launch | military_forum | https://zombiepark.kr?utm_source=community&utm_medium=organic&utm_campaign=zombiepark_launch&utm_content=military_forum |
| 엄마 커뮤니티 (밴드) | community | organic | zombiepark_family | parent_band | https://zombiepark.kr?utm_source=community&utm_medium=organic&utm_campaign=zombiepark_family&utm_content=parent_band |

---

## 📈 분석 대시보드 설정 (GA4)

### 주요 추적 지표

#### 1. 세그먼트별 성과
```
프레퍼층:
- 소스: instagram, youtube, community
- 매체: social_organic, paid_social, organic
- 캠페인: zombiepark_launch, zombiepark_prepper

가족층:
- 소스: facebook, instagram, email
- 매체: paid_social, social_organic, newsletter
- 캠페인: zombiepark_launch, zombiepark_family

기업층:
- 소스: linkedin, email, partner
- 매체: paid_social, newsletter, referral
- 캠페인: zombiepark_corporate
```

#### 2. 퍼널 분석
```
Landing → Browse → Signup → Payment Complete
```

#### 3. 전환 추적 (Goal)
```
Goal 1: Newsletter 구독 (CPA: 3,000원 이하)
Goal 2: 예약 신청 (CPA: 15,000원 이하)
Goal 3: VIP 문의 (CPA: 50,000원 이하)
```

---

## 🎯 캠페인별 목표

| 캠페인 | 기간 | 소스 | 목표 방문 | 목표 예약 | 목표 CPA |
|--------|------|------|---------|---------|---------|
| zombiepark_launch | 5월 1-31 | 전체 | 30,000 | 500 | 30,000원 |
| zombiepark_prepper | 5월 1-31 | Instagram, YouTube, Community | 10,000 | 200 | 25,000원 |
| zombiepark_family | 5월 1-31 | Facebook, Instagram, Email | 8,000 | 150 | 32,000원 |
| zombiepark_corporate | 5월 1-31 | LinkedIn, Email, Partner | 5,000 | 50 | 60,000원 |
| zombiepark_retargeting | 5월 1-31 | Instagram, Facebook | 3,000 | 100 | 40,000원 |
| zombiepark_search | 5월 1-31 | Google (SEM) | 4,000 | 100 | 50,000원 |

---

## 🔍 주간 성과 리포트 항목

### 매주 월요일 데이터 분석
1. **트래픽 소스별 성과** (방문수, 세션, 사용자)
2. **전환율 분석** (캠페인별 CPA, ROI)
3. **세그먼트별 행동** (머물이 시간, 스크롤 깊이, 이탈)
4. **상위 콘텐츠** (가장 많은 클릭 유도한 포스팅)
5. **개선 기회** (낮은 성과 채널 및 캠페인)
6. **다음 주 최적화 계획**

---

## 📋 체크리스트

### 론칭 전 (4월)
- [ ] GA4 계정 설정
- [ ] 모든 UTM 링크 생성 및 테스트
- [ ] Google Search Console 설정
- [ ] 각 채널별 태그 매니저 설정 확인
- [ ] 예약 페이지 추적 코드 설정
- [ ] A/B 테스트 설정 (캠페인별)

### 론칭 후 (5월)
- [ ] 일일 성과 모니터링
- [ ] 주간 리포트 생성 및 검토
- [ ] 성과 낮은 캠페인 즉시 최적화
- [ ] 세그먼트별 메시지 반응도 분석
- [ ] 주 1회 팀 미팅에서 결과 공유
- [ ] 월말 최종 결산

---

## 다음 단계

1. 데이터 분석가에게 GA4 추적 설정 요청
2. 모든 UTM 링크 최종 검토 및 테스트
3. 콘텐츠 캘린더의 각 항목에 대응하는 UTM 링크 연결
4. 예약 시스템과 GA4 연동 확인
5. 일일/주간 리포트 템플릿 준비
