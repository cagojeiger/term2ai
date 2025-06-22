from hypothesis import given
from hypothesis import strategies as st
from term2ai.monads import IOEffect, Maybe, Result


class TestResultMonadLaws:
    """Test that Result monad satisfies monad laws"""

    @given(value=st.integers())
    def test_left_identity(self, value):
        """Left Identity: return(a).bind(f) == f(a)"""

        def f(x):
            return Result.success(x * 2)

        left_side = Result.success(value).bind(f)
        right_side = f(value)

        assert left_side._value == right_side._value
        assert left_side._is_success == right_side._is_success

    @given(value=st.integers())
    def test_right_identity(self, value):
        """Right Identity: m.bind(return) == m"""
        m = Result.success(value)
        result = m.bind(Result.success)

        assert result._value == m._value
        assert result._is_success == m._is_success

    @given(value=st.integers())
    def test_associativity(self, value):
        """Associativity: m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))"""

        def f(x):
            return Result.success(x * 2)

        def g(x):
            return Result.success(x + 1)

        m = Result.success(value)

        left_side = m.bind(f).bind(g)
        right_side = m.bind(lambda x: f(x).bind(g))

        assert left_side._value == right_side._value
        assert left_side._is_success == right_side._is_success

    @given(value=st.integers())
    def test_result_map_functor_law(self, value):
        """Test functor law: map(id) == id"""

        def identity(x):
            return x

        m = Result.success(value)
        mapped = m.map(identity)

        assert mapped._value == m._value
        assert mapped._is_success == m._is_success

    @given(value=st.integers())
    def test_result_error_propagation(self, value):
        """Test that errors propagate correctly through bind"""
        error_result = Result.failure("test error")

        def f(x):
            return Result.success(x * 2)

        result = error_result.bind(f)

        assert not result._is_success
        assert result._value == "test error"


class TestIOEffectMonadLaws:
    """Test that IOEffect monad satisfies monad laws"""

    @given(value=st.integers())
    def test_left_identity(self, value):
        """Left Identity: return(a).bind(f) == f(a)"""

        def f(x):
            return IOEffect(lambda: x * 2)

        left_side = IOEffect(lambda: value).bind(f)
        right_side = f(value)

        assert left_side.run() == right_side.run()

    @given(value=st.integers())
    def test_right_identity(self, value):
        """Right Identity: m.bind(return) == m"""
        m = IOEffect(lambda: value)
        result = m.bind(lambda x: IOEffect(lambda: x))

        assert result.run() == m.run()

    @given(value=st.integers())
    def test_associativity(self, value):
        """Associativity: m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))"""

        def f(x):
            return IOEffect(lambda: x * 2)

        def g(x):
            return IOEffect(lambda: x + 1)

        m = IOEffect(lambda: value)

        left_side = m.bind(f).bind(g)
        right_side = m.bind(lambda x: f(x).bind(g))

        assert left_side.run() == right_side.run()

    @given(value=st.integers())
    def test_ioeffect_map_functor_law(self, value):
        """Test functor law: map(id) == id"""

        def identity(x):
            return x

        m = IOEffect(lambda: value)
        mapped = m.map(identity)

        assert mapped.run() == m.run()

    @given(value=st.integers())
    def test_ioeffect_pure(self, value):
        """Test IOEffect.pure creates correct effect"""
        effect = IOEffect.pure(value)
        assert effect.run() == value


class TestMaybeMonadLaws:
    """Test that Maybe monad satisfies monad laws"""

    @given(value=st.integers())
    def test_left_identity(self, value):
        """Left Identity: return(a).bind(f) == f(a)"""

        def f(x):
            return Maybe.some(x * 2)

        left_side = Maybe.some(value).bind(f)
        right_side = f(value)

        assert left_side._value == right_side._value
        assert left_side.is_some() == right_side.is_some()

    @given(value=st.integers())
    def test_right_identity(self, value):
        """Right Identity: m.bind(return) == m"""
        m = Maybe.some(value)
        result = m.bind(Maybe.some)

        assert result._value == m._value
        assert result.is_some() == m.is_some()

    @given(value=st.integers())
    def test_associativity(self, value):
        """Associativity: m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))"""

        def f(x):
            return Maybe.some(x * 2)

        def g(x):
            return Maybe.some(x + 1)

        m = Maybe.some(value)

        left_side = m.bind(f).bind(g)
        right_side = m.bind(lambda x: f(x).bind(g))

        assert left_side._value == right_side._value
        assert left_side.is_some() == right_side.is_some()

    def test_maybe_none_propagation(self):
        """Test that None propagates correctly through bind"""
        none_maybe = Maybe.none()

        def f(x):
            return Maybe.some(x * 2)

        result = none_maybe.bind(f)

        assert result.is_none()

    @given(value=st.integers())
    def test_maybe_filter(self, value):
        """Test Maybe filter operation"""
        m = Maybe.some(value)

        filtered_true = m.filter(lambda x: True)
        assert filtered_true.is_some()
        assert filtered_true._value == value

        filtered_false = m.filter(lambda x: False)
        assert filtered_false.is_none()


class TestMonadUtilities:
    """Test utility functions for monads"""

    def test_sequence_results_success(self):
        """Test sequencing successful results"""
        from term2ai.monads import sequence_results

        results = [Result.success(1), Result.success(2), Result.success(3)]

        sequenced = sequence_results(results)
        assert sequenced._is_success
        assert sequenced._value == [1, 2, 3]

    def test_sequence_results_failure(self):
        """Test sequencing results with failure"""
        from term2ai.monads import sequence_results

        results = [Result.success(1), Result.failure("error"), Result.success(3)]

        sequenced = sequence_results(results)
        assert not sequenced._is_success
        assert sequenced._value == "error"

    def test_sequence_maybes_success(self):
        """Test sequencing successful maybes"""
        from term2ai.monads import sequence_maybes

        maybes = [Maybe.some(1), Maybe.some(2), Maybe.some(3)]

        sequenced = sequence_maybes(maybes)
        assert sequenced.is_some()
        assert sequenced._value == [1, 2, 3]

    def test_sequence_maybes_none(self):
        """Test sequencing maybes with None"""
        from term2ai.monads import sequence_maybes

        maybes = [Maybe.some(1), Maybe.none(), Maybe.some(3)]

        sequenced = sequence_maybes(maybes)
        assert sequenced.is_none()
