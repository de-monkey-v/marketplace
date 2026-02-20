---
name: frontend-patterns
description: "프론트엔드 패턴 레퍼런스. 컴포넌트 설계 패턴, 상태 관리 전략, 번들/렌더링/Web Vitals 최적화 체크리스트를 제공합니다."
version: 1.0.0
---

# Frontend Patterns Reference

프론트엔드 개발을 위한 전문 레퍼런스 스킬입니다. 컴포넌트 설계 패턴, 상태 관리 전략, 성능 최적화 체크리스트를 제공하여 확장 가능하고 유지보수가 용이한 프론트엔드 애플리케이션을 구축할 수 있도록 돕습니다.

## Overview

이 스킬은 다음과 같은 상황에서 활용됩니다:

- 컴포넌트 아키텍처 설계 시 적절한 패턴 선택
- 상태 관리 전략 수립 및 구현
- 번들 크기 최적화 및 로딩 성능 개선
- Core Web Vitals 지표 개선
- 렌더링 성능 최적화
- 접근성 기준 준수

## Component Architecture Concepts

### Design Principles

현대 프론트엔드 개발에서 컴포넌트 설계는 다음 원칙을 따릅니다:

1. **Single Responsibility Principle**
   - 각 컴포넌트는 하나의 명확한 책임만 가져야 합니다
   - 책임이 여러 개라면 분리를 고려하세요

2. **Composition Over Inheritance**
   - 상속보다는 합성을 통해 기능을 조합합니다
   - 작은 컴포넌트를 조합하여 복잡한 UI를 구성합니다

3. **Controlled vs Uncontrolled Components**
   - Controlled: 부모가 상태를 완전히 제어 (권장)
   - Uncontrolled: 컴포넌트 내부에서 상태 관리 (특수한 경우만)

4. **Presentational vs Container Pattern**
   - Presentational: UI 렌더링에만 집중 (순수 함수)
   - Container: 비즈니스 로직, 데이터 페칭 담당

5. **Colocation**
   - 관련된 코드를 가까이 배치합니다
   - 컴포넌트와 테스트, 스타일, 스토리북을 같은 폴더에 위치시킵니다

### Component Patterns

주요 컴포넌트 패턴은 다음과 같습니다:

- **Compound Components**: 여러 하위 컴포넌트가 암묵적으로 상태를 공유
- **Render Props / Slots**: 유연한 렌더링 제어를 위한 함수 전달
- **Higher-Order Components**: 횡단 관심사 처리 (React에서는 Hooks 선호)
- **Custom Hooks / Composables**: 재사용 가능한 상태 로직 추출
- **Provider Pattern**: Context API를 활용한 전역 상태 공유
- **Polymorphic Components**: 동적 엘리먼트 렌더링 (`as` prop)

자세한 내용은 `references/component-patterns.md`를 참조하세요.

## State Management Overview

### State의 종류

프론트엔드 애플리케이션의 상태는 크게 네 가지로 분류됩니다:

1. **Server State** (서버 데이터)
   - API로부터 받아온 데이터
   - 캐싱, 동기화, 재검증이 필요
   - 권장 도구: TanStack Query, SWR, RTK Query

2. **Client State** (클라이언트 전역 상태)
   - 애플리케이션 전역에서 공유되는 상태
   - 권장 도구: Zustand, Pinia, Jotai

3. **UI State** (로컬 UI 상태)
   - 특정 컴포넌트에만 필요한 상태
   - 권장 도구: useState, ref, computed

4. **URL State** (URL 상태)
   - 검색 파라미터, 경로 파라미터로 관리되는 상태
   - 권장 도구: Router의 params/search

### Decision Matrix

| 시나리오 | 추천 솔루션 | 비고 |
|---------|-----------|------|
| 버튼 토글, 모달 open/close | useState / ref | 로컬 UI 상태 |
| 형제 컴포넌트 간 공유 | Lift state up | 부모로 상태 끌어올리기 |
| 전역 앱 설정 (테마, 언어) | Store (Zustand/Pinia) | 글로벌 클라이언트 상태 |
| API 데이터 | TanStack Query / SWR | 서버 상태 |
| 검색 필터, 페이지네이션 | URL params | 공유 가능한 상태 |
| 폼 입력 | React Hook Form / VeeValidate | 복잡한 검증 필요 시 |

자세한 패턴은 `references/component-patterns.md`의 State Management 섹션을 참조하세요.

## Performance Optimization

### Core Web Vitals

Google의 Core Web Vitals는 사용자 경험을 측정하는 핵심 지표입니다:

- **LCP (Largest Contentful Paint)**: < 2.5초
  - 가장 큰 콘텐츠가 화면에 렌더링되는 시간
  - 개선: 이미지 최적화, 서버 응답 시간 단축, 리소스 우선순위 조정

