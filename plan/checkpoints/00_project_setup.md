# 체크포인트 0: 함수형 프로젝트 설정

## 개요
**함수형 프로그래밍 패러다임** 기반 term2ai 터미널 래퍼 프로젝트를 위한 기본 프로젝트 인프라, 의존성 및 개발 환경을 설정합니다. 순수 함수, 모나드 시스템, Property-based testing을 지원하는 함수형 개발 환경을 구축합니다.

## 상태
- **우선순위**: 높음
- **상태**: ✅ 완료 (2025-06-22)
- **예상 시간**: 2시간
- **실제 시간**: 1.5시간

## 의존성
- 없음 (초기 체크포인트)

## 기술 요구사항

### 1. 프로젝트 초기화
- **설명**: uv 패키지 매니저로 Python 프로젝트 초기화
- **승인 기준**:
  - `uv init --lib` 구조로 프로젝트 생성
  - 라이브러리 개발을 위한 적절한 src/ 레이아웃
  - Git 저장소 초기화
  - Python 3.11+ 호환성

### 2. 함수형 의존성 관리
- **설명**: 함수형 터미널 래퍼 기능을 위한 핵심 의존성 추가
- **승인 기준**:
  - 핵심 라이브러리 추가: pydantic, ptyprocess, pexpect, rich, typer, aiofiles
  - 함수형 프로그래밍 지원: hypothesis (property-based testing)
  - Unix 최적화 (선택적): uvloop, aiosignal
  - 개발 의존성 추가: pytest, pytest-asyncio, mypy, ruff, black, pytest-cov, pytest-timeout
  - uv.lock 파일에 의존성 잠금
  - 함수형 개발 환경이 완전히 설정됨

### 3. 함수형 프로젝트 구조
- **설명**: 함수형 개발을 위한 체계적인 디렉토리 구조 생성
- **승인 기준**:
  - 함수형 아키텍처 문서 (docs/functional-architecture.md)
  - 문서 디렉토리 (docs/) - 함수형 설계 문서 포함
  - Pydantic 모델이 포함된 계획 디렉토리 (plan/)
  - 함수형 체크포인트 추적 디렉토리 (plan/checkpoints/)
  - Property-based 테스트 디렉토리 구조 (tests/)
  - 함수형 소스 코드 구조 (src/term2ai/):
    - src/term2ai/monads/ (모나드 시스템)
    - src/term2ai/effects/ (Effect 시스템)
    - src/term2ai/streams/ (함수형 스트림)
    - src/term2ai/pure/ (순수 함수 모듈)

### 4. 설정 파일
- **설명**: 개발 및 테스트 설정 구성
- **승인 기준**:
  - 테스트 발견 및 커버리지를 위한 pytest.ini 구성
  - Python/uv 프로젝트를 위한 .gitignore 구성
  - 프로젝트 메타데이터로 pyproject.toml 업데이트
  - 개발 도구 구성 (ruff, black, mypy)

## 함수형 테스트 케이스

### 단위 테스트
1. **test_functional_project_structure_exists**: 함수형 디렉토리 구조가 존재하는지 확인
2. **test_functional_dependencies_importable**: 함수형 의존성을 가져올 수 있는지 확인
3. **test_pydantic_models_valid**: 불변 Pydantic 모델을 인스턴스화할 수 있는지 확인
4. **test_hypothesis_setup**: Property-based testing 프레임워크가 작동하는지 확인

### Property-Based 테스트
1. **test_basic_property_examples**: 간단한 속성 기반 테스트 예제가 실행되는지 확인
2. **test_immutable_data_structures**: 모든 데이터 구조가 불변인지 확인

### 통합 테스트
1. **test_uv_commands_work**: 함수형 프로젝트에서 uv 명령이 작동하는지 확인
2. **test_pytest_runs**: pytest가 property-based 테스트를 발견하고 실행할 수 있는지 확인
3. **test_functional_linting_passes**: 함수형 코드가 린팅 검사를 통과하는지 확인

## 함수형 결과물

### 1. 함수형 프로젝트 구조
- **상태**: ✅ 완료
- **위치**: 루트 디렉토리
- **설명**: 함수형 프로그래밍을 지원하는 완전한 프로젝트 디렉토리 구조

### 2. 함수형 아키텍처 문서
- **상태**: ✅ 완료
- **위치**: docs/functional-architecture.md
- **설명**: 순수 함수, 모나드, Effect 시스템을 포함한 함수형 설계 문서

### 3. 불변 Pydantic 모델
- **상태**: ✅ 완료
- **위치**: plan/models/
- **설명**: 체크포인트, 테스트 및 프로젝트 추적을 위한 불변 타입 안전 모델

### 4. 함수형 설정 파일
- **상태**: ✅ 완료
- **위치**: 루트 디렉토리
- **설명**: pytest.ini (property-based testing 포함), .gitignore, pyproject.toml

### 5. 함수형 체크포인트 문서
- **상태**: ✅ 완료
- **위치**: plan/checkpoints/
- **설명**: 모든 함수형 프로젝트 단계를 위한 구조화된 문서

## 함수형 프로그래밍 참고사항
- 프로젝트는 빠른 의존성 관리를 위해 uv 사용
- 불변 Pydantic 모델은 타입 안전성과 불변성을 동시에 제공
- 모든 후속 체크포인트에서 Property-Based TDD 방식 적용
- 함수형 프로젝트 구조는 순수 함수 라이브러리와 Effect 기반 애플리케이션 개발 모두 지원
- hypothesis 프레임워크로 속성 기반 테스트 적용
- 모든 비즈니스 로직은 순수 함수로 구현
- Effect 시스템을 통한 명시적 부작용 관리

## 다음 체크포인트
이 함수형 기반 체크포인트가 검증되면 [체크포인트 1: 순수 함수 기반 PTY 처리](01_basic_pty_wrapper.md)로 진행합니다.
