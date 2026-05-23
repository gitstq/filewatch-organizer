"""
FileWatch-Organizer: Lightweight File System Intelligent Monitoring & Auto-Organization Engine
轻量级文件系统智能监控与自动整理引擎

A zero-dependency, cross-platform file monitoring and auto-organization tool.
"""

__version__ = "1.0.0"
__author__ = "FileWatch Team"
__license__ = "MIT"

from .watcher import FileWatcher
from .organizer import FileOrganizer
from .rules import RuleEngine
from .config import Config

__all__ = ["FileWatcher", "FileOrganizer", "RuleEngine", "Config"]
