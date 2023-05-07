
from enum import Enum, unique


@unique
class NotifyStatusType(Enum):
    """
    通知嵌入(Embed)的状态
    """
    RUNNING = "RUNNING"
    FINISHED = "FINISHED",
    FAILED = "FAILED",
