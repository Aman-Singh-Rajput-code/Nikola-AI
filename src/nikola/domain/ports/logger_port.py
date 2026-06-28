"""Abstract contract for module-specific loggers.

This port lets domain and application code (in future sprints) type-hint
against "a thing I can log messages to" without depending on Python's
stdlib `logging` module directly, or on how Nikola AI happens to configure
handlers/formatters under the hood.

In practice, the concrete logger returned by
`nikola.infrastructure.logging.get_logger()` is a stdlib `logging.Logger`,
which already satisfies this protocol's shape (it has `.debug()`,
`.info()`, etc.) — no adapter class is needed to bridge the two. The port
exists so that call sites depend on a narrow, stable interface rather than
implicitly depending on "whatever `logging.getLogger()` happens to return,"
which keeps the door open to a future non-stdlib logging backend without
touching every module that logs something.
"""

from __future__ import annotations

from typing import Any, Protocol


class LoggerPort(Protocol):
    """Structural contract for a module-specific logger.

    Defined as a `Protocol` (structural typing) rather than an `ABC`
    (nominal typing) because the concrete object handed back by
    `get_logger()` is a stdlib `logging.Logger` — a class Nikola AI does
    not own and should not be forced to subclass just to satisfy this
    port. Any object with these five methods, with this signature shape,
    satisfies `LoggerPort` automatically.

    `*args: Any, **kwargs: Any` (rather than `object`) is deliberate:
    `logging.Logger`'s real methods accept specific named keyword
    arguments (`exc_info`, `stack_info`, `stacklevel`, `extra`, ...) with
    their own specific types, not an arbitrary `**kwargs: object`. Typing
    this protocol with `object` would make `logging.Logger` structurally
    incompatible with it, which defeats the point of the protocol. `Any`
    is the conventional, correct typing for a passthrough logging-call
    signature like this one.
    """

    def debug(self, msg: object, *args: Any, **kwargs: Any) -> None: ...

    def info(self, msg: object, *args: Any, **kwargs: Any) -> None: ...

    def warning(self, msg: object, *args: Any, **kwargs: Any) -> None: ...

    def error(self, msg: object, *args: Any, **kwargs: Any) -> None: ...

    def critical(self, msg: object, *args: Any, **kwargs: Any) -> None: ...