- **INP (Interaction to Next Paint)**: < 200ms
  - 사용자 인터랙션부터 다음 페인트까지의 시간
  - 개선: JavaScript 실행 시간 단축, 메인 스레드 차단 최소화

- **CLS (Cumulative Layout Shift)**: < 0.1
  - 레이아웃이 예기치 않게 이동하는 정도
  - 개선: 이미지/광고에 명시적 크기 지정, 폰트 로딩 최적화

### Optimization Strategies

1. **Bundle Size Optimization**
   - Tree-shaking 활성화
   - 동적 import로 코드 분할
   - 배럴 import 대신 구체적 import 사용

2. **Rendering Performance**
   - 긴 리스트는 가상화 (react-virtual, vue-virtual-scroller)
   - 적절한 메모이제이션 (React.memo, useMemo, computed)
   - 불필요한 재렌더링 방지

3. **Network Optimization**
   - API 응답 캐싱 (stale-while-revalidate)
   - 중요 리소스 프리페칭
   - 압축 활성화 (gzip/brotli)

4. **Image Optimization**
   - Next-gen 포맷 사용 (WebP, AVIF)
   - 반응형 이미지 (srcset)
   - Lazy loading

자세한 체크리스트는 `references/performance-checklist.md`를 참조하세요.

## Reference Files

### component-patterns.md

컴포넌트 설계 패턴과 상태 관리 전략에 대한 상세 가이드:

- **Component Design Principles**: 단일 책임, 합성, Colocation 등
- **Component Patterns**: Compound, Render Props, HOC, Hooks/Composables, Provider, Polymorphic
- **State Management Decision Matrix**: 시나리오별 최적 솔루션
- **State Management Patterns**: 서버 상태, 클라이언트 상태, 폼 상태, URL 상태
- **Component File Structure**: 표준 폴더 구조
- **Accessibility Fundamentals**: 시맨틱 HTML, ARIA, 키보드 내비게이션
- **Anti-Patterns**: 피해야 할 패턴과 해결책

### performance-checklist.md

프론트엔드 성능 최적화를 위한 실행 가능한 체크리스트:

- **Core Web Vitals**: LCP, INP, CLS 타겟과 개선 방법
- **Bundle Size Optimization**: Tree-shaking, 동적 import, 의존성 분석
- **Rendering Performance**: 가상화, 메모이제이션, 디바운싱
- **Image Optimization**: 포맷, 반응형, Lazy loading
- **Network Optimization**: 캐싱, 프리페칭, 압축
- **CSS Performance**: Critical CSS, CSS-in-JS 최적화
- **Measurement Tools**: Lighthouse, DevTools, Bundle Analyzer
- **Performance Budget Template**: 자산별 성능 예산 템플릿
- **Framework-Specific Optimization**: React, Vue, Next.js, Nuxt 최적화 팁

## Usage Examples

### Example 1: 컴포넌트 패턴 선택

**상황**: Select 드롭다운 컴포넌트를 만들어야 하는데, 내부 옵션을 유연하게 커스터마이징할 수 있어야 합니다.

**해결책**: Compound Components 패턴 사용

```tsx
// references/component-patterns.md의 Compound Components 섹션 참조
<Select>
  <Select.Trigger>Choose...</Select.Trigger>
  <Select.Options>
    <Select.Option value="a">Option A</Select.Option>
    <Select.Option value="b">Option B</Select.Option>
  </Select.Options>
</Select>
```

### Example 2: 상태 관리 선택

**상황**: 사용자 프로필 데이터를 여러 페이지에서 사용해야 합니다.

**해결책**:
- 데이터는 API에서 오므로 Server State → TanStack Query 사용
- 인증 토큰은 Client State → Zustand/Pinia 사용

`references/component-patterns.md`의 State Management Decision Matrix를 참조하세요.

### Example 3: LCP 개선

**상황**: Lighthouse에서 LCP가 4.5초로 측정되어 개선이 필요합니다.

**해결책**: `references/performance-checklist.md`의 Image Optimization 체크리스트 확인
- [ ] 히어로 이미지를 WebP로 변환
- [ ] 반응형 이미지 srcset 적용
- [ ] 중요 이미지를 프리로드
- [ ] CDN 사용

## Related Agents

이 스킬은 다음 에이전트들과 함께 사용됩니다:

### 프레임워크 전문가
- **frontend**: 일반 프론트엔드 개발 및 아키텍처
- **react-expert**: React 생태계 전문 (Hooks, Context, React 19+)
- **vue-expert**: Vue.js 전문 (Composition API, Reactivity, Vue 3)
- **nextjs-expert**: Next.js 전문 (SSR, ISR, App Router)
- **nuxt-expert**: Nuxt.js 전문 (Universal Rendering, Modules)

