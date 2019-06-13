import random
from dataclasses import asdict, dataclass, field

import pandas as pd
from faker import Faker

from .xapi import (
    XAPI_VIDEO_DEFAULT_SPEED,
    XAPI_VIDEO_SPEED_VALUES,
    XAPI_VIDEO_VERB_COMPLETED,
    XAPI_VIDEO_VERB_INITIALIZED,
    XAPI_VIDEO_VERB_INTERACTED,
    XAPI_VIDEO_VERB_PAUSED,
    XAPI_VIDEO_VERB_PLAYED,
    XAPI_VIDEO_VERB_SEEKED,
    XAPI_VIDEO_VERB_TERMINATED,
    XAPI_VIDEO_VERBS,
)

fake = Faker()


@dataclass
class xAPIVideoMetricFactory:
    """Base data collected from xAPI video statements"""

    _id: str = field(default_factory=fake.uuid4)
    timestamp: str = field(default_factory=fake.iso8601)
    verb: str = field(default_factory=lambda: random.choice(XAPI_VIDEO_VERBS))
    actor: str = field(default_factory=fake.sha1)
    object_id: str = field(default_factory=lambda: "uuid://{}".format(fake.uuid4()))
    length: float = field(default_factory=lambda: random.uniform(120, 900))
    speed: float = 1.0
    time: float = None
    time_from: float = None
    time_to: float = None

    def __post_init__(self):
        """Generate values for field-dependent fields"""

        if self.verb == XAPI_VIDEO_VERB_PLAYED:
            self.time = random.betavariate(2, 5) * self.length
        elif self.verb == XAPI_VIDEO_VERB_PAUSED:
            self.time = random.betavariate(2, 3) * self.length
        elif self.verb == XAPI_VIDEO_VERB_TERMINATED:
            self.time = random.betavariate(5, 1) * self.length
        elif self.verb == XAPI_VIDEO_VERB_SEEKED:
            self.time_from = random.betavariate(2, 4) * self.length
            self.time_to = random.betavariate(1, 5) * self.length
        elif self.verb == XAPI_VIDEO_VERB_INTERACTED:
            self.time = random.betavariate(2, 5) * self.length
            r = random.betavariate(2, 5)
            if r < 0.5:
                self.speed = random.choice(
                    [
                        s
                        for s in XAPI_VIDEO_SPEED_VALUES
                        if s != XAPI_VIDEO_DEFAULT_SPEED
                    ]
                )


class xAPIVideoMetricsFactory:
    """A factory for xAPI video metrics DataFrames"""

    @staticmethod
    def build(count=10, start_date="-1y", end_date="now", **kwargs):
        """Generate a collection of xAPI Video statement extracted metrics"""

        metrics = []
        for _ in range(count):
            metrics.append(
                asdict(
                    xAPIVideoMetricFactory(
                        timestamp=fake.date_time_between(
                            start_date=start_date, end_date=end_date
                        ).isoformat(),
                        **kwargs
                    )
                )
            )

        # Generate a DataFrame sorted by timestamp as a date time index
        metrics = pd.DataFrame(metrics)
        metrics["timestamp"] = pd.to_datetime(metrics["timestamp"])
        metrics.set_index("timestamp", inplace=True)
        metrics.sort_values(by=["timestamp"], inplace=True)

        return metrics
