# 체크포인트 6: 순수 함수 ANSI 파싱

## 개요
ANSI 이스케이프 시퀀스 파싱을 **완전한 순수 함수**로 구현합니다. Parser 모나드를 사용하여 복잡한 파싱 로직을 합성 가능한 작은 파서들로 분해하고, Property-based testing으로 파싱의 정확성을 검증합니다. 모든 파싱 에러는 Result 모나드로 타입 안전하게 처리됩니다.

## 상태
- **우선순위**: 높음
- **상태**: 📋 대기
- **예상 시간**: 7시간 (순수 함수 + Property-based testing)
- **의존성**: 체크포인트 2 (모나드 기반 I/O 시스템)

## 함수형 기술 요구사항

### 1. Parser 모나드 구현
- **설명**: 파싱을 위한 함수형 Parser 모나드
- **승인 기준**:
  - Parser 모나드 타입 정의 (`Parser[T]`)
  - 기본 파서 조합자 (`char`, `string`, `satisfy`)
  - 파서 합성 연산자 (`bind`, `map`, `<|>`, `>>`, `<<`)
  - 반복 파서 (`many`, `many1`, `sepBy`)
  - 파서 실행 함수 (`run_parser`)

### 2. ANSI 시퀀스 파서
- **설명**: 다양한 ANSI 이스케이프 시퀀스를 파싱하는 순수 함수
- **승인 기준**:
  - CSI 시퀀스 파서 (`parse_csi_sequence`)
  - OSC 시퀀스 파서 (`parse_osc_sequence`)
  - SGR 시퀀스 파서 (`parse_sgr_sequence`)
  - 커서 제어 파서 (`parse_cursor_control`)
  - DEC 프라이빗 모드 파서 (`parse_dec_private`)

### 3. 파싱 결과 타입
- **설명**: 파싱된 ANSI 시퀀스의 타입 안전한 표현
- **승인 기준**:
  - ANSI 명령 ADT (`ANSICommand`)
  - 파싱 에러 타입 (`ParseError`)
  - 파싱 컨텍스트 타입 (`ParseContext`)
  - 시퀀스 파라미터 타입 (`SequenceParams`)
  - 파싱 결과 변환 함수 (`transform_parse_result`)

### 4. 증분 파싱 지원
- **설명**: 불완전한 입력에 대한 증분 파싱
- **승인 기준**:
  - 파싱 상태 타입 (`ParseState`)
  - 증분 파서 (`incremental_parser`)
  - 버퍼 관리 순수 함수 (`update_parse_buffer`)
  - 완료 검사 순수 함수 (`is_sequence_complete`)
  - 파싱 재개 함수 (`resume_parsing`)

### 5. 파서 최적화
- **설명**: 효율적인 파싱을 위한 순수 함수 최적화
- **승인 기준**:
  - 파서 메모이제이션 (`memoize_parser`)
  - 룩어헤드 최적화 (`lookahead_parser`)
  - 파서 특수화 (`specialize_parser`)
  - 파싱 통계 수집 (`collect_parse_stats`)
  - 파서 벤치마킹 함수 (`benchmark_parser`)

## 함수형 테스트 케이스

### Property-Based 파싱 테스트

#### test_parser_monad_laws
- **설명**: Parser 모나드가 모나드 법칙을 만족하는지 테스트
- **테스트 타입**: Property-based 모나드
- **예상 동작**: Left identity, Right identity, Associativity 성립

#### test_parsing_inverse_property
- **설명**: 파싱과 직렬화가 역함수 관계인지 테스트
- **테스트 타입**: Property-based 역함수
- **예상 동작**: `serialize(parse(s)) == s` (유효한 시퀀스에 대해)

#### test_parser_composition_property
- **설명**: 파서 합성의 결합법칙 테스트
- **테스트 타입**: Property-based 합성
- **예상 동작**: `(p1 >> p2) >> p3 == p1 >> (p2 >> p3)`

### ANSI 시퀀스 파싱 테스트

#### test_all_ansi_sequences_parseable
- **설명**: 모든 표준 ANSI 시퀀스 파싱 가능 테스트
- **테스트 타입**: 포괄적 파싱
- **예상 동작**: 알려진 모든 ANSI 시퀀스가 성공적으로 파싱됨

