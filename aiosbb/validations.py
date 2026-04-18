__all__ = "Validations"

from dataclasses import dataclass
from contextlib import suppress


"""A mixin class for validating dataclass fields."""
@dataclass
class Validations:
    def __post_init__(self) -> None:
        """Validate all of the fields in the dataclass."""
        for name, _field in self.__dataclass_fields__.items():
            
            """Validate the field with the specified name."""
            if method := getattr(self, f"_validate_{name}", None):
                with suppress(Exception):
                    setattr(self, name, method(getattr(self, name), field=_field))
