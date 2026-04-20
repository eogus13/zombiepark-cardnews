# 🧟 좀비파크 카드뉴스 자동화

영흥도 좀비파크 인스타그램 카드뉴스를 **매일 자동 발행**하는 시스템입니다.
옵시디언 볼트의 기획 자료를 AI가 읽고, 매주 7개 카드뉴스를 생성하여 발행합니다.

## 시스템 구조

```
금요일 10:00 KST ─── 주간 콘텐츠 생성
  옵시디언 스캔 → Gemini AI 7개 생성 → 전략가 에이전트 강화 → 저장

매일 18:00 KST ─── 일일 발행
  콘텐츠 선택 → 텍스트 다듬기 → 이미지 생성 → 합성 → 업로드 → 발행

매일 21:00 KST ─── 인사이트 수집
  Instagram 데이터 수집 → 에너지 점수 계산 → 주간 분석 (일요일)
```

## 기술 스택 (월 비용: ₩0)

| 역할 | 서비스 | 무료 범위 |
|------|--------|-----------|
| 텍스트 AI | Gemini 2.5 Flash | 무료 티어 |
| 이미지 AI | Stability AI | 커뮤니티 라이선스 |
| 이미지 호스팅 | Cloudinary | 25GB/월 |
| 발행 | Instagram Graph API | 무료 |
| 알림 | Telegram Bot + Discord Webhook | 무료 |
| 자동화 | GitHub Actions (public repo) | 무료 |

## 에이전트 협업

3개 AI 에이전트가 파이프라인 각 단계에서 품질을 높입니다:

- **전략가** (주간): 페르소나 매칭, 고객 여정 단계 배정, 우선순위 조정
- **마케터** (일일): PAS 프레임워크 캡션, 심리 트리거 적용, A/B 캡션
- **데이터분석가** (일일+주간): 인사이트 수집, 에너지 점수, 피드백 루프

## 콘텐츠 유형 (요일별)

| 요일 | 유형 | 설명 |
|------|------|------|
| 월 | did_you_know | 좀비 세계관 상식 |
| 화 | quiz | 서바이벌 퀴즈 |
| 수 | fact_check | 좀비 팩트체크 |
| 목 | survival_skill | 생존 스킬 팁 |
| 금 | culture_story | 좀비 문화 이야기 |
| 토 | scenario | 생존 시나리오 |
| 일 | yeongheung_tmi | 영흥도 TMI |

## 설치 및 배포

### 1. 저장소 생성

```bash
git init zombiepark-cardnews
cd zombiepark-cardnews
# 이 프로젝트의 모든 파일을 복사
git add .
git commit -m "🧟 초기 설정"
git remote add origin https://github.com/YOUR_USERNAME/zombiepark-cardnews.git
git push -u origin main
```

### 2. GitHub Secrets 설정

Settings → Secrets and variables → Actions에서 아래 10개를 등록:

```
GEMINI_API_KEY          # Google AI Studio에서 발급
STABILITY_API_KEY       # Stability AI에서 발급
CLOUDINARY_CLOUD_NAME   # Cloudinary 대시보드
CLOUDINARY_API_KEY      # Cloudinary 대시보드
CLOUDINARY_API_SECRET   # Cloudinary 대시보드
INSTAGRAM_ACCESS_TOKEN  # Meta Developer에서 발급
INSTAGRAM_BUSINESS_ID   # Instagram 비즈니스 계정 ID
TELEGRAM_BOT_TOKEN      # BotFather에서 발급
TELEGRAM_CHAT_ID        # 텔레그램 채팅 ID
DISCORD_WEBHOOK_URL     # Discord 서버 웹훅 URL
```

### 3. 옵시디언 데이터

`obsidian_data/` 폴더에 좀비파크 기획 문서(.md)를 넣으면 AI가 자동으로 읽습니다.
새 자료를 추가하면 다음 금요일 주간 업데이트에 반영됩니다.

### 4. 수동 실행 테스트

```bash
# 로컬 테스트
pip install -r requirements.txt
python weekly_update.py  # 주간 콘텐츠 생성
python main.py           # 일일 발행

# GitHub Actions 수동 실행
# Actions 탭 → 워크플로우 선택 → Run workflow
```

## 프로젝트 구조

```
zombiepark-cardnews/
├── main.py                 # 일일 발행 파이프라인
├── weekly_update.py        # 주간 콘텐츠 생성
├── collect_insights.py     # 인사이트 수집
├── requirements.txt
├── .env.example
├── src/
│   ├── scanner.py          # 옵시디언 변경 감지
│   ├── content_builder.py  # AI 콘텐츠 생성
│   ├── selector.py         # 일일 콘텐츠 선택
│   ├── text_generator.py   # 텍스트 다듬기
│   ├── image_generator.py  # AI 배경 이미지
│   ├── image_composer.py   # 텍스트 오버레이 합성
│   ├── uploader.py         # Cloudinary 업로드
│   ├── publisher.py        # Instagram 캐러셀 발행
│   ├── reviewer.py         # Telegram 미리보기
│   ├── logger.py           # Discord 로깅
│   ├── agent_enhancer.py   # 에이전트 협업
│   └── utils.py
├── data/                   # 런타임 데이터 (자동 관리)
├── obsidian_data/          # 좀비파크 기획 문서
└── .github/workflows/      # GitHub Actions
    ├── daily-post.yml      # 매일 18:00
    ├── weekly-update.yml   # 금 10:00
    └── collect-insights.yml # 매일 21:00
```

## 브랜드 디자인

- 배경: 다크 퍼플 (#1a0a2e)
- 강조: 네온 그린 (#39FF14)
- 폰트: Pretendard Bold
- 크기: 1080×1080px (인스타그램 정사각형)
