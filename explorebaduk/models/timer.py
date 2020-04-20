import time
from abc import ABCMeta, abstractmethod

from explorebaduk.constants import MOVE_DELAY, TimeSystem
from explorebaduk.exceptions import TimerError


class Timer(metaclass=ABCMeta):
    time_system = None

    def __init__(
        self,
        main_time: int = 0,
        overtime: int = 0,
        periods: int = 1,
        stones: int = 1,
        bonus: int = 0,
        time_left: float = None,
    ):
        self.main_time = main_time
        self.overtime = overtime
        self.periods = periods
        self.stones = stones
        self.bonus = bonus
        self.delay = MOVE_DELAY

        self.started_at = None
        self._time_left = time_left or self.initial_time_left()

    @property
    def started(self):
        return self.started_at is not None

    @property
    def time_left(self) -> float:
        if self.started:
            return self._time_left + max(self.started_at - time.monotonic(), 0)
        return self._time_left

    def start(self) -> float:
        if self.started:
            raise TimerError("Already started")

        self.started_at = time.monotonic() + self.delay

        return self.time_left

    def stop(self) -> float:
        if not self.started:
            raise TimerError("Not started")

        time_used = time.monotonic() - self.started_at

        if time_used > 0:
            self.process_time(time_used)

            if self._time_left < 0:
                raise TimerError(f"Out of time")

        self.started_at = None

        return self.time_left

    @abstractmethod
    def initial_time_left(self):
        pass

    @abstractmethod
    def process_time(self, time_used: float) -> None:
        pass


class NoTimeTimer(Timer):
    """
    No time limit
    """

    time_system = TimeSystem.NO_TIME

    def initial_time_left(self):
        return 0

    def start(self):
        pass

    def stop(self):
        pass

    def process_time(self, time_used: float) -> None:
        pass


class AbsoluteTimer(Timer):
    """
    Each player is assigned a fixed amount of time for the whole game.
    If a player's main time expires, they generally lose the game.
    """

    time_system = TimeSystem.ABSOLUTE

    def initial_time_left(self):
        return self.main_time

    def process_time(self, time_used: float) -> None:
        self._time_left -= time_used


class ByoyomiTimer(Timer):
    """
    After the main time is depleted, a player has a certain number of periods.
    If a move is completed before the time expires, the time period resets and restarts the next turn.
    If a move is not completed within a time period, the time period will expire, and the next time period begins.
    """

    time_system = TimeSystem.BYOYOMI

    def initial_time_left(self):
        return self.main_time + self.overtime * self.periods

    def process_time(self, time_used: float) -> None:
        self._time_left -= time_used

        periods_left = self._time_left // self.overtime

        if 0 <= periods_left < self.periods:
            self._time_left = self.overtime * (periods_left + 1)


class CanadianTimer(Timer):
    """
    After the main time is depleted, a player must make a certain number of moves within a certain period of time.
    """

    time_system = TimeSystem.CANADIAN

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stones_left = self.stones

    def initial_time_left(self):
        return self.main_time + self.overtime * self.periods

    def process_time(self, time_used: float) -> None:
        self._time_left -= time_used

        if self._time_left < self.overtime:
            self.stones_left -= 1

            # next overtime period
            if self.stones_left == 0:
                self._time_left = self.overtime
                self.stones_left = self.stones

        else:
            self.stones_left = self.stones


class FischerTimer(Timer):
    """
    A specified amount of time is added to the players main time each move,
    unless the player's main time ran out before they completed their move.
    """

    time_system = TimeSystem.FISCHER

    def initial_time_left(self):
        return self.main_time

    def process_time(self, time_used: float) -> None:
        self._time_left -= time_used + self.bonus


class TimeControl:
    def __init__(
            self,
            time_system: TimeSystem,
            main_time: int = 0,
            overtime: int = 0,
            period: int = 1,
            stones: int = 1,
            bonus: int = 0,
            **kwargs
    ):
        self.time_system = time_system
        self.main_time = main_time
        self.overtime = overtime
        self.periods = period
        self.stones = stones
        self.bonus = bonus

    def __str__(self):
        return f"TS[{self.time_system}M{self.main_time}O{self.overtime}P{self.periods}S{self.stones}B{self.bonus}]"

    def timer(self) -> Timer:
        if self.time_system is TimeSystem.NO_TIME:
            return NoTimeTimer()
        if self.time_system is TimeSystem.ABSOLUTE:
            return AbsoluteTimer(main_time=self.main_time)
        if self.time_system is TimeSystem.BYOYOMI:
            return ByoyomiTimer(main_time=self.main_time, overtime=self.overtime, periods=self.periods)
        if self.time_system is TimeSystem.CANADIAN:
            return CanadianTimer(main_time=self.main_time, overtime=self.overtime, stones=self.stones)
        if self.time_system is TimeSystem.FISCHER:
            return FischerTimer(main_time=self.main_time, bonus=self.bonus)
        raise NotImplementedError("Timer not implemented")