#### test_malformed_sequence_handling
- **설명**: 잘못된 시퀀스에 대한 에러 처리 테스트
- **테스트 타입**: 에러 처리
- **예상 동작**: 잘못된 시퀀스는 적절한 ParseError 반환

#### test_incremental_parsing_consistency
- **설명**: 증분 파싱과 전체 파싱의 일관성 테스트
- **테스트 타입**: 일관성 테스트
- **예상 동작**: 증분 파싱 결과와 전체 파싱 결과 동일

### 파서 성능 테스트

#### test_parser_linear_complexity
- **설명**: 파서의 선형 시간 복잡도 테스트
- **테스트 타입**: 성능 테스트
- **예상 동작**: 입력 길이에 대해 O(n) 시간 복잡도

#### test_parser_memory_efficiency
- **설명**: 파서의 메모리 사용량 테스트
- **테스트 타입**: 메모리 테스트
- **예상 동작**: 일정한 메모리 사용량 (스트리밍 파싱)

## 함수형 결과물

### 1. Parser 모나드
- **위치**: src/term2ai/parsing/parser_monad.py
- **설명**: 함수형 파서 조합자 라이브러리
- **구현**:
  ```python
  from typing import TypeVar, Callable, Optional, Tuple
  from dataclasses import dataclass

  T = TypeVar('T')

  @dataclass(frozen=True)
  class ParseResult[T]:
      value: Optional[T]
      remaining: str
      position: int

  @dataclass(frozen=True)
  class Parser[T]:
      parse: Callable[[str, int], ParseResult[T]]

      def bind[U](self, f: Callable[[T], Parser[U]]) -> Parser[U]:
          """모나드 bind 연산"""
          def bound_parse(input: str, pos: int) -> ParseResult[U]:
              result = self.parse(input, pos)
              if result.value is None:
                  return ParseResult(None, result.remaining, result.position)
              next_parser = f(result.value)
              return next_parser.parse(result.remaining, result.position)
          return Parser(bound_parse)

      def map[U](self, f: Callable[[T], U]) -> Parser[U]:
          """Functor map 연산"""
          return self.bind(lambda x: Parser.pure(f(x)))

      def __or__(self, other: 'Parser[T]') -> 'Parser[T]':
          """대체 파서 (|) 연산자"""
          def alt_parse(input: str, pos: int) -> ParseResult[T]:
              result = self.parse(input, pos)
              if result.value is not None:
                  return result
              return other.parse(input, pos)
          return Parser(alt_parse)

      @staticmethod
      def pure(value: T) -> Parser[T]:
          """순수 값을 파서로 리프팅"""
          return Parser(lambda inp, pos: ParseResult(value, inp, pos))

  # 기본 파서 조합자
  def char(c: str) -> Parser[str]:
      """특정 문자를 파싱"""
      def char_parse(input: str, pos: int) -> ParseResult[str]:
          if pos < len(input) and input[pos] == c:
              return ParseResult(c, input[pos+1:], pos + 1)
          return ParseResult(None, input, pos)
      return Parser(char_parse)

  def many[T](parser: Parser[T]) -> Parser[list[T]]:
      """0개 이상 반복 파싱"""
      def many_parse(input: str, pos: int) -> ParseResult[list[T]]:
          results = []
          current_input = input
          current_pos = pos
          while True:
              result = parser.parse(current_input, current_pos)
              if result.value is None:
                  break
              results.append(result.value)
              current_input = result.remaining
              current_pos = result.position
          return ParseResult(results, current_input, current_pos)
      return Parser(many_parse)
  ```

