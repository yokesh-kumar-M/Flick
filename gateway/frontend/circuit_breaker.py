import time
import threading
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, service_name, failure_threshold=5, recovery_timeout=30, half_open_max_calls=1):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.half_open_calls = 0
        self.lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                else:
                    raise Exception(f"Circuit breaker for {self.service_name} is OPEN")

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise Exception(f"Circuit breaker for {self.service_name} is HALF_OPEN, max calls reached")
                self.half_open_calls += 1

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        with self.lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_max_calls:
                    self.state = CircuitState.CLOSED
                    self.success_count = 0

    def _on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

    def get_state(self):
        return self.state


_circuit_breakers = {}
_cb_lock = threading.Lock()


def get_circuit_breaker(service_name):
    with _cb_lock:
        if service_name not in _circuit_breakers:
            _circuit_breakers[service_name] = CircuitBreaker(service_name)
        return _circuit_breakers[service_name]