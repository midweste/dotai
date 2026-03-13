"""OpenRouter API client — model info, pricing, rate limits, and validation."""

import sys
import threading
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.config import Config


class OpenRouterAPI:
    """Centralized OpenRouter API access — models, pricing, rate limits.

    All model detection, capability checks, and rate info go through this class.
    LLMClient uses it for requests; BuildAgent uses it for concurrency/cost decisions.
    """

    def __init__(self, config: Optional["Config"] = None):
        if config is None:
            from src.config import Config
            config = Config.from_env()
        self._api_key = config.OPENROUTER_API_KEY
        self._api_url = config.MEMORY_BUILD_API_URL
        self._min_context_length = config.MIN_CONTEXT_LENGTH

        # Caches
        self._models_cache: Optional[list[dict]] = None
        self._key_info_cache: Optional[dict] = None

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def api_url(self) -> str:
        return self._api_url

    @property
    def base_url(self) -> str:
        return self._api_url.rsplit("/chat/completions", 1)[0]

    # -- Models API --

    def _fetch_models(self) -> list[dict]:
        """Fetch and cache the full model list from OpenRouter."""
        if self._models_cache is not None:
            return self._models_cache

        import requests
        try:
            resp = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            self._models_cache = resp.json().get("data", [])
        except Exception:
            self._models_cache = []
        return self._models_cache or []

    def get_model_info(self, model_id: str) -> dict:
        """Get model info from OpenRouter API. Raises if model not found.

        Returns dict with: context_length, max_completion_tokens, name,
        supported_parameters, pricing, is_free.
        """
        models = self._fetch_models()
        raw = next((m for m in models if m.get("id") == model_id), None)
        if raw is None:
            raise RuntimeError(
                f"Model '{model_id}' not found on OpenRouter. "
                f"Check MEMORY_EXTRACT_MODEL or MEMORY_REASONING_MODEL in .env."
            )

        pricing = raw.get("pricing", {})
        return {
            "context_length": raw.get("context_length", 32_000),
            "max_completion_tokens": raw.get(
                "top_provider", {}
            ).get("max_completion_tokens", 16_384),
            "name": raw.get("name", model_id),
            "supported_parameters": raw.get("supported_parameters", []),
            "pricing": {
                "prompt": float(pricing.get("prompt", "0")),
                "completion": float(pricing.get("completion", "0")),
            },
            "is_free": (
                pricing.get("prompt") == "0"
                and pricing.get("completion") == "0"
            ),
        }

    def get_fallback_info(self, model_id: str) -> Optional[dict]:
        """Like get_model_info but returns None instead of raising."""
        try:
            return self.get_model_info(model_id)
        except RuntimeError:
            return None

    def validate_model(self, model_id: str) -> None:
        """Raise RuntimeError if the model is unsuitable for memory extraction.

        Checks:
          1. Context window >= MIN_CONTEXT_LENGTH
          2. Model supports structured_outputs (json_schema)
        """
        info = self.get_model_info(model_id)
        ctx = info["context_length"]
        if ctx < self._min_context_length:
            raise RuntimeError(
                f"Model '{model_id}' context window ({ctx:,} tokens) is too "
                f"small. Minimum required: {self._min_context_length:,}. "
                f"Use a model with a larger context window."
            )
        supported = info.get("supported_parameters", [])
        if supported and "structured_outputs" not in supported:
            raise RuntimeError(
                f"Model '{model_id}' does not support structured outputs "
                f"(json_schema). Only models with strict JSON schema support "
                f"are allowed. See .env for verified models."
            )

    # -- Key / Rate Limit API --

    def get_key_info(self) -> dict:
        """Query /api/v1/key for account-level rate and usage info.

        Returns dict with: is_free_tier, usage_daily, limit_remaining,
        free_requests_per_minute, free_requests_per_day.
        """
        if self._key_info_cache is not None:
            return self._key_info_cache

        import requests
        try:
            resp = requests.get(
                f"{self.base_url}/key",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
        except Exception:
            # API unreachable — conservative defaults
            data = {"is_free_tier": True}

        is_free_tier = data.get("is_free_tier", True)
        self._key_info_cache = {
            "is_free_tier": is_free_tier,
            "usage_daily": data.get("usage_daily", 0),
            "limit_remaining": data.get("limit_remaining"),
            # OpenRouter docs: free models = 20 req/min
            # Daily: 50 if free tier, 1000 if purchased $10+ credits
            "free_requests_per_minute": 20,
            "free_requests_per_day": 50 if is_free_tier else 1000,
        }
        return self._key_info_cache

    # -- Concurrency --

    def create_rate_limiter(self, model_id: str) -> "RateLimiter":
        """Create a RateLimiter tuned for this model's actual rate limits.

        Detection logic:
          - Free models (pricing $0): 20 RPM (OpenRouter hard limit)
          - Paid models with credits: ~$1 balance = 1 RPS, max 500 RPS
          - Falls back to 20 RPM if detection fails
        """
        model_info = self.get_model_info(model_id)
        key_info = self.get_key_info()
        is_free_model = model_info.get("is_free", True)

        if is_free_model:
            # Free models: hard 20 RPM limit regardless of account tier
            rpm = 20
            reason = "free model"
        else:
            # Paid models: ~$1 balance = 1 RPS, max 500 RPS
            balance = key_info.get("limit_remaining")
            if balance is not None and balance > 0:
                rps = min(balance, 500)
                rpm = int(rps * 60)
                reason = f"${balance:.2f} balance"
            else:
                # No balance info — conservative default
                rpm = 20
                reason = "unknown balance"

        print(
            f"  rate limit: {rpm} RPM ({reason})",
            file=sys.stderr, flush=True,
        )
        return RateLimiter(rpm=rpm)

    # -- Cost Estimation --

    def estimate_cost(
        self, model_id: str, input_tokens: int, output_tokens: int = 0,
    ) -> float:
        """Estimate cost in USD for a given token count."""
        info = self.get_model_info(model_id)
        pricing = info.get("pricing", {"prompt": 0, "completion": 0})
        return (
            input_tokens * pricing["prompt"]
            + output_tokens * pricing["completion"]
        )


class RateLimiter:
    """Sliding-window rate limiter with 429 emergency braking.

    Two layers of protection:
    1. Proactive pacing: acquire() enforces a sliding-window RPM limit,
       sleeping until a slot opens rather than firing and getting rejected.
    2. Reactive braking: on_rate_limit() closes the gate for all threads
       when a 429 is received (safety net for miscalculated limits).

    Thread-safe. Designed for use with ThreadPoolExecutor.
    """

    def __init__(self, rpm: int = 20):
        self._rpm = rpm
        # Sliding window: timestamps of recent request starts
        self._window: list[float] = []
        self._window_lock = threading.Lock()
        # Emergency brake (429 handling)
        self._gate = threading.Event()
        self._gate.set()  # Start open
        self._brake_lock = threading.Lock()
        self._consecutive_429s = 0
        self._cooldown_until = 0.0
        self._total_429s = 0

    @property
    def rpm(self) -> int:
        return self._rpm

    @property
    def total_429s(self) -> int:
        return self._total_429s

    def acquire(self) -> None:
        """Call before each API request. Paces to stay within RPM.

        Blocks if:
        1. The sliding window is full (proactive pacing), OR
        2. The emergency brake is engaged (429 received)
        """
        # Wait for emergency brake to release
        self._gate.wait()

        # Sliding-window pacing
        while True:
            now = time.monotonic()
            with self._window_lock:
                # Evict entries older than 60s
                cutoff = now - 60.0
                self._window = [t for t in self._window if t > cutoff]

                if len(self._window) < self._rpm:
                    # Slot available — record and proceed
                    self._window.append(now)
                    return

                # Window full — calculate sleep until oldest entry expires
                sleep_until = self._window[0] + 60.0

            wait = sleep_until - now
            if wait > 0:
                time.sleep(wait + 0.05)  # small buffer to avoid edge-case ties

            # Re-check emergency brake after sleeping
            self._gate.wait()

    def on_success(self) -> None:
        """Call after a successful response."""
        with self._brake_lock:
            self._consecutive_429s = 0

    def on_rate_limit(self, retry_after: Optional[float] = None) -> None:
        """Call when a 429 is received. Closes the gate for all threads.

        Args:
            retry_after: Value from Retry-After header (seconds).
                         Falls back to exponential backoff if None.
        """
        with self._brake_lock:
            self._total_429s += 1
            self._consecutive_429s += 1

            if retry_after and retry_after > 0:
                wait = retry_after
            else:
                wait = min(2 ** self._consecutive_429s, 30)

            target = time.monotonic() + wait

            if target <= self._cooldown_until:
                return  # Another thread already set a longer cooldown

            self._cooldown_until = target
            self._gate.clear()

            # Also reduce RPM to back off more aggressively
            new_rpm = max(self._rpm // 2, 5)
            if new_rpm < self._rpm:
                self._rpm = new_rpm
                print(
                    f"      rate limited — reducing to {self._rpm} RPM, "
                    f"pausing {wait:.0f}s (429 #{self._total_429s})",
                    file=sys.stderr, flush=True,
                )
            else:
                print(
                    f"      rate limited — pausing all workers for {wait:.0f}s "
                    f"(429 #{self._total_429s})",
                    file=sys.stderr, flush=True,
                )

        timer = threading.Timer(wait, self._release)
        timer.daemon = True
        timer.start()

    def _release(self) -> None:
        """Re-open the gate after cooldown."""
        with self._brake_lock:
            if time.monotonic() >= self._cooldown_until:
                self._gate.set()