### 2. ANSI 시퀀스 파서
- **위치**: src/term2ai/parsing/ansi_parser.py
- **설명**: ANSI 이스케이프 시퀀스 파싱 구현
- **구현**:
  ```python
  # ANSI 명령 타입
  @dataclass(frozen=True)
  class CursorMove:
      direction: Literal['up', 'down', 'forward', 'back']
      count: int

  @dataclass(frozen=True)
  class SGRCommand:
      attributes: tuple[int, ...]

  @dataclass(frozen=True)
  class EraseCommand:
      target: Literal['screen', 'line', 'display']
      mode: Literal['to_end', 'to_beginning', 'all']

  ANSICommand = Union[CursorMove, SGRCommand, EraseCommand, ...]

  # ESC 파서
  esc_parser = char('\x1b')

  # CSI 시퀀스 파서
  def parse_csi_sequence() -> Parser[ANSICommand]:
      """Control Sequence Introducer 파싱"""
      return (
          esc_parser >>
          char('[') >>
          parse_csi_params().bind(lambda params:
          parse_csi_command().map(lambda cmd:
              create_ansi_command(cmd, params)
          ))
      )

  def parse_csi_params() -> Parser[list[int]]:
      """CSI 파라미터 파싱 (예: "1;2;3")"""
      return sepBy(parse_number(), char(';'))

  def parse_sgr_sequence() -> Parser[SGRCommand]:
      """Select Graphic Rendition 파싱"""
      return (
          esc_parser >>
          char('[') >>
          parse_csi_params() <<
          char('m')
      ).map(SGRCommand)

  # 증분 파싱 지원
  @dataclass(frozen=True)
  class PartialParse:
      buffer: str
      parsed_commands: tuple[ANSICommand, ...]

  def incremental_parse(
      partial: PartialParse,
      new_data: str
  ) -> tuple[PartialParse, tuple[ANSICommand, ...]]:
      """증분적으로 ANSI 시퀀스 파싱"""
      combined = partial.buffer + new_data
      commands = []
      remaining = combined

      while remaining:
          result = parse_any_sequence().parse(remaining, 0)
          if result.value is None:
              # 불완전한 시퀀스
              break
          commands.append(result.value)
          remaining = result.remaining

      return (
          PartialParse(remaining, partial.parsed_commands + tuple(commands)),
          tuple(commands)
      )
  ```

### 3. 파싱 결과 타입
- **위치**: src/term2ai/parsing/types.py
- **설명**: 파싱 관련 타입 정의
- **구현**:
  ```python
  @dataclass(frozen=True)
  class ParseError:
      position: int
      expected: str
      actual: str
      context: str

  @dataclass(frozen=True)
  class ParseContext:
      line: int
      column: int
      file_offset: int
      parse_mode: Literal['strict', 'lenient', 'recovery']

  @dataclass(frozen=True)
  class ParseStatistics:
      total_bytes: int
      parsed_sequences: int
      failed_sequences: int
      parse_time_ms: float

  def transform_parse_result(
      result: ParseResult[ANSICommand],
      context: ParseContext
  ) -> Result[ANSICommand, ParseError]:
      """파싱 결과를 Result 모나드로 변환"""
      if result.value is not None:
          return Ok(result.value)

      error = ParseError(
          position=result.position,
          expected="valid ANSI sequence",
          actual=result.remaining[:10] + "...",
          context=f"line {context.line}, col {context.column}"
      )
      return Err(error)
  ```

### 4. 파서 최적화
- **위치**: src/term2ai/parsing/optimization.py
- **설명**: 파서 성능 최적화 기법
- **구현**:
  ```python
  from functools import lru_cache

  def memoize_parser[T](parser: Parser[T], cache_size: int = 128) -> Parser[T]:
      """파서 결과 메모이제이션"""
      @lru_cache(maxsize=cache_size)
      def cached_parse(input: str, pos: int) -> ParseResult[T]:
          return parser.parse(input, pos)

      return Parser(cached_parse)

  def lookahead[T](parser: Parser[T]) -> Parser[Optional[T]]:
      """입력을 소비하지 않는 룩어헤드 파서"""
      def lookahead_parse(input: str, pos: int) -> ParseResult[Optional[T]]:
          result = parser.parse(input, pos)
          # 성공해도 입력 위치 변경 안함
          return ParseResult(result.value, input, pos)

      return Parser(lookahead_parse)

  def optimize_ansi_parser() -> Parser[ANSICommand]:
      """최적화된 ANSI 파서 생성"""
      # 자주 사용되는 시퀀스 우선 파싱
      common_sequences = (
          parse_sgr_sequence() |  # 가장 흔한 색상/스타일
          parse_cursor_move() |   # 커서 이동
          parse_erase_line()      # 라인 지우기
      )

      # 덜 흔한 시퀀스
      rare_sequences = (
          parse_osc_sequence() |
          parse_dec_private() |
          parse_apc_sequence()
      )

      return memoize_parser(common_sequences | rare_sequences)
  ```

