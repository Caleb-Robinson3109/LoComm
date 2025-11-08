"""
Lightweight LoRa network simulator that models latency, jitter, drops,
and queueing so UI flows can be exercised without real hardware.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
import random
import time
from pathlib import Path
from typing import Deque, Dict, Iterable, Optional, Tuple

from services.transport_contract import TransportMessage


@dataclass
class NetworkScenario:
    name: str
    latency_ms: Tuple[int, int] = (120, 260)
    jitter_ms: int = 60
    drop_rate: float = 0.0
    queue_limit: int = 32
    description: str = ""


class LoRaNetworkSimulator:
    scenarios_path = Path(__file__).resolve().parent.parent / "mock_data" / "scenarios.json"

    def __init__(self, scenario_name: str = "default"):
        self._queue: Deque[tuple[float, TransportMessage]] = deque()
        self._scenarios = self._load_scenarios()
        self._scenario = self._scenarios.get(scenario_name) or self._default_scenario(scenario_name)

    @property
    def scenario(self) -> NetworkScenario:
        return self._scenario

    def set_scenario(self, scenario_name: str) -> None:
        self._scenario = self._scenarios.get(scenario_name) or self._default_scenario(scenario_name)
        self._queue.clear()

    def queue_message(self, message: TransportMessage) -> bool:
        if self._should_drop():
            return False

        latency = random.uniform(*self._scenario.latency_ms) / 1000.0
        jitter = random.uniform(-self._scenario.jitter_ms, self._scenario.jitter_ms) / 1000.0
        ready_at = time.time() + max(latency + jitter, 0.0)

        if len(self._queue) >= self._scenario.queue_limit:
            self._queue.popleft()

        self._queue.append((ready_at, message))
        return True

    def next_message(self) -> Optional[TransportMessage]:
        if not self._queue:
            return None
        ready_at, message = self._queue[0]
        if time.time() >= ready_at:
            self._queue.popleft()
            return message
        return None

    def available_scenarios(self) -> Iterable[str]:
        return self._scenarios.keys()

    def scenario_summary(self) -> Dict[str, Dict]:
        return {
            name: {
                "latency_ms": scenario.latency_ms,
                "jitter_ms": scenario.jitter_ms,
                "drop_rate": scenario.drop_rate,
                "queue_limit": scenario.queue_limit,
                "description": scenario.description,
            }
            for name, scenario in self._scenarios.items()
        }

    def _should_drop(self) -> bool:
        if self._scenario.drop_rate <= 0:
            return False
        return random.random() < self._scenario.drop_rate

    def _load_scenarios(self) -> Dict[str, NetworkScenario]:
        if not self.scenarios_path.exists():
            return {"default": self._default_scenario("default")}
        try:
            with self.scenarios_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {"default": self._default_scenario("default")}

        scenarios: Dict[str, NetworkScenario] = {}
        for name, cfg in data.items():
            scenarios[name] = NetworkScenario(
                name=name,
                latency_ms=tuple(cfg.get("latency_ms", (120, 260))),
                jitter_ms=int(cfg.get("jitter_ms", 60)),
                drop_rate=float(cfg.get("drop_rate", 0.0)),
                queue_limit=int(cfg.get("queue_limit", 32)),
                description=cfg.get("description", ""),
            )
        return scenarios

    @staticmethod
    def _default_scenario(name: str) -> NetworkScenario:
        return NetworkScenario(
            name=name,
            latency_ms=(100, 200),
            jitter_ms=40,
            drop_rate=0.02,
            queue_limit=32,
            description="Fallback scenario with moderate latency.",
        )