### 아키텍처 및 디자인
- **ui-architect**: UI 컴포넌트 시스템 설계, 디자인 시스템 구축
- **state-designer**: 복잡한 상태 관리 아키텍처 설계
- **css-architect**: CSS 아키텍처, 스타일 시스템 설계

### 품질 및 최적화
- **a11y-auditor**: 접근성 감사 및 WCAG 준수 검증
- **fe-performance**: 프론트엔드 성능 프로파일링 및 최적화
- **fe-tester**: 프론트엔드 테스팅 전략 (Unit, Integration, E2E)

### 전문 영역
- **i18n-specialist**: 국제화(i18n) 및 다국어 지원 구현

## Best Practices

### 1. 패턴 선택 시 고려사항

- **복잡도**: 간단한 문제에 복잡한 패턴을 사용하지 마세요
- **팀 숙련도**: 팀이 이해하고 유지보수할 수 있는 패턴을 선택하세요
- **성능**: 패턴의 런타임 비용을 고려하세요 (특히 렌더 프롭, HOC)
- **타입 안정성**: TypeScript를 사용한다면 타입 추론이 잘 되는 패턴을 선호하세요

### 2. 상태 관리 원칙

- **가장 가까운 곳에 배치**: 상태는 가능한 한 사용처 가까이에 배치하세요
- **Server vs Client 분리**: 서버 데이터와 클라이언트 상태를 명확히 구분하세요
- **단일 진실 공급원**: 같은 데이터를 여러 곳에 중복 저장하지 마세요
- **파생 상태 최소화**: 계산 가능한 값은 저장하지 말고 계산하세요

### 3. 성능 최적화 접근법

- **측정 우선**: 추측하지 말고 실제 성능을 측정하세요
- **중요한 것부터**: 사용자 경험에 가장 큰 영향을 주는 것부터 개선하세요
- **과도한 최적화 경계**: 가독성과 유지보수성을 희생하지 마세요
- **성능 예산 설정**: 명확한 목표를 설정하고 CI/CD에서 모니터링하세요

## Common Pitfalls

### 1. 컴포넌트 설계

- **거대한 컴포넌트**: 200줄 이상의 컴포넌트는 분리를 고려하세요
- **Prop Drilling**: 3단계 이상 prop을 전달한다면 Context나 Store를 고려하세요
- **과도한 추상화**: YAGNI 원칙 - 필요할 때 추상화하세요

### 2. 상태 관리

- **전역 상태 남용**: 모든 상태를 Store에 넣지 마세요
- **불필요한 리렌더링**: 객체/배열 참조를 매번 새로 생성하지 마세요
- **복잡한 파생 상태**: 단순하게 유지하세요, 복잡하면 분리하세요

### 3. 성능 최적화

- **조기 최적화**: 문제가 있을 때 최적화하세요
- **과도한 메모이제이션**: 모든 것을 memo/useMemo로 감싸지 마세요
- **번들 분석 누락**: 추측하지 말고 번들 분석기를 사용하세요

## Troubleshooting

### 컴포넌트 재렌더링 문제

1. React DevTools Profiler 또는 Vue Devtools에서 렌더링 기록
2. 불필요한 재렌더링 원인 파악:
   - 새로운 객체/배열 참조
   - 인라인 함수 생성
   - 부모 컴포넌트 재렌더링
3. `references/component-patterns.md`의 Anti-Patterns 섹션 참조

### LCP가 느린 경우

1. Lighthouse에서 LCP 요소 확인
2. `references/performance-checklist.md`의 Image Optimization 체크리스트 실행
3. 서버 응답 시간 확인 (TTFB < 600ms)
4. 중요 리소스 프리로드 설정

### 번들 크기가 큰 경우

1. webpack-bundle-analyzer 실행
2. `references/performance-checklist.md`의 Bundle Size Optimization 체크리스트 실행
3. 큰 의존성 확인 및 대안 검토
4. 동적 import로 코드 분할

## Conclusion

이 스킬은 프론트엔드 개발의 핵심 패턴과 최적화 전략을 제공합니다. 실제 프로젝트에 적용할 때는:

1. **컨텍스트 이해**: 프로젝트의 규모, 팀 구성, 기술 스택을 고려하세요
2. **점진적 적용**: 한 번에 모든 것을 바꾸려 하지 말고 점진적으로 개선하세요
3. **측정과 검증**: 변경 사항의 효과를 측정하고 검증하세요
4. **팀과 공유**: 패턴과 원칙을 팀과 공유하고 합의하세요

관련 에이전트들과 협력하여 더 나은 프론트엔드 애플리케이션을 구축하세요.
