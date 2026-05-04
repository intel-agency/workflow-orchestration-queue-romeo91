"""Abstract interface definitions for OS-APOW.

Provides the ITaskQueue protocol that all queue implementations
must satisfy, enabling provider-agnostic queue operations.
"""

from workflow_orchestration_queue.interfaces.i_task_queue import ITaskQueue

__all__ = ["ITaskQueue"]
