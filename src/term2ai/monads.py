from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, cast

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


@dataclass(frozen=True)
class Result(Generic[T, E]):
    """Result monad for type-safe error handling"""

    _value: T | E
    _is_success: bool

    @classmethod
    def success(cls, value: T) -> "Result[T, E]":
        return cls(_value=value, _is_success=True)

    @classmethod
    def failure(cls, error: E) -> "Result[T, E]":
        return cls(_value=error, _is_success=False)

    def bind(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        if self._is_success:
            return func(cast(T, self._value))
        return Result.failure(cast(E, self._value))

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        if self._is_success:
            return Result.success(func(cast(T, self._value)))
        return Result.failure(cast(E, self._value))

    def map_err(self, func: Callable[[E], U]) -> "Result[T, U]":
        if not self._is_success:
            return Result.failure(func(cast(E, self._value)))
        return Result.success(cast(T, self._value))

    def is_success(self) -> bool:
        return self._is_success

    def is_failure(self) -> bool:
        return not self._is_success

    def unwrap(self) -> T:
        """Unwrap the success value, raises exception if failure"""
        if self._is_success:
            return cast(T, self._value)
        raise ValueError(f"Called unwrap on failure: {self._value}")

    def unwrap_or(self, default: T) -> T:
        """Unwrap the success value or return default if failure"""
        if self._is_success:
            return cast(T, self._value)
        return default

    def unwrap_err(self) -> E:
        """Unwrap the error value, raises exception if success"""
        if not self._is_success:
            return cast(E, self._value)
        raise ValueError(f"Called unwrap_err on success: {self._value}")


class IOEffect(Generic[T]):
    """IOEffect monad for encapsulating side effects"""

    def __init__(self, effect: Callable[[], T]):
        self._effect = effect

    def run(self) -> T:
        """Execute the effect and return the result"""
        return self._effect()

    def bind(self, func: Callable[[T], "IOEffect[U]"]) -> "IOEffect[U]":
        """Monadic bind operation for IOEffect"""

        def combined_effect() -> U:
            result = self.run()
            return func(result).run()

        return IOEffect(combined_effect)

    def map(self, func: Callable[[T], U]) -> "IOEffect[U]":
        """Map a function over the IOEffect result"""

        def mapped_effect() -> U:
            return func(self.run())

        return IOEffect(mapped_effect)

    def flat_map(self, func: Callable[[T], "IOEffect[U]"]) -> "IOEffect[U]":
        """Alias for bind to match common functional programming conventions"""
        return self.bind(func)

    @staticmethod
    def pure(value: T) -> "IOEffect[T]":
        """Create an IOEffect that returns a pure value"""
        return IOEffect(lambda: value)

    @staticmethod
    def from_callable(func: Callable[[], T]) -> "IOEffect[T]":
        """Create an IOEffect from a callable"""
        return IOEffect(func)


class Maybe(Generic[T]):
    """Maybe monad for null safety"""

    def __init__(self, value: T | None):
        self._value = value

    @classmethod
    def some(cls, value: T) -> "Maybe[T]":
        """Create a Maybe with a value"""
        if value is None:
            raise ValueError("Cannot create Some with None value")
        return cls(value)

    @classmethod
    def none(cls) -> "Maybe[T]":
        """Create an empty Maybe"""
        return cls(None)

    @classmethod
    def from_optional(cls, value: T | None) -> "Maybe[T]":
        """Create a Maybe from an optional value"""
        return cls(value)

    def is_some(self) -> bool:
        """Check if Maybe contains a value"""
        return self._value is not None

    def is_none(self) -> bool:
        """Check if Maybe is empty"""
        return self._value is None

    def bind(self, func: Callable[[T], "Maybe[U]"]) -> "Maybe[U]":
        """Monadic bind operation for Maybe"""
        if self.is_some():
            return func(cast(T, self._value))
        return Maybe.none()

    def map(self, func: Callable[[T], U]) -> "Maybe[U]":
        """Map a function over the Maybe value"""
        if self.is_some():
            return Maybe.some(func(cast(T, self._value)))
        return Maybe.none()

    def unwrap(self) -> T:
        """Unwrap the value, raises exception if None"""
        if self.is_some():
            return cast(T, self._value)
        raise ValueError("Called unwrap on None")

    def unwrap_or(self, default: T) -> T:
        """Unwrap the value or return default if None"""
        if self.is_some():
            return cast(T, self._value)
        return default

    def filter(self, predicate: Callable[[T], bool]) -> "Maybe[T]":
        """Filter the Maybe value with a predicate"""
        if self.is_some() and predicate(cast(T, self._value)):
            return self
        return Maybe.none()


def sequence_results(results: list[Result[T, E]]) -> Result[list[T], E]:
    """Convert a list of Results to a Result of list"""
    values = []
    for result in results:
        if result.is_failure():
            return Result.failure(result.unwrap_err())
        values.append(result.unwrap())
    return Result.success(values)


def sequence_maybes(maybes: list[Maybe[T]]) -> Maybe[list[T]]:
    """Convert a list of Maybes to a Maybe of list"""
    values = []
    for maybe in maybes:
        if maybe.is_none():
            return Maybe.none()
        values.append(maybe.unwrap())
    return Maybe.some(values)


def sequence_effects(effects: list[IOEffect[T]]) -> IOEffect[list[T]]:
    """Convert a list of IOEffects to an IOEffect of list"""

    def run_all() -> list[T]:
        return [effect.run() for effect in effects]

    return IOEffect(run_all)
