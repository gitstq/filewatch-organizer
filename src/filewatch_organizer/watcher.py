"""File system watcher module using native Python libraries"""
import os, time, threading
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set
from datetime import datetime

class FileEvent:
    EVENT_CREATED = "created"
    EVENT_MODIFIED = "modified"
    EVENT_DELETED = "deleted"
    EVENT_MOVED = "moved"
    
    def __init__(self, event_type: str, src_path: str, dest_path: Optional[str] = None,
                 is_directory: bool = False, timestamp: Optional[float] = None):
        self.event_type = event_type
        self.src_path = src_path
        self.dest_path = dest_path
        self.is_directory = is_directory
        self.timestamp = timestamp or time.time()
    
    def __repr__(self):
        if self.event_type == self.EVENT_MOVED:
            return f"FileEvent({self.event_type}: {self.src_path} -> {self.dest_path})"
        return f"FileEvent({self.event_type}: {self.src_path})"
    
    @property
    def filename(self) -> str: return os.path.basename(self.src_path)
    @property
    def extension(self) -> str: return Path(self.src_path).suffix.lower()

class FileWatcher:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.watch_paths: List[Dict] = []
        self.callbacks: List[Callable[[FileEvent], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._file_snapshots: Dict[str, Dict] = {}
        self._snapshot_lock = threading.Lock()
        self._debounce_seconds = self.config.get("debounce_seconds", 1.0)
        self._pending_events: Dict[str, float] = {}
        self.stats = {"events_processed": 0, "files_watched": 0, "start_time": None}
    
    def add_watch_path(self, path: str, recursive: bool = True) -> bool:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path) or not os.path.isdir(abs_path):
            print(f"Warning: Path does not exist or is not a directory: {abs_path}")
            return False
        watch_entry = {"path": abs_path, "recursive": recursive}
        if watch_entry not in self.watch_paths:
            self.watch_paths.append(watch_entry)
            self._take_snapshot(abs_path, recursive)
            return True
        return False
    
    def remove_watch_path(self, path: str) -> bool:
        abs_path = os.path.abspath(path)
        original_len = len(self.watch_paths)
        self.watch_paths = [wp for wp in self.watch_paths if wp["path"] != abs_path]
        with self._snapshot_lock:
            paths_to_remove = [p for p in self._file_snapshots if p.startswith(abs_path)]
            for p in paths_to_remove: del self._file_snapshots[p]
        return len(self.watch_paths) < original_len
    
    def on_event(self, callback: Callable[[FileEvent], None]) -> None:
        self.callbacks.append(callback)
    
    def _take_snapshot(self, path: str, recursive: bool = True) -> None:
        snapshot = {}
        try:
            if recursive:
                for root, dirs, files in os.walk(path):
                    for name in dirs + files:
                        full_path = os.path.join(root, name)
                        try:
                            stat = os.stat(full_path)
                            snapshot[full_path] = {"mtime": stat.st_mtime, "size": stat.st_size, "is_dir": os.path.isdir(full_path)}
                        except (OSError, IOError): continue
            else:
                for entry in os.scandir(path):
                    try:
                        stat = entry.stat()
                        snapshot[entry.path] = {"mtime": stat.st_mtime, "size": stat.st_size, "is_dir": entry.is_dir()}
                    except (OSError, IOError): continue
        except Exception as e: print(f"Error taking snapshot of {path}: {e}")
        with self._snapshot_lock:
            self._file_snapshots.update(snapshot)
            self.stats["files_watched"] = len(self._file_snapshots)
    
    def _detect_changes(self, path: str, recursive: bool = True) -> List[FileEvent]:
        events = []
        current_snapshot = {}
        try:
            if recursive:
                for root, dirs, files in os.walk(path):
                    for name in dirs + files:
                        full_path = os.path.join(root, name)
                        try:
                            stat = os.stat(full_path)
                            current_snapshot[full_path] = {"mtime": stat.st_mtime, "size": stat.st_size, "is_dir": os.path.isdir(full_path)}
                        except (OSError, IOError): continue
            else:
                for entry in os.scandir(path):
                    try:
                        stat = entry.stat()
                        current_snapshot[entry.path] = {"mtime": stat.st_mtime, "size": stat.st_size, "is_dir": entry.is_dir()}
                    except (OSError, IOError): continue
        except Exception as e: return events
        
        with self._snapshot_lock:
            old_snapshot = dict(self._file_snapshots)
            for file_path, info in current_snapshot.items():
                if file_path not in old_snapshot:
                    events.append(FileEvent(FileEvent.EVENT_CREATED, file_path, is_directory=info["is_dir"]))
                elif old_snapshot[file_path]["mtime"] != info["mtime"] or old_snapshot[file_path]["size"] != info["size"]:
                    events.append(FileEvent(FileEvent.EVENT_MODIFIED, file_path, is_directory=info["is_dir"]))
            for file_path, info in old_snapshot.items():
                if file_path not in current_snapshot:
                    events.append(FileEvent(FileEvent.EVENT_DELETED, file_path, is_directory=info["is_dir"]))
            self._file_snapshots = current_snapshot
            self.stats["files_watched"] = len(self._file_snapshots)
        return events
    
    def _process_events(self, events: List[FileEvent]) -> None:
        current_time = time.time()
        for event in events:
            event_key = f"{event.event_type}:{event.src_path}"
            if event_key in self._pending_events:
                if current_time - self._pending_events[event_key] < self._debounce_seconds: continue
            self._pending_events[event_key] = current_time
            for callback in self.callbacks:
                try: callback(event)
                except Exception as e: print(f"Error in event callback: {e}")
            self.stats["events_processed"] += 1
        self._pending_events = {k: v for k, v in self._pending_events.items() if current_time - v < self._debounce_seconds * 2}
    
    def _watch_loop(self) -> None:
        poll_interval = self.config.get("poll_interval", 1.0)
        while not self._stop_event.is_set():
            all_events = []
            for watch_entry in self.watch_paths:
                path = watch_entry["path"]
                recursive = watch_entry.get("recursive", True)
                if os.path.exists(path):
                    events = self._detect_changes(path, recursive)
                    all_events.extend(events)
            if all_events: self._process_events(all_events)
            self._stop_event.wait(poll_interval)
    
    def start(self) -> None:
        if self._running: return
        if not self.watch_paths: return
        self._running = True
        self._stop_event.clear()
        self.stats["start_time"] = datetime.now()
        for watch_entry in self.watch_paths:
            self._take_snapshot(watch_entry["path"], watch_entry.get("recursive", True))
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        if not self._running: return
        self._stop_event.set()
        self._running = False
        if self._thread and self._thread.is_alive(): self._thread.join(timeout=5.0)
    
    def is_running(self) -> bool: return self._running and self._thread and self._thread.is_alive()
    def get_stats(self) -> Dict:
        stats = self.stats.copy()
        if stats["start_time"]: stats["uptime_seconds"] = (datetime.now() - stats["start_time"]).total_seconds()
        return stats
