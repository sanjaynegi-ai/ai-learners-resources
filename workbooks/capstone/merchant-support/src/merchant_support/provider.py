"""Explicitly selected paid evaluation adapter, never enabled by the HTTP service."""
import asyncio
import json
import sys


class BedrockProvider:
    kind = "real-model-unreviewed"

    def __init__(self, model):
        if not isinstance(model, str) or not 1 <= len(model) <= 2048:
            raise ValueError("invalid model")
        self.model = model
        self.last_usage = None
        self.last_error = None

    async def generate(self, evidence):
        self.last_usage = None
        self.last_error = None
        proc = await asyncio.create_subprocess_exec(sys.executable, "-m", "merchant_support.provider_worker",
            self.model, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL)
        try:
            stdout, _ = await proc.communicate(json.dumps(evidence).encode())
            if proc.returncode or len(stdout) > 8192:
                raise RuntimeError("provider failed")
            value = json.loads(stdout)
            if "error" in value:
                self.last_error = value["error"]
                raise RuntimeError("provider service rejected request")
            self.last_usage = value["usage"]
            return value["proposal"]
        finally:
            if proc.returncode is None:
                proc.kill()
                await proc.wait()  # Local process exit does not cancel remote billing/work.
