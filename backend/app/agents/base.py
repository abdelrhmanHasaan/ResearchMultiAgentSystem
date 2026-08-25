"""Agent contract."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process input data and return its contribution to the pipeline."""
        raise NotImplementedError
