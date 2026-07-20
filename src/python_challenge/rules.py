"""Detection rule definitions used by the scanner."""

from dataclasses import dataclass
import re
from typing import Pattern


_VALUE = r'''(?P<value>"[^"\r\n]*"|'[^'\r\n]*'|[^\s#]+)'''


@dataclass(frozen=True)
class Rule:
    """A named regular-expression rule for secret-like assignments."""

    identifier: str
    pattern: Pattern[str]


RULES = (
    Rule("password-assignment", re.compile(rf"(?i)\bpassword\s*=\s*{_VALUE}")),
    Rule("api-key-assignment", re.compile(rf"(?i)\bapi_key\s*=\s*{_VALUE}")),
    Rule("access-token-assignment", re.compile(rf"(?i)\baccess_token\s*=\s*{_VALUE}")),
    Rule("client-secret-assignment", re.compile(rf"(?i)\bclient_secret\s*=\s*{_VALUE}")),
)
