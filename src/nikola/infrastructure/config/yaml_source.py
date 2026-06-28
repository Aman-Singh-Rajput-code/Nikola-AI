"""A `pydantic-settings` source that reads configuration from a YAML file.

`pydantic-settings` ships built-in sources for init kwargs, environment
variables, `.env` files, and secret files — but not YAML. This module
implements the missing piece: a `PydanticBaseSettingsSource` subclass that
reads and parses a YAML file, exposing it the same way the built-in sources
do, so it can be spliced into the resolution order in
`NikolaSettings.settings_customise_sources` (see `settings.py`).

Keeping this in its own file (rather than inlining it into `settings.py`)
keeps the schema module focused purely on shape/validation, and makes this
YAML-reading concern independently testable and replaceable — for instance,
a future sprint could add a `TomlConfigSettingsSource` alongside it without
touching `settings.py`'s structure.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from pydantic_settings import PydanticBaseSettingsSource

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo

DEFAULT_YAML_CONFIG_PATH = Path("config/default.yaml")

#: Name of the environment variable that, if set, overrides which YAML file
#: this source reads from. Primarily useful for tests that want to point at
#: a temporary fixture file without mutating the real config/default.yaml.
YAML_CONFIG_PATH_ENV_VAR = "NIKOLA_CONFIG_FILE"


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """Reads a YAML file and exposes its contents as a settings source.

    Resolution of *which* file to read, in priority order:

        1. An explicit `yaml_file` passed to the constructor (used by the
           loader when a caller specifies a path explicitly).
        2. The `NIKOLA_CONFIG_FILE` environment variable, if set.
        3. The default path, `config/default.yaml`, resolved relative to
           the current working directory.

    A missing YAML file is NOT treated as an error here — `config/default.yaml`
    is expected to exist in any real checkout, but unit tests constructing a
    bare `NikolaSettings()` without a config file present should still be
    able to fall back cleanly to field defaults. Whether a missing default
    config file should be fatal in a real running application is decided by
    `nikola.infrastructure.config.loader.load_settings`, not here.
    """

    def __init__(
        self,
        settings_cls: type[Any],
        yaml_file: str | Path | None = None,
    ) -> None:
        super().__init__(settings_cls)
        self._yaml_file = self._resolve_yaml_path(yaml_file)

    @staticmethod
    def _resolve_yaml_path(explicit_path: str | Path | None) -> Path:
        if explicit_path is not None:
            return Path(explicit_path)
        env_override = os.environ.get(YAML_CONFIG_PATH_ENV_VAR)
        if env_override:
            return Path(env_override)
        return DEFAULT_YAML_CONFIG_PATH

    def _read_yaml(self) -> dict[str, Any]:
        if not self._yaml_file.is_file():
            return {}

        with self._yaml_file.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle)

        if loaded is None:
            # An empty YAML file is valid and simply contributes no overrides.
            return {}

        if not isinstance(loaded, dict):
            raise ValueError(
                f"Configuration file '{self._yaml_file}' must contain a YAML "
                f"mapping (key: value pairs) at the top level, got "
                f"{type(loaded).__name__} instead."
            )

        return loaded

    def get_field_value(  # pragma: no cover
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        """Required by the base class; unused because we override __call__.

        The `field` parameter is part of `PydanticBaseSettingsSource`'s
        abstract interface and must be accepted even though this source
        resolves values wholesale via `__call__` rather than field-by-field.
        Marked `no cover`: `pydantic-settings` never actually calls this
        method on a source that overrides `__call__`, so it is unreachable
        in practice. It exists solely to satisfy the abstract base class.
        """
        del field  # Required by the abstract signature; not used here.
        data = self._read_yaml()
        return data.get(field_name), field_name, False

    def __call__(self) -> dict[str, Any]:
        """Return the parsed YAML content as a plain dict.

        Returning the whole mapping (rather than resolving field-by-field
        via `get_field_value`) lets nested sections (`app:`, `logging:`)
        pass straight through to Pydantic's own nested-model validation,
        the same way a nested dict from environment variables or `.env`
        would be handled.
        """
        return self._read_yaml()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(yaml_file={self._yaml_file})"
