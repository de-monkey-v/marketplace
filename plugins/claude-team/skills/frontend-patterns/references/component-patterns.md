# Component Patterns Reference

프론트엔드 컴포넌트 설계 패턴과 상태 관리 전략에 대한 상세 가이드입니다.

## Table of Contents

1. [Component Design Principles](#component-design-principles)
2. [Component Patterns](#component-patterns)
3. [State Management Decision Matrix](#state-management-decision-matrix)
4. [State Management Patterns](#state-management-patterns)
5. [Component File Structure](#component-file-structure)
6. [Accessibility Fundamentals](#accessibility-fundamentals)
7. [Anti-Patterns](#anti-patterns)

## Component Design Principles

### 1. Single Responsibility Principle

각 컴포넌트는 하나의 명확한 책임만 가져야 합니다.

```tsx
// Bad: 너무 많은 책임
function UserDashboard() {
  // 데이터 페칭, 폼 처리, 차트 렌더링, 테이블 렌더링...
  // 500줄의 코드
}

// Good: 책임 분리
function UserDashboard() {
  return (
    <>
      <UserProfile />
      <UserStats />
      <UserActivityChart />
      <UserRecentOrders />
    </>
  );
}
```

**판단 기준**:
- 컴포넌트 이름으로 명확하게 설명 가능한가?
- 변경 사유가 여러 개인가? (데이터 구조 변경, UI 변경, 비즈니스 로직 변경)
- 100줄을 초과하는가? (경험적 기준)

### 2. Composition Over Inheritance

상속보다 합성을 사용하여 기능을 조합합니다.

```tsx
// Bad: 상속 (React에서는 권장하지 않음)
class FancyButton extends Button {
  // ...
}

// Good: 합성
function FancyButton(props) {
  return (
    <Button className="fancy" {...props}>
      <Icon />
      {props.children}
    </Button>
  );
}
```

**장점**:
- 유연성: 런타임에 동작 변경 가능
- 명시성: 의존성이 명확함
- 재사용성: 작은 조각들을 다양하게 조합

### 3. Controlled vs Uncontrolled Components

**Controlled (권장)**:
```tsx
function ControlledInput() {
  const [value, setValue] = useState('');

  return (
    <input
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  );
}
```

**Uncontrolled (특수한 경우만)**:
```tsx
function UncontrolledInput() {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    console.log(inputRef.current?.value);
  };

  return <input ref={inputRef} />;
}
```

**언제 Uncontrolled를 사용하나**:
- 파일 입력 (`<input type="file">`)
- 써드파티 라이브러리와 통합 시
- 성능이 매우 중요하고 리렌더링을 피해야 할 때

### 4. Presentational vs Container (Smart vs Dumb)

**Presentational Component**:
```tsx
// Props만 받아서 UI 렌더링
function UserCard({ user, onEdit }: UserCardProps) {
  return (
    <div className="user-card">
      <img src={user.avatar} alt={user.name} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <button onClick={onEdit}>Edit</button>
    </div>
  );
}
```

**Container Component**:
```tsx
// 비즈니스 로직, 데이터 페칭
function UserCardContainer({ userId }: { userId: string }) {
  const { data: user } = useQuery(['user', userId], fetchUser);
  const mutation = useMutation(updateUser);

  const handleEdit = () => {
    // 비즈니스 로직
    mutation.mutate({ id: userId, ... });
  };

  if (!user) return <Skeleton />;

  return <UserCard user={user} onEdit={handleEdit} />;
}
```

**분리의 장점**:
- Presentational은 Storybook에서 쉽게 테스트
- 재사용성 향상
- 관심사 분리

### 5. Colocation

관련된 코드를 가까이 배치하여 응집도를 높입니다.

```
features/
  user-profile/
    UserProfile.tsx          # 컴포넌트
    UserProfile.test.tsx     # 테스트
    UserProfile.stories.tsx  # Storybook
    UserProfile.module.css   # 스타일
    useUserProfile.ts        # 커스텀 훅
    utils.ts                 # 헬퍼 함수
    types.ts                 # 타입 정의
    index.ts                 # 공개 API
```

**원칙**:
- 함께 변경되는 것은 함께 위치
- 폴더 구조는 기능 중심으로 (기술 스택 중심 X)
- index.ts로 공개 API 제한

## Component Patterns

### 1. Compound Components

여러 하위 컴포넌트가 암묵적으로 상태를 공유하는 패턴입니다.

**사용 시기**: 다중 파트 UI (Select, Tabs, Accordion)에서 부모-자식 간 상태 공유가 필요할 때

**React 구현**:
```tsx
// Context로 상태 공유
const SelectContext = createContext<SelectContextValue | null>(null);

function Select({ children, value, onChange }: SelectProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <SelectContext.Provider value={{ value, onChange, isOpen, setIsOpen }}>
      <div className="select">{children}</div>
    </SelectContext.Provider>
  );
}

function Trigger({ children }: TriggerProps) {
  const context = useContext(SelectContext);
  if (!context) throw new Error('Trigger must be used within Select');

  return (
    <button onClick={() => context.setIsOpen(!context.isOpen)}>
      {children}
    </button>
  );
}

function Options({ children }: OptionsProps) {
  const context = useContext(SelectContext);
  if (!context?.isOpen) return null;

  return <div className="options">{children}</div>;
}

function Option({ value, children }: OptionProps) {
  const context = useContext(SelectContext);

  return (
    <button
      onClick={() => {
        context.onChange(value);
        context.setIsOpen(false);
      }}
      className={context.value === value ? 'selected' : ''}
    >
      {children}
    </button>
  );
}

// 네임스페이스 패턴으로 그룹화
Select.Trigger = Trigger;
Select.Options = Options;
Select.Option = Option;

// 사용
<Select value={selected} onChange={setSelected}>
  <Select.Trigger>Choose...</Select.Trigger>
  <Select.Options>
    <Select.Option value="a">Option A</Select.Option>
    <Select.Option value="b">Option B</Select.Option>
  </Select.Options>
</Select>
```

**Vue 3 구현**:
```vue
<!-- Select.vue -->
<script setup lang="ts">
import { provide, ref } from 'vue';

const props = defineProps<{ modelValue: string }>();
const emit = defineEmits<{ 'update:modelValue': [string] }>();

const isOpen = ref(false);

provide('select', {
  value: computed(() => props.modelValue),
  isOpen,
  select: (value: string) => {
    emit('update:modelValue', value);
    isOpen.value = false;
  },
  toggle: () => { isOpen.value = !isOpen.value; }
});
</script>

<template>
  <div class="select">
    <slot />
  </div>
</template>

<!-- SelectTrigger.vue -->
<script setup lang="ts">
import { inject } from 'vue';
const select = inject('select');
</script>

<template>
  <button @click="select.toggle">
    <slot />
  </button>
</template>
```

**장점**:
- 유연한 마크업 구조
- 암묵적 상태 공유로 prop drilling 방지
- API가 직관적

**단점**:
- Context 오버헤드
- 컴포넌트 구조가 강제됨

### 2. Render Props / Slots

렌더링 로직을 외부에서 주입받는 패턴입니다.

**사용 시기**: 컴포넌트의 로직은 재사용하되 렌더링은 유연하게 변경해야 할 때

**React - Render Props**:
```tsx
function MouseTracker({ render }: { render: (pos: Point) => ReactNode }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMove);
    return () => window.removeEventListener('mousemove', handleMove);
  }, []);

  return <>{render(position)}</>;
}

// 사용
<MouseTracker
  render={({ x, y }) => (
    <div>Mouse at {x}, {y}</div>
  )}
/>
```

**Vue - Scoped Slots**:
```vue
<!-- DataFetcher.vue -->
<script setup lang="ts">
const { data, loading, error } = useFetch(props.url);
</script>

<template>
  <div>
    <slot v-if="loading" name="loading" />
    <slot v-else-if="error" name="error" :error="error" />
    <slot v-else :data="data" />
  </div>
</template>

<!-- 사용 -->
<DataFetcher url="/api/users">
  <template #loading>Loading...</template>
  <template #error="{ error }">Error: {{ error.message }}</template>
  <template #default="{ data }">
    <UserList :users="data" />
  </template>
</DataFetcher>
```

**Modern React - Children as Function**:
```tsx
function DataFetcher({ url, children }: DataFetcherProps) {
  const { data, loading, error } = useQuery(url);

  return <>{children({ data, loading, error })}</>;
}

// 사용
<DataFetcher url="/api/users">
  {({ data, loading, error }) => {
    if (loading) return <Spinner />;
    if (error) return <Error error={error} />;
    return <UserList users={data} />;
  }}
</DataFetcher>
```

### 3. Higher-Order Components (HOC)

컴포넌트를 받아서 강화된 컴포넌트를 반환하는 함수입니다.

**사용 시기**: 횡단 관심사 (인증, 로깅, 분석) 처리

**주의**: React에서는 Hooks로 대체 가능하며, Hooks가 더 권장됨

```tsx
// HOC 방식 (Legacy)
function withAuth<P extends object>(Component: ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { user, loading } = useAuth();

    if (loading) return <Spinner />;
    if (!user) return <Navigate to="/login" />;

    return <Component {...props} user={user} />;
  };
}

const ProtectedPage = withAuth(Dashboard);

// Hooks 방식 (권장)
function Dashboard() {
  const user = useRequireAuth(); // 내부에서 리다이렉트 처리

  return <div>Welcome, {user.name}</div>;
}
```

**HOC가 여전히 유용한 경우**:
- 레거시 클래스 컴포넌트
- React DevTools에서 명확한 계층 구조 표시
- 여러 컴포넌트에 동일한 props 주입

### 4. Custom Hooks / Composables

재사용 가능한 상태 로직을 추출하는 패턴입니다.

**사용 시기**: 여러 컴포넌트에서 동일한 상태 로직을 사용할 때

**React - Custom Hooks**:
```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

// 사용
function SearchBar() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);

  const { data } = useQuery(['search', debouncedSearch], () =>
    fetchResults(debouncedSearch)
  );

  return <input value={search} onChange={(e) => setSearch(e.target.value)} />;
}
```

**Vue 3 - Composables**:
```typescript
export function useDebounce<T>(value: Ref<T>, delay: number): Ref<T> {
  const debouncedValue = ref(value.value) as Ref<T>;

  watch(value, (newValue) => {
    const handler = setTimeout(() => {
      debouncedValue.value = newValue;
    }, delay);

    onUnmounted(() => clearTimeout(handler));
  });

  return debouncedValue;
}

// 사용
const search = ref('');
const debouncedSearch = useDebounce(search, 300);

const { data } = useQuery(['search', debouncedSearch], () =>
  fetchResults(debouncedSearch.value)
);
```

**복잡한 예제 - useInfiniteScroll**:
```tsx
function useInfiniteScroll(callback: () => void, threshold = 100) {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useCallback((node: HTMLElement | null) => {
    if (observerRef.current) observerRef.current.disconnect();

    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        callback();
      }
    }, { rootMargin: `${threshold}px` });

    if (node) observerRef.current.observe(node);
  }, [callback, threshold]);

  return loadMoreRef;
}

// 사용
function UserList() {
  const { data, fetchNextPage, hasNextPage } = useInfiniteQuery(...);
  const loadMoreRef = useInfiniteScroll(() => {
    if (hasNextPage) fetchNextPage();
  });

  return (
    <div>
      {data.pages.map(page => page.users.map(user => <UserCard key={user.id} user={user} />))}
      {hasNextPage && <div ref={loadMoreRef}>Loading...</div>}
    </div>
  );
}
```

### 5. Provider Pattern

Context API를 활용하여 전역 상태를 공유하는 패턴입니다.

**사용 시기**: 깊은 prop drilling을 피하고 싶을 때, 테마/언어/인증 등 전역 설정

**React**:
```tsx
// ThemeContext.tsx
const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  const value = useMemo(() => ({ theme, toggleTheme }), [theme, toggleTheme]);

  return (
    <ThemeContext.Provider value={value}>
      <div className={theme}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// 사용
function App() {
  return (
    <ThemeProvider>
      <Header />
      <Main />
    </ThemeProvider>
  );
}

function Header() {
  const { theme, toggleTheme } = useTheme();
  return <button onClick={toggleTheme}>Toggle to {theme === 'light' ? 'dark' : 'light'}</button>;
}
```

**Vue 3 - Provide/Inject**:
```typescript
// useTheme.ts
const ThemeSymbol = Symbol('theme');

export function provideTheme() {
  const theme = ref<'light' | 'dark'>('light');
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light';
  };

  provide(ThemeSymbol, { theme: readonly(theme), toggleTheme });
}

export function useTheme() {
  const theme = inject(ThemeSymbol);
  if (!theme) {
    throw new Error('useTheme must be used within a theme provider');
  }
  return theme;
}
```

**최적화 팁**:
- Provider 값은 `useMemo`로 메모이제이션
- 콜백은 `useCallback`으로 안정화
- 컨텍스트를 작게 유지 (필요시 여러 개로 분리)

### 6. Polymorphic Components

동적으로 렌더링할 엘리먼트를 선택할 수 있는 컴포넌트입니다.

**사용 시기**: 같은 스타일/동작이지만 다른 HTML 요소로 렌더링해야 할 때

```tsx
type AsProp<C extends React.ElementType> = {
  as?: C;
};

type PropsToOmit<C extends React.ElementType, P> = keyof (AsProp<C> & P);

type PolymorphicComponentProp<
  C extends React.ElementType,
  Props = {}
> = React.PropsWithChildren<Props & AsProp<C>> &
  Omit<React.ComponentPropsWithoutRef<C>, PropsToOmit<C, Props>>;

type ButtonProps<C extends React.ElementType> = PolymorphicComponentProp<
  C,
  { variant?: 'primary' | 'secondary' }
>;

function Button<C extends React.ElementType = 'button'>({
  as,
  variant = 'primary',
  children,
  ...restProps
}: ButtonProps<C>) {
  const Component = as || 'button';

  return (
    <Component className={`btn btn-${variant}`} {...restProps}>
      {children}
    </Component>
  );
}

// 사용
<Button>Default button</Button>
<Button as="a" href="/home">Link styled as button</Button>
<Button as={Link} to="/about">React Router Link</Button>
```

## State Management Decision Matrix

| 시나리오 | 추천 솔루션 | 프레임워크 | 비고 |
|---------|-----------|-----------|------|
| 토글, 모달 open/close | `useState` / `ref` | React / Vue | 로컬 UI 상태 |
| 폼 입력 (간단) | `useState` / `ref` | React / Vue | 단일 컴포넌트 |
| 폼 입력 (복잡, 검증) | React Hook Form / VeeValidate | React / Vue | 의존성 추가 가치 |
| 형제 컴포넌트 간 공유 | Lift state up | All | 부모로 상태 끌어올리기 |
| 깊은 prop drilling | Context / Provide | React / Vue | 3단계 이상 시 고려 |
| 전역 앱 설정 (테마, 언어) | Zustand / Pinia | React / Vue | 글로벌 클라이언트 상태 |
| 복잡한 전역 상태 | Redux Toolkit / Pinia | React / Vue | DevTools, 미들웨어 필요 시 |
| API 데이터 (CRUD) | TanStack Query / SWR | All | 캐싱, 재검증 자동화 |
| 실시간 데이터 (WebSocket) | TanStack Query + subscription | All | 서버 상태 + 리얼타임 |
| 검색 필터, 페이지네이션 | URL params (useSearchParams) | All | 공유 가능, 북마크 가능 |
| 라우트 상태 | Router params | All | URL 기반 상태 |
| 로컬 스토리지 동기화 | Custom hook + localStorage | All | `useLocalStorage` |
| 복잡한 상태 머신 | XState | All | 명시적 상태 전이 필요 시 |

## State Management Patterns

### 1. Server State (TanStack Query)

서버 데이터는 클라이언트 상태와 다르게 관리해야 합니다.

**핵심 개념**:
- **Query Key**: 데이터를 고유하게 식별
- **Stale While Revalidate**: 오래된 데이터를 보여주면서 백그라운드에서 갱신
- **Automatic Refetching**: 포커스, 재연결 시 자동 갱신

```tsx
// 기본 사용
const { data, isLoading, error } = useQuery({
  queryKey: ['users', userId],
  queryFn: () => fetchUser(userId),
  staleTime: 5 * 60 * 1000, // 5분간 fresh
  cacheTime: 10 * 60 * 1000, // 10분간 캐시 유지
});

// Mutation
const mutation = useMutation({
  mutationFn: updateUser,
  onSuccess: () => {
    // 관련 쿼리 무효화
    queryClient.invalidateQueries({ queryKey: ['users'] });
  },
});

// Optimistic Update
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    await queryClient.cancelQueries({ queryKey: ['todos'] });
    const previousTodos = queryClient.getQueryData(['todos']);

    queryClient.setQueryData(['todos'], (old) => [...old, newTodo]);

    return { previousTodos };
  },
  onError: (err, newTodo, context) => {
    queryClient.setQueryData(['todos'], context.previousTodos);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] });
  },
});
```

### 2. Client State (Zustand / Pinia)

클라이언트 전역 상태 관리

**Zustand (React)**:
```tsx
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface UserStore {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const useUserStore = create<UserStore>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        token: null,
        login: async (email, password) => {
          const { user, token } = await api.login(email, password);
          set({ user, token });
        },
        logout: () => set({ user: null, token: null }),
      }),
      { name: 'user-storage' }
    )
  )
);

// 사용
function Header() {
  const user = useUserStore((state) => state.user);
  const logout = useUserStore((state) => state.logout);

  return user ? <button onClick={logout}>Logout</button> : <LoginButton />;
}
```

**Pinia (Vue)**:
```typescript
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);

  const isAuthenticated = computed(() => !!user.value);

  async function login(email: string, password: string) {
    const response = await api.login(email, password);
    user.value = response.user;
    token.value = response.token;
  }

  function logout() {
    user.value = null;
    token.value = null;
  }

  return { user, token, isAuthenticated, login, logout };
});
```

### 3. Form State

**React Hook Form**:
```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormData = z.infer<typeof schema>;

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}

      <input type="password" {...register('password')} />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit">Login</button>
    </form>
  );
}
```

### 4. URL State

```tsx
import { useSearchParams } from 'react-router-dom';

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();

  const page = parseInt(searchParams.get('page') || '1');
  const category = searchParams.get('category') || 'all';

  const { data } = useQuery({
    queryKey: ['products', { page, category }],
    queryFn: () => fetchProducts({ page, category }),
  });

  return (
    <div>
      <select
        value={category}
        onChange={(e) => setSearchParams({ category: e.target.value, page: '1' })}
      >
        <option value="all">All</option>
        <option value="electronics">Electronics</option>
      </select>

      <ProductGrid products={data.products} />

      <Pagination
        currentPage={page}
        totalPages={data.totalPages}
        onPageChange={(p) => setSearchParams({ category, page: p.toString() })}
      />
    </div>
  );
}
```

## Component File Structure

### 표준 폴더 구조

```
src/
  components/           # 재사용 가능한 공통 컴포넌트
    Button/
      Button.tsx
      Button.test.tsx
      Button.stories.tsx
      Button.module.css
      index.ts
  features/            # 기능별 컴포넌트
    user-profile/
      components/      # 기능 전용 컴포넌트
        UserAvatar.tsx
        UserStats.tsx
      UserProfile.tsx
      UserProfile.test.tsx
      useUserProfile.ts
      api.ts
      types.ts
      index.ts
  pages/              # 라우트 페이지
    UserPage.tsx
  hooks/              # 공통 커스텀 훅
  utils/              # 유틸리티 함수
  types/              # 공통 타입
```

### index.ts 패턴

```typescript
// 공개 API만 노출
export { Button } from './Button';
export type { ButtonProps } from './Button';

// 내부 구현은 숨김 (ButtonInternal, useButtonState 등)
```

## Accessibility Fundamentals

### 1. Semantic HTML First

```tsx
// Bad
<div onClick={handleClick}>Click me</div>

// Good
<button onClick={handleClick}>Click me</button>
```

### 2. ARIA Roles and Labels

ARIA는 시맨틱 HTML로 표현할 수 없을 때만 사용합니다.

```tsx
// 커스텀 체크박스
<div
  role="checkbox"
  aria-checked={isChecked}
  aria-label="Accept terms and conditions"
  tabIndex={0}
  onClick={toggle}
  onKeyDown={(e) => e.key === ' ' && toggle()}
/>

// 하지만 가능하면 네이티브 사용
<input
  type="checkbox"
  checked={isChecked}
  onChange={toggle}
  aria-label="Accept terms and conditions"
/>
```

### 3. Keyboard Navigation

```tsx
function Dropdown({ items }: DropdownProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const handleKeyDown = (e: KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((i) => Math.min(i + 1, items.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((i) => Math.max(i - 1, 0));
        break;
      case 'Enter':
        selectItem(items[selectedIndex]);
        break;
      case 'Escape':
        closeDropdown();
        break;
    }
  };

  return <div role="listbox" onKeyDown={handleKeyDown}>...</div>;
}
```

### 4. Focus Management

```tsx
function Modal({ isOpen, onClose }: ModalProps) {
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  return isOpen ? (
    <div ref={modalRef} role="dialog" aria-modal="true" tabIndex={-1}>
      ...
    </div>
  ) : null;
}
```

### 5. Color Contrast

WCAG AA 기준: 4.5:1 (일반 텍스트), 3:1 (대형 텍스트, UI 컴포넌트)

도구: Chrome DevTools, axe DevTools

## Anti-Patterns

| Anti-Pattern | 문제 | 해결책 |
|-------------|------|--------|
| **Prop Drilling** | 3단계 이상 prop 전달, 유지보수 어려움 | Context, Store 사용 |
| **Massive Component** | 500줄 이상, 테스트/이해 어려움 | 하위 컴포넌트로 분리 |
| **Business Logic in Component** | 재사용 불가, 테스트 어려움 | Custom Hook/Composable로 추출 |
| **Direct DOM Manipulation** | React/Vue 충돌, 예측 불가 | ref 올바르게 사용 |
| **Inline Object/Array in Deps** | 무한 루프 | useMemo 또는 외부 선언 |
| **useEffect for Derived State** | 불필요한 렌더링 | useMemo / computed 사용 |
| **Too Many useState** | 복잡한 상태 관리 | useReducer / reactive 사용 |
| **Premature Optimization** | 코드 복잡도 증가 | 문제 발생 시 최적화 |
| **Index as Key** | 리스트 업데이트 시 버그 | 고유 ID 사용 |
| **Mutation in React** | 리렌더링 안 됨 | 불변성 유지 (spread, immer) |

### 상세 예제

**Prop Drilling**:
```tsx
// Bad
<App>
  <Header user={user} />
    <Nav user={user} />
      <UserMenu user={user} /> {/* 3단계 전달 */}
</App>

// Good - Context
const UserContext = createContext<User | null>(null);

<UserContext.Provider value={user}>
  <App>
    <Header />  {/* user prop 불필요 */}
  </App>
</UserContext.Provider>

function UserMenu() {
  const user = useContext(UserContext);
  return ...;
}
```

**Derived State**:
```tsx
// Bad
const [items, setItems] = useState([]);
const [total, setTotal] = useState(0);

useEffect(() => {
  setTotal(items.reduce((sum, item) => sum + item.price, 0));
}, [items]); // 불필요한 리렌더링

// Good
const [items, setItems] = useState([]);
const total = useMemo(
  () => items.reduce((sum, item) => sum + item.price, 0),
  [items]
);
```

**Index as Key**:
```tsx
// Bad - 정렬/필터 시 버그
{items.map((item, index) => (
  <Item key={index} item={item} />
))}

// Good
{items.map((item) => (
  <Item key={item.id} item={item} />
))}
```
