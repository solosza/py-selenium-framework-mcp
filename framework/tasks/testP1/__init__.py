"""testP1 Tasks - Task modules for ParaBank test workflow."""

from tasks.testP1.auth_tasks import AuthTasks
from tasks.testP1.transfer_tasks import TransferTasks

__all__ = ['AuthTasks', 'TransferTasks']
