# Frontend Performance Checklist

프론트엔드 성능 최적화를 위한 실행 가능한 체크리스트입니다. Core Web Vitals 개선, 번들 최적화, 렌더링 성능 향상을 위한 구체적인 전략을 제공합니다.

## Table of Contents

1. [Core Web Vitals](#core-web-vitals)
2. [Bundle Size Optimization](#bundle-size-optimization)
3. [Rendering Performance](#rendering-performance)
4. [Image Optimization](#image-optimization)
5. [Network Optimization](#network-optimization)
6. [CSS Performance](#css-performance)
7. [Measurement Tools](#measurement-tools)
8. [Performance Budget Template](#performance-budget-template)
9. [Framework-Specific Optimization](#framework-specific-optimization)

## Core Web Vitals

Google의 Core Web Vitals는 사용자 경험을 측정하는 핵심 지표입니다.

### LCP (Largest Contentful Paint)

**타겟**: < 2.5초
**측정 대상**: 뷰포트 내 가장 큰 콘텐츠 요소가 렌더링되는 시간

**개선 전략**:

- [ ] **서버 응답 시간 개선 (TTFB < 600ms)**
  ```nginx
  # Nginx 예시
  gzip on;
  gzip_types text/plain text/css application/json application/javascript;
  http2_push_preload on;
  ```

- [ ] **중요 리소스 프리로드**
  ```html
  <link rel="preload" href="/hero-image.webp" as="image">
  <link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
  ```

- [ ] **렌더 블로킹 리소스 제거**
  ```html
  <!-- Bad -->
  <link rel="stylesheet" href="styles.css">

  <!-- Good: 중요 CSS만 인라인 -->
  <style>/* Critical CSS */</style>
  <link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  ```

- [ ] **이미지 최적화** (자세한 내용은 Image Optimization 섹션)
  - WebP/AVIF 포맷 사용
  - 적절한 크기로 제공
  - CDN 사용

- [ ] **클라이언트 사이드 렌더링 최소화**
  - SSR/SSG 고려 (Next.js, Nuxt.js)
  - 초기 HTML에 중요 콘텐츠 포함

**디버깅**:
```javascript
// LCP 요소 확인
new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP element:', lastEntry.element);
  console.log('LCP time:', lastEntry.renderTime || lastEntry.loadTime);
}).observe({ type: 'largest-contentful-paint', buffered: true });
```

### INP (Interaction to Next Paint)

**타겟**: < 200ms
**측정 대상**: 사용자 상호작용부터 다음 화면 업데이트까지의 시간

**개선 전략**:

- [ ] **JavaScript 실행 시간 단축**
  - 코드 분할 (Dynamic Import)
  - 불필요한 JavaScript 제거
  - Debounce/Throttle 적용

- [ ] **메인 스레드 차단 최소화**
  ```javascript
  // Bad: 동기 작업이 메인 스레드 차단
  function processLargeData(data) {
    return data.map(item => complexCalculation(item)); // 50ms 소요
  }

  // Good: Web Worker로 분리
  const worker = new Worker('worker.js');
  worker.postMessage(data);
  worker.onmessage = (e) => {
    const result = e.data;
  };
  ```

- [ ] **입력 딜레이 최소화**
  ```javascript
  // Bad: 무거운 이벤트 핸들러
  input.addEventListener('input', (e) => {
    expensiveSearch(e.target.value);
  });

  // Good: Debounce 적용
  import { debounce } from 'lodash-es';
  input.addEventListener('input', debounce((e) => {
    expensiveSearch(e.target.value);
  }, 300));
  ```

- [ ] **불필요한 리렌더링 방지** (Rendering Performance 섹션 참조)

- [ ] **requestIdleCallback 활용**
  ```javascript
  // 우선순위 낮은 작업 지연
  requestIdleCallback(() => {
    sendAnalytics();
  });
  ```

**측정**:
```javascript
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.duration > 200) {
      console.warn('Slow interaction detected:', entry);
    }
  }
}).observe({ type: 'event', buffered: true, durationThreshold: 100 });
```

### CLS (Cumulative Layout Shift)

**타겟**: < 0.1
**측정 대상**: 예기치 않은 레이아웃 이동의 누적 점수

**개선 전략**:

- [ ] **이미지/비디오에 명시적 크기 지정**
  ```html
  <!-- Bad -->
  <img src="hero.jpg" alt="Hero">

  <!-- Good -->
  <img src="hero.jpg" alt="Hero" width="1200" height="600">

  <!-- Better: aspect-ratio -->
  <img src="hero.jpg" alt="Hero" style="aspect-ratio: 1200/600; width: 100%;">
  ```

- [ ] **폰트 로딩 최적화**
  ```css
  /* font-display로 FOIT/FOUT 제어 */
  @font-face {
    font-family: 'Inter';
    src: url('/fonts/inter.woff2') format('woff2');
    font-display: swap; /* 또는 optional */
  }
  ```

  ```html
  <!-- 폰트 프리로드 -->
  <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
  ```

- [ ] **광고/임베드에 공간 예약**
  ```css
  .ad-container {
    min-height: 250px; /* 광고 로드 전 공간 확보 */
  }
  ```

- [ ] **동적 콘텐츠 삽입 위치 주의**
  ```javascript
  // Bad: 상단에 배너 동적 삽입
  document.body.insertBefore(banner, document.body.firstChild);

  // Good: 고정된 위치에 삽입
  document.getElementById('banner-slot').appendChild(banner);
  ```

- [ ] **애니메이션은 transform/opacity만 사용**
  ```css
  /* Bad: layout shift 발생 */
  .box {
    transition: height 0.3s;
  }

  /* Good: GPU 가속, layout shift 없음 */
  .box {
    transition: transform 0.3s;
  }
  ```

**측정**:
```javascript
let cls = 0;
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) {
      cls += entry.value;
      console.log('CLS:', cls, 'Element:', entry.sources);
    }
  }
}).observe({ type: 'layout-shift', buffered: true });
```

## Bundle Size Optimization

### Tree-Shaking

- [ ] **모듈 시스템 확인 (ES Modules 사용)**
  ```javascript
  // package.json
  {
    "sideEffects": false // 모든 파일이 사이드 이펙트 없음
    // 또는
    "sideEffects": ["*.css", "*.scss"] // CSS만 사이드 이펙트
  }
  ```

- [ ] **배럴 import 피하기**
  ```typescript
  // Bad: 전체 라이브러리 번들링 가능
  import { debounce } from 'lodash';

  // Good: 특정 함수만 임포트
  import debounce from 'lodash-es/debounce';
  ```

- [ ] **Import Cost 분석**
  - VS Code Extension: Import Cost
  - 각 import의 크기를 실시간으로 표시

### Dynamic Imports

- [ ] **라우트 기반 코드 분할**
  ```tsx
  // React
  const Dashboard = lazy(() => import('./pages/Dashboard'));

  <Suspense fallback={<Spinner />}>
    <Routes>
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  </Suspense>
  ```

  ```typescript
  // Vue
  const routes = [
    {
      path: '/dashboard',
      component: () => import('./pages/Dashboard.vue')
    }
  ];
  ```

- [ ] **조건부 로딩**
  ```typescript
  // 기능이 사용될 때만 로드
  button.addEventListener('click', async () => {
    const { default: Chart } = await import('chart.js');
    new Chart(ctx, config);
  });
  ```

- [ ] **below-the-fold 컴포넌트 지연 로딩**
  ```tsx
  const Comments = lazy(() => import('./Comments'));

  <IntersectionObserverWrapper>
    <Suspense fallback={<Skeleton />}>
      <Comments />
    </Suspense>
  </IntersectionObserverWrapper>
  ```

### Bundle Analysis

- [ ] **Webpack Bundle Analyzer 설정**
  ```javascript
  // webpack.config.js
  const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

  module.exports = {
    plugins: [
      new BundleAnalyzerPlugin({
        analyzerMode: 'static',
        openAnalyzer: false,
        reportFilename: 'bundle-report.html'
      })
    ]
  };
  ```

  ```bash
  # Vite
  npm run build -- --mode analyze
  ```

- [ ] **중복 의존성 확인**
  ```bash
  npm ls <package-name>
  # 또는
  yarn why <package-name>
  ```

- [ ] **큰 의존성 대체 검토**
  | 라이브러리 | 크기 | 대안 | 대안 크기 |
  |----------|------|------|----------|
  | moment.js | 67KB | date-fns | 13KB (필요한 함수만) |
  | lodash | 69KB | lodash-es | 24KB (tree-shakeable) |
  | axios | 13KB | fetch API | 0KB (네이티브) |

### CSS Optimization

- [ ] **사용하지 않는 CSS 제거**
  ```javascript
  // Tailwind CSS
  module.exports = {
    content: ['./src/**/*.{js,jsx,ts,tsx}'],
    // 사용된 클래스만 포함
  };
  ```

  ```javascript
  // PurgeCSS
  const purgecss = require('@fullhuman/postcss-purgecss');
  module.exports = {
    plugins: [
      purgecss({
        content: ['./src/**/*.html', './src/**/*.jsx']
      })
    ]
  };
  ```

- [ ] **CSS-in-JS 런타임 비용 고려**
  | 라이브러리 | 런타임 | 번들 크기 | 비고 |
  |----------|--------|----------|------|
  | styled-components | Yes | ~15KB | 런타임 스타일 생성 |
  | emotion | Yes | ~11KB | styled-components와 유사 |
  | Linaria | No | ~0KB | 빌드 타임 CSS 추출 |
  | vanilla-extract | No | ~0KB | 타입 세이프 CSS |

## Rendering Performance

### Virtualization

긴 리스트를 렌더링할 때 필수입니다.

- [ ] **react-virtual / vue-virtual-scroller 사용**
  ```tsx
  // React
  import { useVirtualizer } from '@tanstack/react-virtual';

  function VirtualList({ items }) {
    const parentRef = useRef<HTMLDivElement>(null);

    const virtualizer = useVirtualizer({
      count: items.length,
      getScrollElement: () => parentRef.current,
      estimateSize: () => 50,
    });

    return (
      <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
        <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
          {virtualizer.getVirtualItems().map((virtualItem) => (
            <div
              key={virtualItem.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              <Item item={items[virtualItem.index]} />
            </div>
          ))}
        </div>
      </div>
    );
  }
  ```

- [ ] **가상화 필요 기준**
  - 리스트 아이템 > 100개
  - 각 아이템이 복잡한 구조 (이미지, 여러 자식)

### Memoization

- [ ] **React.memo / Vue computed 적절히 사용**
  ```tsx
  // React
  const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
    // 복잡한 렌더링
    return <div>{/* ... */}</div>;
  }, (prevProps, nextProps) => {
    // 커스텀 비교 함수
    return prevProps.data.id === nextProps.data.id;
  });
  ```

  ```typescript
  // Vue
  const filteredItems = computed(() => {
    return items.value.filter(item => item.active);
  });
  ```

- [ ] **useMemo로 비싼 계산 메모이제이션**
  ```tsx
  const sortedItems = useMemo(() => {
    return [...items].sort((a, b) => a.price - b.price);
  }, [items]);
  ```

- [ ] **useCallback으로 함수 안정화**
  ```tsx
  const handleClick = useCallback((id: string) => {
    // 이벤트 핸들러
  }, [/* dependencies */]);

  return <MemoizedChild onClick={handleClick} />;
  ```

**주의**: 모든 것을 메모이제이션하지 마세요. 프로파일링 후 병목이 확인된 곳만 적용하세요.

### Avoiding Re-renders

- [ ] **새로운 객체/배열 참조 방지**
  ```tsx
  // Bad: 매 렌더링마다 새 객체
  <Child style={{ margin: 10 }} />

  // Good: 상수로 추출
  const childStyle = { margin: 10 };
  <Child style={childStyle} />
  ```

- [ ] **인라인 함수 주의**
  ```tsx
  // Bad: 매 렌더링마다 새 함수
  <Child onClick={() => handleClick(id)} />

  // Good: useCallback 또는 bind
  const handleChildClick = useCallback(() => handleClick(id), [id]);
  <Child onClick={handleChildClick} />
  ```

- [ ] **Context 값 메모이제이션**
  ```tsx
  const value = useMemo(() => ({
    user,
    login,
    logout
  }), [user]);

  <UserContext.Provider value={value}>
    {children}
  </UserContext.Provider>
  ```

### List Rendering

- [ ] **고유한 key 사용 (index 피하기)**
  ```tsx
  // Bad
  {items.map((item, index) => <Item key={index} {...item} />)}

  // Good
  {items.map((item) => <Item key={item.id} {...item} />)}
  ```

- [ ] **key로 리스트 업데이트 최적화**
  - React는 key로 요소를 추적하여 최소한의 DOM 조작만 수행

### Debouncing & Throttling

- [ ] **검색 입력 디바운스**
  ```tsx
  import { useDebouncedCallback } from 'use-debounce';

  const handleSearch = useDebouncedCallback((query: string) => {
    fetchResults(query);
  }, 300);

  <input onChange={(e) => handleSearch(e.target.value)} />
  ```

- [ ] **스크롤/리사이즈 이벤트 쓰로틀**
  ```javascript
  import { throttle } from 'lodash-es';

  window.addEventListener('scroll', throttle(() => {
    updateScrollPosition();
  }, 100));
  ```

### requestAnimationFrame

- [ ] **애니메이션은 RAF 사용**
  ```javascript
  function animate() {
    // 애니메이션 로직
    element.style.transform = `translateX(${x}px)`;

    requestAnimationFrame(animate);
  }

  requestAnimationFrame(animate);
  ```

### Web Workers

- [ ] **무거운 계산은 Web Worker로 분리**
  ```javascript
  // worker.js
  self.addEventListener('message', (e) => {
    const result = heavyComputation(e.data);
    self.postMessage(result);
  });

  // main.js
  const worker = new Worker('worker.js');
  worker.postMessage(largeData);
  worker.addEventListener('message', (e) => {
    console.log('Result:', e.data);
  });
  ```

**적합한 작업**:
- 이미지 처리
- 데이터 파싱/변환
- 암호화/복호화
- 복잡한 계산

## Image Optimization

### Format Selection

- [ ] **Next-gen 포맷 사용 (WebP, AVIF)**
  ```html
  <picture>
    <source type="image/avif" srcset="hero.avif">
    <source type="image/webp" srcset="hero.webp">
    <img src="hero.jpg" alt="Hero">
  </picture>
  ```

  | 포맷 | 브라우저 지원 | 압축률 | 추천 용도 |
  |------|------------|--------|----------|
  | AVIF | Modern (90%) | 최고 | 모든 이미지 |
  | WebP | 거의 모든 (97%) | 높음 | 폴백 포맷 |
  | JPEG | 100% | 중간 | 최종 폴백 |

### Responsive Images

- [ ] **srcset으로 디바이스별 이미지 제공**
  ```html
  <img
    src="image-800.jpg"
    srcset="
      image-400.jpg 400w,
      image-800.jpg 800w,
      image-1200.jpg 1200w
    "
    sizes="(max-width: 600px) 400px, (max-width: 1000px) 800px, 1200px"
    alt="Responsive image"
  >
  ```

- [ ] **art direction (picture 태그)**
  ```html
  <picture>
    <source media="(max-width: 600px)" srcset="mobile.jpg">
    <source media="(max-width: 1200px)" srcset="tablet.jpg">
    <img src="desktop.jpg" alt="Art direction example">
  </picture>
  ```

### Lazy Loading

- [ ] **네이티브 lazy loading**
  ```html
  <img src="image.jpg" loading="lazy" alt="Lazy loaded image">
  ```

- [ ] **Intersection Observer로 커스텀 구현**
  ```javascript
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        observer.unobserve(img);
      }
    });
  });

  document.querySelectorAll('img[data-src]').forEach(img => {
    observer.observe(img);
  });
  ```

### Sizing

- [ ] **이미지를 필요한 크기로만 제공**
  ```html
  <!-- Bad: 2000x1500 이미지를 400x300으로 표시 -->
  <img src="large.jpg" width="400" height="300">

  <!-- Good: 실제 표시 크기에 맞는 이미지 -->
  <img src="medium.jpg" width="400" height="300">
  ```

### CDN & Caching

- [ ] **이미지 CDN 사용 (Cloudinary, Imgix, Cloudflare Images)**
  ```html
  <!-- Cloudinary 예시 -->
  <img src="https://res.cloudinary.com/demo/image/upload/w_400,f_auto,q_auto/sample.jpg">
  ```

  자동으로 제공되는 기능:
  - 포맷 변환 (f_auto)
  - 품질 최적화 (q_auto)
  - 리사이징 (w_400)
  - 캐싱

### Placeholder

- [ ] **로딩 중 플레이스홀더 표시**
  ```tsx
  // LQIP (Low Quality Image Placeholder)
  <img
    src="image-full.jpg"
    style={{
      backgroundImage: 'url(data:image/jpeg;base64,/9j/4AAQ...)', // 작은 블러 이미지
      backgroundSize: 'cover'
    }}
  />

  // BlurHash
  import { Blurhash } from 'react-blurhash';
  <Blurhash
    hash="LEHV6nWB2yk8pyo0adR*.7kCMdnj"
    width={400}
    height={300}
  />
  ```

## Network Optimization

### API Response Caching

- [ ] **Stale-While-Revalidate 패턴**
  ```typescript
  // TanStack Query
  const { data } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    staleTime: 5 * 60 * 1000, // 5분간 fresh
    cacheTime: 10 * 60 * 1000, // 10분간 캐시 유지
  });
  ```

- [ ] **HTTP 캐시 헤더 설정**
  ```http
  Cache-Control: public, max-age=31536000, immutable  # 정적 자산
  Cache-Control: public, max-age=0, must-revalidate   # HTML
  Cache-Control: private, max-age=3600                # API 응답
  ```

### Resource Prefetching

- [ ] **중요 리소스 프리로드**
  ```html
  <link rel="preload" href="/critical.css" as="style">
  <link rel="preload" href="/hero.webp" as="image">
  ```

- [ ] **다음 페이지 프리페치**
  ```tsx
  // Next.js
  import Link from 'next/link';
  <Link href="/dashboard" prefetch>Dashboard</Link>

  // React Router
  import { Link } from 'react-router-dom';
  <Link to="/dashboard" onMouseEnter={() => preloadRoute('/dashboard')}>
  ```

- [ ] **DNS 프리페치**
  ```html
  <link rel="dns-prefetch" href="https://api.example.com">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  ```

### HTTP/2 & HTTP/3

- [ ] **HTTP/2 활성화**
  - 멀티플렉싱: 여러 요청을 동시에 처리
  - 서버 푸시: 필요한 리소스를 미리 전송
  - 헤더 압축

- [ ] **도메인 샤딩 제거**
  - HTTP/1.1에서는 유용했지만 HTTP/2에서는 역효과

### Compression

- [ ] **Gzip / Brotli 압축**
  ```nginx
  # Nginx
  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
  gzip_min_length 1000;

  brotli on;
  brotli_types text/plain text/css application/json application/javascript;
  ```

  | 포맷 | 압축률 | 브라우저 지원 |
  |------|--------|------------|
  | Brotli | ~20% 더 좋음 | Modern (95%) |
  | Gzip | 기본 | 100% |

### Service Worker

- [ ] **오프라인 캐싱**
  ```javascript
  // service-worker.js
  self.addEventListener('install', (event) => {
    event.waitUntil(
      caches.open('v1').then((cache) => {
        return cache.addAll([
          '/',
          '/styles.css',
          '/script.js',
          '/offline.html'
        ]);
      })
    );
  });

  self.addEventListener('fetch', (event) => {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      })
    );
  });
  ```

## CSS Performance

### Critical CSS

- [ ] **Above-the-fold CSS 인라인**
  ```html
  <head>
    <style>
      /* Critical CSS - 첫 화면에 필요한 스타일만 */
      body { margin: 0; font-family: sans-serif; }
      .header { height: 60px; background: #000; }
    </style>
    <link rel="preload" href="/styles.css" as="style" onload="this.rel='stylesheet'">
  </head>
  ```

  도구: Critical, Critters (Next.js 내장)

### CSS-in-JS Runtime Cost

- [ ] **런타임 비용 인지**
  | 라이브러리 | 런타임 오버헤드 | 권장 시나리오 |
  |----------|--------------|------------|
  | styled-components | 높음 | 소규모 앱, DX 우선 |
  | emotion | 중간 | 밸런스 |
  | Linaria | 없음 | 성능 중요, 빌드 타임 OK |
  | vanilla-extract | 없음 | 타입 세이프 + 성능 |

- [ ] **서버 사이드 스타일 추출**
  ```tsx
  // Next.js pages/_document.tsx
  import { ServerStyleSheet } from 'styled-components';

  export default class MyDocument extends Document {
    static async getInitialProps(ctx) {
      const sheet = new ServerStyleSheet();
      const originalRenderPage = ctx.renderPage;

      ctx.renderPage = () =>
        originalRenderPage({
          enhanceApp: (App) => (props) =>
            sheet.collectStyles(<App {...props} />),
        });

      const initialProps = await Document.getInitialProps(ctx);
      return {
        ...initialProps,
        styles: (
          <>
            {initialProps.styles}
            {sheet.getStyleElement()}
          </>
        ),
      };
    }
  }
  ```

### Expensive Selectors

- [ ] **복잡한 선택자 피하기**
  ```css
  /* Bad: 비싼 선택자 */
  * { margin: 0; }
  div > div > div > .nested { }
  [class*="col-"] { }

  /* Good: 단순한 선택자 */
  .container { margin: 0; }
  .nested { }
  .col { }
  ```

### CSS Containment

- [ ] **독립된 컴포넌트에 contain 적용**
  ```css
  .card {
    contain: layout paint; /* 레이아웃/페인트 범위 제한 */
  }

  .article {
    contain: content; /* layout + paint + style */
  }
  ```

### will-change

- [ ] **애니메이션 요소에 will-change (신중하게)**
  ```css
  .animated {
    will-change: transform; /* GPU 레이어 생성 */
  }

  /* 애니메이션 후 제거 */
  .animated:hover {
    transform: scale(1.1);
  }
  ```

  **주의**: 과도하게 사용 시 메모리 소비 증가

## Measurement Tools

### Lighthouse

**용도**: 전반적인 성능 점수, Core Web Vitals

```bash
# CLI
npm install -g lighthouse
lighthouse https://example.com --view

# CI/CD
lighthouse https://example.com --output json --output-path ./report.json
```

**CI/CD 통합**:
```yaml
# GitHub Actions
- name: Run Lighthouse
  uses: treosh/lighthouse-ci-action@v9
  with:
    urls: |
      https://example.com
      https://example.com/about
    budgetPath: ./budget.json
    uploadArtifacts: true
```

### Chrome DevTools Performance

**용도**: 런타임 프로파일링, 병목 지점 파악

1. DevTools > Performance 탭
2. 기록 시작 > 사용자 시나리오 수행 > 기록 중지
3. 분석:
   - Main 스레드에서 긴 작업 확인 (Long Task > 50ms)
   - 레이아웃/페인트 시간 확인
   - JavaScript 실행 시간 확인

### webpack-bundle-analyzer

**용도**: 번들 구성 분석

```bash
npm install --save-dev webpack-bundle-analyzer

# package.json
"scripts": {
  "analyze": "webpack --config webpack.config.js --profile --json > stats.json && webpack-bundle-analyzer stats.json"
}
```

### React Profiler

**용도**: React 컴포넌트 렌더링 시간

```tsx
import { Profiler } from 'react';

<Profiler id="App" onRender={(id, phase, actualDuration) => {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
}}>
  <App />
</Profiler>
```

React DevTools Profiler 탭에서 시각적 분석도 가능

### Vue Devtools

**용도**: Vue 컴포넌트 렌더링, 반응성 추적

- Performance 탭: 컴포넌트 렌더 시간
- Reactivity 탭: 어떤 데이터 변경이 리렌더링을 일으켰는지 추적

## Performance Budget Template

프로젝트에 맞게 조정하여 사용하세요.

| 자산 유형 | 예산 | 현재 | 상태 | 측정 방법 |
|----------|------|------|------|----------|
| **JavaScript (total)** | < 200KB gzipped | ? | ? | Bundle analyzer |
| **JavaScript (initial)** | < 100KB gzipped | ? | ? | Bundle analyzer |
| **CSS (total)** | < 50KB gzipped | ? | ? | Build output |
| **Images (per page)** | < 500KB | ? | ? | Network tab |
| **Web Fonts** | < 100KB | ? | ? | Network tab |
| **Total Page Weight** | < 1MB | ? | ? | Network tab |
| **LCP** | < 2.5s | ? | ? | Lighthouse, Field Data |
| **INP** | < 200ms | ? | ? | Lighthouse, Field Data |
| **CLS** | < 0.1 | ? | ? | Lighthouse, Field Data |
| **TTFB** | < 600ms | ? | ? | Network tab |
| **TTI (Time to Interactive)** | < 3.5s | ? | ? | Lighthouse |
| **Request Count** | < 50 | ? | ? | Network tab |

### CI/CD에서 강제하기

```json
// budget.json
{
  "budgets": [
    {
      "resourceSizes": [
        { "resourceType": "script", "budget": 200 },
        { "resourceType": "stylesheet", "budget": 50 },
        { "resourceType": "image", "budget": 500 }
      ],
      "timings": [
        { "metric": "interactive", "budget": 3500 },
        { "metric": "first-contentful-paint", "budget": 2000 }
      ]
    }
  ]
}
```

## Framework-Specific Optimization

### React

#### React.lazy + Suspense

```tsx
const Dashboard = lazy(() => import('./Dashboard'));

<Suspense fallback={<Spinner />}>
  <Dashboard />
</Suspense>
```

#### useMemo / useCallback

```tsx
// 비싼 계산 메모이제이션
const sortedData = useMemo(() => {
  return data.sort((a, b) => a.value - b.value);
}, [data]);

// 자식 컴포넌트에 전달하는 함수 안정화
const handleClick = useCallback(() => {
  console.log('clicked');
}, []);
```

#### React Compiler (React 19+)

React 19부터는 컴파일러가 자동으로 메모이제이션을 처리합니다.

```javascript
// babel.config.js
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      // options
    }]
  ]
};
```

수동 최적화가 줄어들지만 기본 원칙은 여전히 유효합니다.

### Vue

#### defineAsyncComponent

```typescript
const AsyncComponent = defineAsyncComponent(() =>
  import('./HeavyComponent.vue')
);
```

#### v-once

정적 콘텐츠는 한 번만 렌더링

```vue
<div v-once>
  <h1>{{ staticTitle }}</h1>
  <p>{{ staticDescription }}</p>
</div>
```

#### shallowRef / shallowReactive

큰 객체의 얕은 반응성

```typescript
// Bad: 깊은 반응성으로 인한 오버헤드
const largeObject = reactive({ /* 1000개 프로퍼티 */ });

// Good: 얕은 반응성
const largeObject = shallowReactive({ /* 1000개 프로퍼티 */ });
// 루트 레벨 변경만 추적
```

#### Computed vs Methods

```vue
<script setup>
// Bad: 매 렌더링마다 재계산
const fullName = () => firstName.value + ' ' + lastName.value;

// Good: 캐싱됨
const fullName = computed(() => firstName.value + ' ' + lastName.value);
</script>

<template>
  <!-- 렌더링될 때마다 함수 호출 -->
  <div>{{ fullName() }}</div>

  <!-- 의존성이 변경될 때만 재계산 -->
  <div>{{ fullName }}</div>
</template>
```

### Next.js

#### ISR (Incremental Static Regeneration)

```tsx
export async function getStaticProps() {
  const data = await fetchData();

  return {
    props: { data },
    revalidate: 60 // 60초마다 재생성
  };
}
```

#### Image Component

```tsx
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // LCP 이미지는 priority
  placeholder="blur"
  blurDataURL="data:image/..."
/>
```

자동으로 제공되는 기능:
- 반응형 이미지
- WebP 자동 변환
- Lazy loading
- 크기 최적화

#### Font Optimization

```tsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }) {
  return (
    <html className={inter.className}>
      <body>{children}</body>
    </html>
  );
}
```

자동으로 제공되는 기능:
- 폰트 파일 자동 최적화
- Layout shift 방지
- 프리로드

### Nuxt

#### Hybrid Rendering

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    '/': { prerender: true },           // 빌드 타임 생성
    '/blog/**': { swr: 3600 },          // ISR (1시간)
    '/admin/**': { ssr: false },        // CSR
    '/api/**': { cors: true }
  }
});
```

#### Auto Imports

```vue
<script setup>
// 자동 import, 트리 셰이킹됨
const route = useRoute();
const { data } = await useFetch('/api/users');
</script>
```

#### Nuxt Image

```vue
<template>
  <NuxtImg
    src="/hero.jpg"
    width="1200"
    height="600"
    format="webp"
    quality="80"
    loading="lazy"
  />
</template>
```

---

## Summary

이 체크리스트는 포괄적이지만 **모든 항목을 한 번에 적용할 필요는 없습니다**.

**우선순위**:
1. Core Web Vitals 측정 (Lighthouse, Field Data)
2. 가장 큰 영향을 주는 것부터 개선 (보통 이미지, JavaScript)
3. Performance Budget 설정 및 CI/CD 통합
4. 지속적인 모니터링

**기억하세요**:
- 추측하지 말고 측정하세요
- 사용자 경험에 가장 큰 영향을 주는 것부터 개선하세요
- 과도한 최적화는 가독성과 유지보수성을 해칠 수 있습니다
