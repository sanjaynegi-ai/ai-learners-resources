"""Virtual time for the simulation.

VirtualTimeLoop is a normal asyncio event loop whose clock is virtual: whenever nothing is ready to run, it jumps
straight to the next scheduled timer instead of waiting. Timeouts, sleeps, cancellation and task interleaving all
behave as in production asyncio, but a 60-second scenario finishes instantly and identically on every machine.
(Wall-clock scaling is unreliable: on Windows, timers tick about every 15.6 ms.) Durations are in simulated seconds.
"""
import asyncio
import selectors


class _VirtualSelector(selectors.BaseSelector):
    """Never touches the OS. `select(timeout)` advances virtual time by `timeout` and reports no I/O events."""

    def __init__(self, loop: "VirtualTimeLoop") -> None:
        self._loop, self._keys = loop, {}

    def register(self, fileobj, events, data=None):
        fd = fileobj if isinstance(fileobj, int) else fileobj.fileno()
        key = selectors.SelectorKey(fileobj, fd, events, data)
        self._keys[fd] = key
        return key

    def unregister(self, fileobj):
        fd = fileobj if isinstance(fileobj, int) else fileobj.fileno()
        return self._keys.pop(fd)

    def select(self, timeout=None):
        if timeout is None:
            raise RuntimeError("Simulation deadlock: nothing is runnable and no timer is scheduled")
        self._loop.virtual_now += max(0.0, timeout)
        return []

    def get_map(self):
        return self._keys

    def close(self):
        self._keys.clear()


class VirtualTimeLoop(asyncio.SelectorEventLoop):
    def __init__(self) -> None:
        self.virtual_now = 0.0
        super().__init__(selector=_VirtualSelector(self))

    def time(self) -> float:
        return self.virtual_now


def run_simulated(coroutine):
    """Run a coroutine on a fresh virtual-time loop (asyncio.Runner's loop_factory exists from Python 3.11)."""
    with asyncio.Runner(loop_factory=VirtualTimeLoop) as runner:
        return runner.run(coroutine)


class Clock:
    """Thin wrapper so service code reads naturally; under VirtualTimeLoop all of these are virtual seconds."""

    def now(self) -> float:
        return asyncio.get_running_loop().time()

    async def sleep(self, seconds: float) -> None:
        await asyncio.sleep(max(0.0, seconds))

    def timeout(self, seconds: float):
        return asyncio.timeout(max(0.0, seconds))


class Deadline:
    """An absolute end time created once, at the edge, and passed down. Every wait inside it uses `remaining()`."""

    def __init__(self, clock: Clock, seconds: float) -> None:
        self.clock = clock
        self.ends_at = clock.now() + seconds

    def remaining(self) -> float:
        return max(0.0, self.ends_at - self.clock.now())

    def expired(self) -> bool:
        return self.remaining() <= 0
