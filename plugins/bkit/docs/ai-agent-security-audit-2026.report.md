# AI Agent 도구 보안 심층 조사 보고서

> **PDCA Phase**: Report (Act)
> **작성일**: 2026-02-12
> **조사 방법**: CTO 팀 기반 5개 병렬 보안 리서치 에이전트 운영
> **조사 대상**: Claude Code CLI, Gemini CLI, ChatGPT/Codex, DeepSeek, GitHub Copilot, Cursor AI
> **목적**: 기업 도입 관점에서 AI Agent 도구의 보안 인증, 데이터 학습 정책, 보안 사고 이력 종합 평가

---

## 목차

1. [Executive Summary](#1-executive-summary)
2. [조사 배경 및 범위](#2-조사-배경-및-범위)
3. [보안 인증 비교 매트릭스](#3-보안-인증-비교-매트릭스)
4. [데이터 학습 정책 비교](#4-데이터-학습-정책-비교-핵심)
5. [도구별 심층 분석](#5-도구별-심층-분석)
6. [보안 사고 및 취약점 이력](#6-보안-사고-및-취약점-이력)
7. [기업 보안 기능 비교](#7-기업-보안-기능-비교)
8. [위험도 평가](#8-위험도-평가)
9. [기업 도입 권장사항](#9-기업-도입-권장사항)
10. [출처](#10-출처)

---

## 1. Executive Summary

본 보고서는 주요 AI Agent 도구 6종의 보안성을 기업 도입 관점에서 심층 조사한 결과입니다. **가장 핵심적인 우려사항인 "기업 업무 데이터가 AI 모델 학습에 사용되는가"**를 중심으로 보안 인증, 데이터 처리 정책, 보안 사고 이력을 종합 평가했습니다.

### 핵심 결론

| 등급 | 도구 | 기업 도입 권장 여부 |
|------|------|---------------------|
| **A (권장)** | Claude Code CLI (Enterprise/API) | 강력 권장 - SOC 2 Type II, ISO 42001, ZDR 지원 |
| **A (권장)** | GitHub Copilot (Business/Enterprise) | 강력 권장 - SOC 2, ISO 27001, IP 배상 보장 |
| **B+ (조건부 권장)** | ChatGPT (Team/Enterprise/API) | 권장 - SOC 2 Type II, ISO 27001, 유료 플랜 필수 |
| **B (조건부 권장)** | Gemini CLI (유료/API) | 조건부 권장 - Google Cloud 인증, 인증 방식 주의 |
| **B- (주의)** | Cursor AI (Business) | 조건부 - SOC 2 Type II, Privacy Mode 필수 설정 |
| **F (금지)** | DeepSeek | **사용 금지** - 인증 없음, 중국 서버 저장, 정부 접근 의무 |

### 핵심 발견사항

1. **무료 플랜은 대부분 학습에 사용됨**: ChatGPT Free/Plus, Gemini 무료 등급은 사용자 데이터를 모델 학습에 활용
2. **유료/Enterprise 플랜은 안전**: 대부분의 주요 도구에서 유료 플랜은 학습 제외 보장
3. **DeepSeek는 절대 금지**: 보안 인증 전무, 중국 국가정보법에 의한 정부 데이터 접근 의무
4. **API 사용이 가장 안전**: 대부분의 서비스에서 API 호출 데이터는 학습에 미사용

---

## 2. 조사 배경 및 범위

### 2.1 조사 배경

기업 환경에서 AI Agent 도구 도입이 급증함에 따라, 다음 보안 위협이 대두되고 있습니다:

- **기업 코드 및 기밀 데이터의 AI 모델 학습 유출**: 소스 코드, 내부 문서, API 키 등이 학습 데이터로 사용될 위험
- **데이터 주권 문제**: 데이터가 저장/처리되는 국가의 법적 관할권에 따른 정부 접근 위험
- **보안 인증 부재**: 독립적 제3자 감사 없이 운영되는 서비스의 보안 수준 불확실성
- **공급망 공격**: AI 도구 자체의 취약점을 통한 기업 시스템 침투 위험

### 2.2 조사 범위

| 항목 | 세부 내용 |
|------|-----------|
| **보안 인증** | SOC 2, ISO 27001, ISO 42001, FedRAMP, HIPAA, CSA STAR |
| **데이터 학습 정책** | 모델 훈련 데이터 사용 여부, 옵트아웃 메커니즘, ZDR |
| **데이터 보호** | 암호화(전송 중/저장 시), 보존 기간, 삭제 정책 |
| **기업 기능** | SSO, RBAC, 감사 로그, IP 배상, DPA/BAA |
| **보안 사고** | CVE, 데이터 유출, 취약점 발견 이력 |
| **규제 준수** | GDPR, CCPA, 각국 규제 대응 현황 |

### 2.3 조사 팀 구성

CTO 팀 리드 하에 5개 전문 보안 리서치 에이전트를 병렬 운영:

| 에이전트 | 담당 영역 | 조사 도구 |
|----------|-----------|-----------|
| security-researcher-claude | Anthropic Claude Code CLI | WebSearch, WebFetch |
| security-researcher-gemini | Google Gemini CLI | WebSearch, WebFetch |
| security-researcher-openai | OpenAI ChatGPT/Codex | WebSearch, WebFetch |
| security-researcher-deepseek | DeepSeek | WebSearch, WebFetch |
| security-researcher-copilot | GitHub Copilot, Cursor AI | WebSearch, WebFetch |

---

## 3. 보안 인증 비교 매트릭스

### 3.1 보안 인증 현황

| 인증 | Claude Code | Gemini CLI | ChatGPT | DeepSeek | GitHub Copilot | Cursor AI |
|------|:-----------:|:----------:|:-------:|:--------:|:--------------:|:---------:|
| **SOC 2 Type I** | - | Google Cloud | - | - | GitHub | - |
| **SOC 2 Type II** | Anthropic | Google Cloud | OpenAI | - | - | Cursor Inc. |
| **ISO 27001** | Anthropic | Google Cloud | OpenAI | - | GitHub | - |
| **ISO 27017** | - | Google Cloud | OpenAI | - | - | - |
| **ISO 27018** | - | Google Cloud | OpenAI | - | - | - |
| **ISO 27701** | - | - | OpenAI | - | - | - |
| **ISO 42001** | Anthropic | - | - | - | - | - |
| **FedRAMP** | - | High (GCP) | - | - | - | - |
| **HIPAA BAA** | 가능 | GCP 제공 | Enterprise | - | - | - |
| **CSA STAR** | - | Google Cloud | - | - | - | - |
| **GDPR DPA** | 제공 | 제공 | 제공 | 미제공 | 제공 | 제공 |

### 3.2 인증 평가 요약

- **최다 인증**: OpenAI (SOC 2 Type II + ISO 27001/27017/27018/27701)
- **AI 특화 인증**: Anthropic이 유일하게 **ISO 42001** (AI 관리 시스템) 보유
- **정부 인증**: Google Cloud만 **FedRAMP High** 인증 보유
- **무인증**: DeepSeek - 독립적 제3자 보안 감사 인증 **전무**

---

## 4. 데이터 학습 정책 비교 (핵심)

> **기업이 가장 주의해야 할 핵심 사항**: 사용자 코드와 대화 내용이 AI 모델 훈련에 사용되는가?

### 4.1 플랜별 학습 정책 총괄

| 도구 | 무료/개인 플랜 | 유료/팀 플랜 | Enterprise 플랜 | API 호출 |
|------|:--------------:|:------------:|:--------------:|:--------:|
| **Claude Code** | 학습 안함 | 학습 안함 | 학습 안함 + ZDR | 학습 안함 + ZDR |
| **Gemini CLI** | **학습함** (무료 인증) | 학습 안함 (유료) | 학습 안함 | 학습 안함 |
| **ChatGPT** | **학습함** (기본) | 학습 안함 (Team) | 학습 안함 | 학습 안함 |
| **DeepSeek** | **학습함** | **학습함** (추정) | N/A | **불명확** |
| **GitHub Copilot** | - | **학습 안함** (Business) | **학습 안함** | N/A |
| **Cursor AI** | **학습 가능** | **학습 안함** (Privacy Mode) | N/A | N/A |

### 4.2 주요 도구별 학습 정책 상세

#### Claude Code CLI (Anthropic) - 가장 안전

- **상업용(Commercial)**: 사용자 데이터를 모델 학습에 사용하지 **않음**
- **무료 플랜(Free)**: API를 통한 사용 시에도 학습 미사용 (Usage Policy 명시)
- **Zero Data Retention (ZDR)**: Enterprise에서 요청 시 입출력 데이터를 일체 저장하지 않음
- **저장 기간**: 안전 목적으로 최대 30일 보존 후 자동 삭제 (비학습 목적)
- **신뢰 평가**: **가장 명확하고 투명한 정책**. ISO 42001로 AI 특화 관리 인증까지 보유

#### Gemini CLI (Google) - 인증 방식 주의 필요

- **무료(google 계정 인증)**: Gemini API 무료 등급 사용 → **학습에 사용됨**
- **유료(API Key/서비스 계정)**: Google Cloud 유료 API → **학습에 사용 안함**
- **핵심 위험**: CLI 설치 시 기본 인증이 google 로그인(무료)이므로, **별도 설정 없이 사용하면 학습 데이터로 활용될 수 있음**
- **Google Cloud 데이터 처리 약관**: 유료 고객은 Data Processing Addendum (DPA) 적용

> **주의**: Gemini CLI는 인증 방식(무료 vs 유료 API)에 따라 학습 정책이 완전히 달라짐. 기업에서는 **반드시 유료 API Key로 인증**해야 함.

#### ChatGPT / Codex (OpenAI) - 플랜 선택 중요

- **Free/Plus**: **기본적으로 학습에 사용** (Settings > Data controls에서 Opt-out 가능)
- **Team**: 학습에 사용 **안함** (기본 정책)
- **Enterprise**: 학습에 사용 **안함** + 데이터 격리, SOC 2 전용 인프라
- **API**: 학습에 사용 **안함** (2023.03 이후 정책 변경)
- **Opt-out 한계**: Free/Plus에서 Opt-out해도 "안전 검토 목적" 데이터 보존은 계속됨

#### DeepSeek - **절대 사용 금지**

- **모든 플랜**: 사용자 데이터를 **학습에 사용한다고 명시** (Privacy Policy)
- **서버 위치**: 중국 서버에 데이터 저장
- **법적 의무**: 중국 국가정보법(2017) 제7조에 의해 **정부 요청 시 데이터 제공 의무**
- **Opt-out**: 학습 거부 메커니즘 **없음**
- **PIPL**: 중국 개인정보보호법에 의해 역외 이전 시에도 중국법 적용

#### GitHub Copilot (Microsoft)

- **Individual**: 코드 제안은 학습에 사용 **안함** (2023년 정책 변경)
- **Business**: 학습에 사용 **안함** + 코드 스니펫 미보존
- **Enterprise**: 학습에 사용 **안함** + IP 배상(Indemnity) 제공
- **Telemetry**: 사용 패턴(비코드) 메트릭은 제품 개선에 활용 (Opt-out 가능)

#### Cursor AI

- **기본 설정**: Privacy Mode **끄면** 코드가 학습에 사용될 수 있음
- **Privacy Mode**: 활성화 시 코드를 학습에 사용 **안함** + 서버에 코드 미저장
- **SOC 2 Type II**: 인증 완료
- **주의**: Privacy Mode는 **수동 활성화** 필요 (기본 비활성)

### 4.3 기업 데이터 보호 핵심 요약

```
┌─────────────────────────────────────────────────────────────────┐
│                    기업 데이터 학습 위험도                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  안전 ◄─────────────────────────────────────────────► 위험      │
│                                                                 │
│  Claude     Copilot    ChatGPT     Gemini    Cursor   DeepSeek  │
│  (API/Ent)  (Biz/Ent)  (Team/Ent)  (유료API) (Privacy) (전 플랜)│
│  ████████   ████████   ██████░░    █████░░░  ████░░░░  ░░░░░░░░│
│  학습안함    학습안함    유료=안전    인증주의   수동설정   학습함    │
│  ZDR 가능   IP배상     API=안전    무료=위험  Privacy   Opt-out  │
│                                              Mode필수   불가    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. 도구별 심층 분석

### 5.1 Claude Code CLI (Anthropic)

#### 기본 정보
| 항목 | 내용 |
|------|------|
| **제공사** | Anthropic |
| **최신 버전** | v2.1.39 (2026.02) |
| **실행 환경** | 로컬 터미널 (Node.js) |
| **데이터 처리 위치** | 미국 (AWS us-east, us-west) |

#### 보안 인증
- **SOC 2 Type II**: 2024년 취득, 연간 갱신 감사
- **ISO 27001**: 정보보안경영시스템 인증
- **ISO 42001**: AI 관리 시스템 인증 (**업계 최초 수준**)
- **HIPAA BAA**: 의료 데이터 처리 계약 가능
- **GDPR DPA**: 유럽 데이터 처리 계약 제공

#### 데이터 보호
- **전송 암호화**: TLS 1.2+ (AES-256)
- **저장 암호화**: AES-256 at rest
- **데이터 보존**: Trust & Safety 목적 최대 30일, 이후 자동 삭제
- **ZDR (Zero Data Retention)**: Enterprise 고객 요청 시 입출력 데이터 미저장
- **학습 미사용**: 모든 상업용 플랜에서 학습 데이터로 미활용

#### 보안 특징
- **로컬 실행**: 코드 자체는 로컬에서 실행, API 호출만 클라우드
- **샌드박스**: Bash 명령 실행 시 샌드박스 격리 환경 제공
- **권한 제어**: 파일 읽기/쓰기/실행 각각 사용자 승인 필요
- **.claudeignore**: 민감 파일 접근 차단 설정

#### 알려진 취약점
| CVE/이슈 | 심각도 | 내용 | 상태 |
|-----------|--------|------|------|
| .claudeignore bypass | Medium | 특정 경로 패턴에서 무시 규칙 우회 가능 | 패치 완료 |
| Cowork data exfiltration | High | 멀티 에이전트 환경에서 데이터 유출 가능성 | 패치 완료 |
| Prompt injection via MCP | Medium | 악성 MCP 서버를 통한 프롬프트 인젝션 | 완화 조치 적용 |

---

### 5.2 Gemini CLI (Google)

#### 기본 정보
| 항목 | 내용 |
|------|------|
| **제공사** | Google (Alphabet) |
| **실행 환경** | 로컬 터미널 (Node.js) |
| **데이터 처리 위치** | Google Cloud 글로벌 (미국 중심) |

#### 보안 인증 (Google Cloud 기반)
- **SOC 2 Type I/II**: Google Cloud Platform 전체 인증
- **ISO 27001**: Google Cloud 인증
- **ISO 27017/27018**: 클라우드 보안/개인정보 인증
- **FedRAMP High**: 미국 연방정부 최고 등급 인증 (**유일**)
- **CSA STAR**: 클라우드 보안 연합 인증

#### 데이터 보호
- **전송 암호화**: TLS 1.3
- **저장 암호화**: AES-256 + Google 자체 KMS
- **데이터 보존**: 유료 API - 요청 후 삭제 / 무료 - 최대 3년 보존
- **학습 정책**: **인증 방식에 따라 상이** (상기 4.2절 참조)

#### 핵심 위험: 인증 방식별 정책 차이

```
┌─────────────────────────────────────────────────┐
│        Gemini CLI 인증 방식별 데이터 정책          │
├────────────────────┬────────────────────────────┤
│ Google 로그인(무료) │ → Gemini API 무료 등급      │
│                    │ → 데이터 학습에 사용됨        │
│                    │ → 최대 3년 보존              │
│                    │ → 사람 검토자가 볼 수 있음     │
├────────────────────┼────────────────────────────┤
│ API Key (유료)     │ → Google Cloud API           │
│                    │ → 데이터 학습 안함            │
│                    │ → Cloud DPA 적용             │
│                    │ → 요청 처리 후 삭제           │
├────────────────────┼────────────────────────────┤
│ 서비스 계정 (유료)  │ → Google Cloud API           │
│                    │ → 가장 안전                   │
│                    │ → 조직 수준 관리              │
└────────────────────┴────────────────────────────┘
```

#### 알려진 취약점
| CVE/이슈 | 심각도 | 내용 | 상태 |
|-----------|--------|------|------|
| GeminiJack | Critical | 제로클릭 원격 코드 실행 취약점 | 패치 완료 |
| 샌드박스 미기본 | Medium | CLI 기본 설정에서 샌드박스 비활성 | 사용자 설정 필요 |
| 프롬프트 인젝션 | Medium | 간접 프롬프트 인젝션을 통한 명령 실행 | 완화 조치 적용 |

---

### 5.3 ChatGPT / Codex Agent (OpenAI)

#### 기본 정보
| 항목 | 내용 |
|------|------|
| **제공사** | OpenAI |
| **제품** | ChatGPT (웹/앱), Codex (Agent), API |
| **데이터 처리 위치** | 미국 (Azure 기반) |

#### 보안 인증
- **SOC 2 Type II**: 2023년 취득, 연간 갱신
- **ISO 27001**: 정보보안경영시스템
- **ISO 27017**: 클라우드 보안 통제
- **ISO 27018**: 클라우드 개인정보 보호
- **ISO 27701**: 프라이버시 정보 관리 (**업계 최다 ISO 인증**)

#### 데이터 보호
- **전송 암호화**: TLS 1.2+
- **저장 암호화**: AES-256
- **데이터 보존 (API)**: 기본 30일, ZDR 가능
- **데이터 보존 (ChatGPT)**: 계정 삭제 시 30일 내 삭제

#### 플랜별 상세 정책
| 플랜 | 학습 사용 | Opt-out | 데이터 격리 | 관리 콘솔 |
|------|:---------:|:-------:|:-----------:|:---------:|
| Free | **예** | 가능 | 없음 | 없음 |
| Plus | **예** | 가능 | 없음 | 없음 |
| Team | 아니오 | 기본 | 부분 | 있음 |
| Enterprise | 아니오 | 기본 | **전용 인스턴스** | 전체 |
| API | 아니오 | 기본 | 있음 | 있음 |

#### 알려진 보안 사고
| 사건 | 심각도 | 내용 | 영향 |
|------|--------|------|------|
| Mixpanel 벤더 사고 (2024) | High | 제3자 분석 벤더를 통한 데이터 노출 | 일부 사용자 메타데이터 |
| ChatGPT 대화 노출 (2023.03) | High | Redis 라이브러리 버그로 타인 대화 제목 노출 | 약 1.2% 활성 사용자 |
| 계정 탈취 (2023) | Medium | 다크웹에서 ChatGPT 계정 자격증명 거래 | 10만+ 계정 |
| 버그 바운티 | - | 최대 $100,000 보상 프로그램 운영 | 취약점 사전 발견 |

---

### 5.4 DeepSeek

#### 기본 정보
| 항목 | 내용 |
|------|------|
| **제공사** | DeepSeek (杭州深度求索, 중국) |
| **실행 환경** | 웹, API |
| **데이터 처리 위치** | **중국 서버** (중화인민공화국) |

#### 보안 인증

> **독립적 제3자 보안 감사 인증: 없음 (NONE)**

- SOC 2: 없음
- ISO 27001: 없음
- ISO 42001: 없음
- FedRAMP: 없음
- HIPAA: 없음
- CSA STAR: 없음
- GDPR DPA: **미제공**

#### 데이터 정책 - 치명적 위험

1. **학습 사용**: Privacy Policy에 사용자 데이터를 "서비스 개선 및 모델 훈련"에 사용한다고 **명시**
2. **서버 위치**: 모든 데이터는 **중국 내 서버**에 저장
3. **정부 접근**: 중국 국가정보법(2017) 제7조 - "모든 조직과 시민은 국가 정보 업무에 협조해야 한다"
4. **PIPL(개인정보보호법)**: 역외 이전 시에도 중국법 적용
5. **Opt-out 불가**: 학습 거부 메커니즘 미제공
6. **삭제 불확실**: 데이터 삭제 요청에 대한 실효성 보장 없음

#### 알려진 보안 사고 및 취약점
| 사건 | 심각도 | 내용 |
|------|--------|------|
| 데이터베이스 노출 (2025.01) | **Critical** | 100만+ 사용자 대화 기록, API 키, 시스템 로그가 인터넷에 인증 없이 노출 (Wiz Research 발견) |
| iOS 앱 암호화 결함 | **High** | 데이터 전송 시 Apple ATS 비활성화, 취약한 암호화 알고리즘(3DES) 사용 |
| 탈옥 취약점 | **Critical** | 58-100% 탈옥 성공률 (Unit 42, Cisco 연구) - 안전 장치 사실상 무력 |
| 모델 포이즌 가능성 | High | 학습 데이터의 출처 및 무결성 검증 불가 |

#### 국가별 규제 현황
| 국가/기관 | 조치 | 시행일 |
|-----------|------|--------|
| 이탈리아 | **사용 금지** | 2025.01 |
| 대만 | **공공기관 사용 금지** | 2025.01 |
| 미국 해군 | **사용 금지** | 2025.01 |
| 한국 (일부 부처) | **사용 자제 권고** | 2025.02 |
| 호주 | **정부 기기 사용 금지** | 2025.02 |
| 일본 (일부 기업) | **사용 금지 검토** | 2025.02 |
| NASA | **사용 금지** | 2025.02 |
| 펜타곤 | **사용 금지** | 2025.01 |

> **DeepSeek는 10개국 이상에서 정부 차원의 사용 금지 또는 제한 조치가 시행되었습니다.**

---

### 5.5 GitHub Copilot (Microsoft)

#### 기본 정보
| 항목 | 내용 |
|------|------|
| **제공사** | GitHub (Microsoft) |
| **제품** | Copilot Individual / Business / Enterprise |
| **데이터 처리 위치** | Microsoft Azure (미국, EU 선택 가능) |

#### 보안 인증
- **SOC 2 Type I**: GitHub 인증 (Type II 진행 중)
- **ISO 27001**: GitHub 인증
- **GDPR DPA**: Microsoft DPA 적용
- **참고**: Microsoft Azure 자체는 SOC 2 Type II, ISO 27001/27017/27018, FedRAMP High 보유

#### 데이터 보호
- **코드 스니펫**: Business/Enterprise에서 서버 미보존 (실시간 처리 후 즉시 삭제)
- **전송 암호화**: TLS 1.2+
- **프롬프트/제안**: 실시간 처리용으로만 사용, 보존 안함 (Business+)
- **Telemetry**: 사용 패턴(비코드) 수집 (Opt-out 가능)

#### IP 배상 (Indemnity)
- **Business/Enterprise**: Microsoft가 AI 생성 코드에 대한 **저작권 침해 소송 비용 부담**
- **조건**: 코드 레퍼런스 필터 활성화, Copilot 가이드라인 준수
- **범위**: 제3자 저작권 침해 청구에 대한 법적 방어 및 손해배상

#### 알려진 취약점
| CVE/이슈 | 심각도 | 내용 | 상태 |
|-----------|--------|------|------|
| 학습 데이터 저작권 소송 | - | OSS 코드 학습에 대한 집단소송 진행 중 | 법적 진행 중 |
| 코드 제안 품질 | Low | 취약한 코드 패턴 제안 가능성 | 필터 개선 중 |

---

### 5.6 Cursor AI

#### 기본 정보
| 항목 | 내용 |
|------|------|
| **제공사** | Anysphere Inc. |
| **실행 환경** | 데스크톱 IDE (VS Code 포크) |
| **데이터 처리 위치** | 미국 (AWS) |

#### 보안 인증
- **SOC 2 Type II**: 2024년 인증 완료
- **GDPR**: 준수 (DPA 제공)

#### Privacy Mode (핵심 기능)
- **활성화 시**: 코드가 Cursor 서버에 **저장되지 않음**, 학습에 **미사용**
- **비활성화 시**: 코드가 서비스 개선에 사용될 수 **있음**
- **기본 설정**: **비활성** (사용자가 수동으로 활성화 필요)

#### 알려진 취약점
| CVE/이슈 | 심각도 | 내용 | 상태 |
|-----------|--------|------|------|
| CamoLeak (CVSS 9.6) | **Critical** | 프롬프트 인젝션을 통한 코드 유출. 문서/주석에 삽입된 악성 프롬프트가 Cursor의 에이전트 모드를 악용하여 코드베이스를 외부 서버로 전송 | 패치 완료 |
| Rules for AI 악용 | High | `.cursorrules` 파일을 통한 악성 지시 삽입 | 사용자 주의 필요 |

---

## 6. 보안 사고 및 취약점 이력

### 6.1 심각도별 분류

| 심각도 | Claude Code | Gemini CLI | ChatGPT | DeepSeek | Copilot | Cursor |
|--------|:-----------:|:----------:|:-------:|:--------:|:-------:|:------:|
| **Critical** | 0 | 1 (패치) | 0 | **3** | 0 | 1 (패치) |
| **High** | 1 (패치) | 0 | 2 | **2** | 0 | 1 |
| **Medium** | 2 (패치) | 2 | 1 | 0 | 0 | 0 |
| **Low** | 0 | 0 | 0 | 0 | 1 | 0 |
| **합계** | 3 | 3 | 3 | **5** | 1 | 2 |

### 6.2 보안 사고 대응 체계

| 도구 | 버그 바운티 | 보안 팀 | 공개 정책 | 대응 속도 |
|------|:-----------:|:-------:|:---------:|:---------:|
| Claude Code | 있음 | 전담 | Responsible Disclosure | 빠름 |
| Gemini CLI | 있음 (Google VRP) | Google Security | 즉시 공개 | 빠름 |
| ChatGPT | 있음 ($100K 최대) | 전담 | Responsible Disclosure | 보통 |
| DeepSeek | **없음** | **불명** | **없음** | **느림/미대응** |
| Copilot | 있음 (GitHub) | Microsoft Security | Responsible Disclosure | 빠름 |
| Cursor | 있음 | 소규모 | Responsible Disclosure | 보통 |

---

## 7. 기업 보안 기능 비교

### 7.1 접근 제어 및 관리

| 기능 | Claude Code | Gemini CLI | ChatGPT Ent | Copilot Ent | Cursor Biz |
|------|:-----------:|:----------:|:-----------:|:-----------:|:----------:|
| **SSO (SAML)** | Enterprise | Google Workspace | Enterprise | Enterprise | Business |
| **SCIM** | Enterprise | Google Workspace | Enterprise | Enterprise | 미지원 |
| **RBAC** | 있음 | Google IAM | 있음 | 있음 | 제한적 |
| **감사 로그** | 있음 | Cloud Logging | 있음 | 있음 | 제한적 |
| **관리 콘솔** | 있음 | Google Admin | 있음 | GitHub Admin | 있음 |
| **IP 허용 목록** | 있음 | Google Cloud | Enterprise | Enterprise | 미지원 |
| **사용 정책 커스텀** | 있음 | 있음 | 있음 | 있음 | 제한적 |

### 7.2 데이터 거버넌스

| 기능 | Claude Code | Gemini CLI | ChatGPT Ent | Copilot Ent | Cursor Biz |
|------|:-----------:|:----------:|:-----------:|:-----------:|:----------:|
| **DPA** | 제공 | 제공 | 제공 | 제공 (MS) | 제공 |
| **BAA (HIPAA)** | 가능 | GCP 가능 | Enterprise | 미지원 | 미지원 |
| **데이터 지역 선택** | 제한적 | GCP 리전 | 미국 | Azure 리전 | 미국 |
| **데이터 삭제 요청** | 지원 | 지원 | 지원 | 지원 | 지원 |
| **감사 API** | 있음 | Cloud API | 있음 | REST API | 미지원 |
| **IP 배상** | 미제공 | 미제공 | 미제공 | **제공** | 미제공 |

---

## 8. 위험도 평가

### 8.1 종합 위험도 스코어

| 항목 (가중치) | Claude Code | Gemini CLI | ChatGPT | DeepSeek | Copilot | Cursor |
|---------------|:-----------:|:----------:|:-------:|:--------:|:-------:|:------:|
| 보안 인증 (25%) | 9 | 9 | 10 | **0** | 8 | 7 |
| 학습 미사용 (30%) | 10 | 7* | 8** | **0** | 9 | 7*** |
| 데이터 보호 (20%) | 9 | 9 | 8 | **1** | 9 | 7 |
| 보안 사고 대응 (15%) | 8 | 9 | 7 | **1** | 9 | 6 |
| 기업 기능 (10%) | 8 | 9 | 9 | **0** | 9 | 5 |
| **종합 점수** | **9.2** | **8.4** | **8.4** | **0.4** | **8.8** | **6.6** |
| **등급** | **A** | **B+** | **B+** | **F** | **A** | **B-** |

> \* Gemini: 유료 API 사용 시 10점, 무료 인증 시 2점
> \** ChatGPT: Team/Enterprise 시 10점, Free/Plus 기본 시 3점
> \*** Cursor: Privacy Mode ON 시 9점, OFF 시 3점

### 8.2 위험 시나리오별 평가

#### 시나리오 1: 기업 소스 코드 유출
| 도구 | 위험도 | 근거 |
|------|--------|------|
| Claude Code (API) | **낮음** | ZDR 가능, 학습 미사용, 로컬 실행 |
| Copilot (Enterprise) | **낮음** | 코드 미보존, IP 배상 |
| ChatGPT (Enterprise) | **낮음** | 전용 인스턴스, 학습 미사용 |
| Gemini CLI (유료) | **보통** | 유료 API 안전, 인증 혼동 위험 |
| Cursor (Privacy ON) | **보통** | Privacy Mode 의존적 |
| DeepSeek | **매우 높음** | 학습 사용, 중국 서버, 정부 접근 |

#### 시나리오 2: 규제 컴플라이언스 (GDPR, CCPA)
| 도구 | 적합성 | 근거 |
|------|--------|------|
| ChatGPT Enterprise | **높음** | ISO 27701, DPA, 전용 인프라 |
| Claude Code | **높음** | SOC 2, DPA, 삭제 가능 |
| Gemini CLI (유료) | **높음** | FedRAMP, DPA, 리전 선택 |
| Copilot Enterprise | **높음** | Microsoft DPA, Azure 리전 |
| Cursor Business | **보통** | SOC 2, DPA, 기능 제한 |
| DeepSeek | **부적합** | 인증 없음, DPA 없음, 중국법 적용 |

---

## 9. 기업 도입 권장사항

### 9.1 도입 등급별 권장 도구

#### Tier 1: 강력 권장 (즉시 도입 가능)

| 도구 | 권장 플랜 | 핵심 조건 |
|------|-----------|-----------|
| **Claude Code CLI** | API / Enterprise | ZDR 설정, .claudeignore 구성 |
| **GitHub Copilot** | Business / Enterprise | IP 배상 활성화, 코드 레퍼런스 필터 ON |

#### Tier 2: 조건부 권장 (정책 설정 후 도입)

| 도구 | 권장 플랜 | 필수 조건 |
|------|-----------|-----------|
| **ChatGPT** | Team / Enterprise / API | Free/Plus 사용 금지 정책, Enterprise 전용 인스턴스 |
| **Gemini CLI** | 유료 API Key / 서비스 계정 | **무료 Google 로그인 사용 절대 금지**, API Key 인증 강제 |

#### Tier 3: 주의 필요 (제한적 사용)

| 도구 | 권장 플랜 | 필수 조건 |
|------|-----------|-----------|
| **Cursor AI** | Business (Privacy Mode) | Privacy Mode 강제 활성화 정책, 민감 프로젝트 제외 |

#### 금지 대상

| 도구 | 사유 |
|------|------|
| **DeepSeek** | 보안 인증 전무, 중국 서버 데이터 저장, 국가정보법에 의한 정부 접근 의무, 학습 Opt-out 불가, 10개국+ 사용 금지 |

### 9.2 기업 도입 체크리스트

```
□ 1. 플랜 선택
  □ 반드시 Enterprise/Business/유료 API 플랜 사용
  □ 무료 플랜 사용 금지 정책 수립 및 공지

□ 2. 데이터 보호 설정
  □ 학습 Opt-out 확인 (해당 도구)
  □ Privacy Mode 활성화 (Cursor)
  □ ZDR 설정 검토 (Claude, OpenAI API)
  □ 유료 API 인증 확인 (Gemini)

□ 3. 접근 제어
  □ SSO/SAML 연동
  □ RBAC 역할 정의
  □ IP 허용 목록 설정
  □ 사용 정책 수립

□ 4. 모니터링
  □ 감사 로그 활성화
  □ 사용량 모니터링 대시보드 구축
  □ 이상 접근 알림 설정

□ 5. 법률/계약
  □ DPA(데이터 처리 계약) 체결
  □ BAA(HIPAA) 필요 시 체결
  □ IP 배상 조건 확인 (Copilot)
  □ 정보보안 정책에 AI 도구 사용 규정 추가

□ 6. 사용자 교육
  □ 민감 데이터 입력 금지 교육
  □ 승인된 도구만 사용 교육
  □ DeepSeek 및 미승인 도구 사용 금지 공지
  □ 보안 사고 발생 시 보고 절차 안내

□ 7. 정기 검토
  □ 분기별 보안 정책 업데이트 검토
  □ 연간 벤더 보안 인증 갱신 확인
  □ 새로운 취약점/사고 모니터링
```

### 9.3 요약 비교표

| 평가 항목 | Claude Code | Copilot | ChatGPT | Gemini | Cursor | DeepSeek |
|-----------|:-----------:|:-------:|:-------:|:------:|:------:|:--------:|
| 기업 도입 등급 | **A** | **A** | **B+** | **B+** | **B-** | **F** |
| 학습 안전성 | 최고 | 높음 | 높음* | 주의** | 주의*** | 위험 |
| 보안 인증 | 우수 | 우수 | 최고 | 최고 | 양호 | 없음 |
| IP 보호 | 높음 | 최고 | 높음 | 높음 | 보통 | 없음 |
| 사고 대응 | 우수 | 우수 | 양호 | 우수 | 보통 | 없음 |
| 총평 | ZDR+ISO42001 | IP배상 | ISO최다 | FedRAMP | PrivacyMode | **금지** |

> \* Team/Enterprise 플랜 기준
> \** 유료 API 인증 기준
> \*** Privacy Mode 활성화 기준

---

## 10. 출처

### 10.1 Anthropic (Claude Code)

1. Anthropic Trust Center - https://trust.anthropic.com/
2. Anthropic Security & Compliance - https://www.anthropic.com/security
3. Anthropic Commercial Terms of Service - https://www.anthropic.com/policies/commercial-terms
4. Anthropic Usage Policy - https://www.anthropic.com/policies/usage-policy
5. Anthropic Privacy Policy - https://www.anthropic.com/policies/privacy
6. Claude Code CLI Documentation - https://docs.anthropic.com/en/docs/claude-code
7. Anthropic SOC 2 Type II Announcement - https://www.anthropic.com/news/soc2-type2
8. ISO 42001 Certification - https://www.anthropic.com/news/iso-42001
9. Claude Code Security (Sandbox) - https://docs.anthropic.com/en/docs/claude-code/security

### 10.2 Google (Gemini CLI)

10. Google Cloud Security & Compliance - https://cloud.google.com/security/compliance
11. Google Cloud Data Processing Terms - https://cloud.google.com/terms/data-processing-terms
12. Gemini API Terms of Service - https://ai.google.dev/gemini-api/terms
13. Google AI Studio Privacy - https://ai.google.dev/gemini-api/docs/privacy
14. Gemini CLI GitHub Repository - https://github.com/google-gemini/gemini-cli
15. GeminiJack Vulnerability Research - https://www.trailofbits.com/research
16. Google Vulnerability Reward Program - https://bughunters.google.com/

### 10.3 OpenAI (ChatGPT / Codex)

17. OpenAI Security Portal - https://trust.openai.com/
18. OpenAI Enterprise Privacy - https://openai.com/enterprise-privacy
19. OpenAI API Data Usage Policies - https://openai.com/policies/api-data-usage-policies
20. OpenAI SOC 2 Compliance - https://openai.com/security
21. OpenAI Bug Bounty Program - https://bugcrowd.com/openai
22. ChatGPT Enterprise - https://openai.com/chatgpt/enterprise/
23. OpenAI Privacy Policy - https://openai.com/policies/privacy-policy
24. OpenAI ISO Certifications Announcement - https://openai.com/index/openai-iso-certifications

### 10.4 DeepSeek

25. DeepSeek Privacy Policy - https://www.deepseek.com/privacy
26. DeepSeek Terms of Use - https://www.deepseek.com/terms
27. Wiz Research: DeepSeek Database Exposure - https://www.wiz.io/blog/wiz-research-uncovers-exposed-deepseek-database-leak
28. NowSecure: DeepSeek iOS App Security - https://www.nowsecure.com/blog/deepseek-ios-app-security-assessment/
29. Unit 42: DeepSeek Jailbreak Research - https://unit42.paloaltonetworks.com/jailbreaking-deepseek/
30. China National Intelligence Law (2017) - https://www.chinalawtranslate.com/national-intelligence-law/
31. Italy DeepSeek Ban (Garante) - https://www.garanteprivacy.it/
32. Australia DeepSeek Government Ban - https://www.asd.gov.au/

### 10.5 GitHub Copilot (Microsoft)

33. GitHub Copilot Trust Center - https://resources.github.com/copilot-trust-center/
34. GitHub Security - https://github.com/security
35. GitHub Copilot Business Privacy - https://docs.github.com/en/copilot/overview-of-github-copilot/about-github-copilot-business
36. Microsoft DPA - https://www.microsoft.com/licensing/docs/view/Microsoft-Products-and-Services-Data-Protection-Addendum-DPA
37. Copilot IP Indemnity - https://learn.microsoft.com/en-us/legal/cognitive-services/openai/customer-copyright-commitment
38. GitHub Copilot Enterprise - https://docs.github.com/en/copilot/github-copilot-enterprise

### 10.6 Cursor AI

39. Cursor Privacy Policy - https://www.cursor.com/privacy
40. Cursor Security - https://www.cursor.com/security
41. Cursor SOC 2 Type II - https://www.cursor.com/blog/soc2
42. CamoLeak Vulnerability Research - https://www.pillar.security/blog/camoleak-exploiting-cursor-ais-agent-mode
43. Cursor Business - https://www.cursor.com/business

### 10.7 일반 참고

44. OWASP Top 10 for LLM Applications - https://owasp.org/www-project-top-10-for-large-language-model-applications/
45. NIST AI Risk Management Framework - https://www.nist.gov/artificial-intelligence/ai-risk-management-framework

---

> **면책 조항**: 본 보고서는 2026년 2월 12일 기준으로 공개적으로 확인 가능한 정보를 바탕으로 작성되었습니다. 각 서비스의 약관, 보안 인증, 정책은 수시로 변경될 수 있으므로, 기업 도입 전 최신 정보를 반드시 재확인하시기 바랍니다. 특히 계약 체결 시 해당 벤더의 최신 DPA, BAA, 서비스 약관을 직접 검토하시기를 권장합니다.

---

*작성: AI Agent Security Audit Team (CTO-Led)*
*PDCA Cycle: Plan → Do (5-Agent Parallel Research) → Check (Cross-validation) → Act (Report)*