### 5. Property-Based 테스트
- **위치**: tests/test_checkpoint_06_ansi_parsing/
- **설명**: ANSI 파싱의 속성 기반 테스트
- **파일**:
  - `test_parser_monad.py`: Parser 모나드 법칙 테스트
  - `test_ansi_sequences.py`: ANSI 시퀀스 파싱 테스트
  - `test_parse_properties.py`: 파싱 속성 테스트
  - `test_incremental_parsing.py`: 증분 파싱 테스트
  - `test_parser_performance.py`: 성능 및 메모리 테스트

### 6. ANSI 시퀀스 생성기
- **위치**: src/term2ai/parsing/generators.py
- **설명**: 테스트용 ANSI 시퀀스 생성 순수 함수
- **구현**:
  ```python
  def generate_sgr_sequence(attributes: list[int]) -> str:
      """SGR 시퀀스 생성"""
      params = ';'.join(map(str, attributes))
      return f"\x1b[{params}m"

  def generate_cursor_sequence(
      direction: str,
      count: int = 1
  ) -> str:
      """커서 이동 시퀀스 생성"""
      direction_codes = {
          'up': 'A', 'down': 'B',
          'forward': 'C', 'back': 'D'
      }
      return f"\x1b[{count}{direction_codes[direction]}"

  # Property-based testing을 위한 임의 시퀀스 생성
  @composite
  def ansi_sequence_strategy(draw):
      """Hypothesis를 위한 ANSI 시퀀스 전략"""
      seq_type = draw(sampled_from(['sgr', 'cursor', 'erase']))

      if seq_type == 'sgr':
          attrs = draw(lists(integers(0, 107), min_size=1))
          return generate_sgr_sequence(attrs)
      elif seq_type == 'cursor':
          direction = draw(sampled_from(['up', 'down', 'forward', 'back']))
          count = draw(integers(1, 999))
          return generate_cursor_sequence(direction, count)
      # ... 더 많은 시퀀스 타입
  ```

## 함수형 구현 참고사항

### 파서 설계 원칙
1. **조합성**: 작은 파서들을 조합하여 복잡한 파서 구성
2. **불변성**: 파싱 중 상태 변경 없음
3. **결정성**: 동일 입력에 대해 항상 동일한 결과
4. **에러 전파**: Result 모나드로 모든 에러 처리

### ANSI 표준 준수
- **ECMA-48**: 기본 제어 시퀀스 표준
- **XTerm 확장**: 256색 및 트루컬러 지원
- **DEC VT100/VT220**: 레거시 터미널 호환성
- **현대 터미널**: iTerm2, Windows Terminal 확장

### 성능 고려사항
- **스트리밍 파싱**: 전체 입력을 메모리에 로드하지 않음
- **조기 종료**: 파싱 실패 시 즉시 중단
- **메모이제이션**: 반복되는 패턴 캐싱
- **특수화**: 일반적인 시퀀스 최적화

## 함수형 승인 기준
- [ ] Parser 모나드가 모나드 법칙을 만족함
- [ ] 모든 표준 ANSI 시퀀스가 파싱됨
- [ ] 파싱 에러가 Result 타입으로 안전하게 처리됨
- [ ] 증분 파싱이 전체 파싱과 동일한 결과 생성
- [ ] Property-based 테스트로 파싱 정확성 검증
- [ ] 파싱과 생성이 역함수 관계 (왕복 테스트 통과)
- [ ] 선형 시간 복잡도와 일정한 메모리 사용량
- [ ] 잘못된 시퀀스에 대한 명확한 에러 메시지
- [ ] 파서 조합이 타입 안전하게 작동

## 다음 체크포인트
순수 함수 ANSI 파싱이 구현되면 터미널 출력을 완벽하게 이해하고 처리할 수 있으며, [체크포인트 7: 함수형 세션 관리](07_functional_sessions.md)로 진행할 수 있습니다.
