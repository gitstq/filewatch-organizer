"""File organizer - executes organization actions"""
import os, shutil, logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime

class FileOrganizer:
    def __init__(self, config: Optional[Dict] = None, dry_run: bool = False):
        self.config = config or {}
        self.dry_run = dry_run or self.config.get("dry_run", False)
        self.history: List[Dict] = []
        self.callbacks: List[Callable[[Dict], None]] = []
        log_level = self.config.get("log_level", "INFO")
        logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('FileOrganizer')
    
    def on_action(self, callback: Callable[[Dict], None]) -> None:
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, action_result: Dict) -> None:
        for callback in self.callbacks:
            try: callback(action_result)
            except Exception as e: self.logger.error(f"Error in action callback: {e}")
    
    def execute_action(self, action: Dict) -> Dict:
        operation = action.get("operation")
        source = action.get("source")
        result = {"timestamp": datetime.now().isoformat(), "operation": operation, "source": source, "success": False, "message": ""}
        try:
            if operation == "move": result.update(self._execute_move(action))
            elif operation == "copy": result.update(self._execute_copy(action))
            elif operation == "delete": result.update(self._execute_delete(action))
            elif operation == "rename": result.update(self._execute_rename(action))
            elif operation == "archive": result.update(self._execute_archive(action))
            else: result["message"] = f"Unknown operation: {operation}"
        except Exception as e:
            result["message"] = f"Error executing action: {str(e)}"
            self.logger.error(result["message"])
        self.history.append(result)
        self._notify_callbacks(result)
        return result
    
    def _execute_move(self, action: Dict) -> Dict:
        source, destination = action["source"], action["destination"]
        create_dirs = action.get("create_dirs", True)
        if not os.path.exists(source): return {"success": False, "message": f"Source does not exist: {source}"}
        if os.path.exists(destination): destination = self._generate_unique_path(destination)
        if self.dry_run: return {"success": True, "message": f"[DRY RUN] Would move: {source} -> {destination}", "destination": destination}
        if create_dirs: os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.move(source, destination)
        return {"success": True, "message": f"Moved: {source} -> {destination}", "destination": destination}
    
    def _execute_copy(self, action: Dict) -> Dict:
        source, destination = action["source"], action["destination"]
        create_dirs = action.get("create_dirs", True)
        if not os.path.exists(source): return {"success": False, "message": f"Source does not exist: {source}"}
        if os.path.exists(destination): destination = self._generate_unique_path(destination)
        if self.dry_run: return {"success": True, "message": f"[DRY RUN] Would copy: {source} -> {destination}", "destination": destination}
        if create_dirs: os.makedirs(os.path.dirname(destination), exist_ok=True)
        if os.path.isdir(source): shutil.copytree(source, destination)
        else: shutil.copy2(source, destination)
        return {"success": True, "message": f"Copied: {source} -> {destination}", "destination": destination}
    
    def _execute_delete(self, action: Dict) -> Dict:
        source, reason = action["source"], action.get("reason", "")
        if not os.path.exists(source): return {"success": False, "message": f"Source does not exist: {source}"}
        if self.dry_run: return {"success": True, "message": f"[DRY RUN] Would delete: {source} ({reason})"}
        if os.path.isdir(source): shutil.rmtree(source)
        else: os.remove(source)
        return {"success": True, "message": f"Deleted: {source} ({reason})"}
    
    def _execute_rename(self, action: Dict) -> Dict:
        source, new_name = action["source"], action["new_name"]
        if not os.path.exists(source): return {"success": False, "message": f"Source does not exist: {source}"}
        dest_dir = os.path.dirname(source)
        destination = os.path.join(dest_dir, new_name)
        if os.path.exists(destination): destination = self._generate_unique_path(destination)
        if self.dry_run: return {"success": True, "message": f"[DRY RUN] Would rename: {source} -> {destination}", "destination": destination}
        os.rename(source, destination)
        return {"success": True, "message": f"Renamed: {source} -> {destination}", "destination": destination}
    
    def _execute_archive(self, action: Dict) -> Dict:
        source, destination = action["source"], action["destination"]
        archive_format = action.get("format", "zip")
        if not os.path.exists(source): return {"success": False, "message": f"Source does not exist: {source}"}
        if not destination.endswith(f".{archive_format}"): destination += f".{archive_format}"
        if os.path.exists(destination): destination = self._generate_unique_path(destination)
        if self.dry_run: return {"success": True, "message": f"[DRY RUN] Would archive: {source} -> {destination}", "destination": destination}
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        base_name = destination.replace(f".{archive_format}", "")
        root_dir = source if os.path.isdir(source) else os.path.dirname(source)
        base_dir = os.path.basename(source) if os.path.isdir(source) else None
        archive_path = shutil.make_archive(base_name=base_name, format=archive_format, root_dir=root_dir, base_dir=base_dir)
        return {"success": True, "message": f"Archived: {source} -> {archive_path}", "destination": archive_path}
    
    def _generate_unique_path(self, path: str) -> str:
        if not os.path.exists(path): return path
        directory, filename = os.path.dirname(path), os.path.basename(path)
        name, ext = os.path.splitext(filename)
        counter = 1
        while True:
            new_path = os.path.join(directory, f"{name}_{counter}{ext}")
            if not os.path.exists(new_path): return new_path
            counter += 1
    
    def execute_batch(self, actions: List[Dict]) -> List[Dict]:
        return [self.execute_action(action) for action in actions]
    
    def get_history(self) -> List[Dict]: return self.history.copy()
    def clear_history(self) -> None: self.history.clear()
    def get_stats(self) -> Dict:
        total = len(self.history)
        successful = sum(1 for h in self.history if h.get("success"))
        operations = {}
        for h in self.history:
            op = h.get("operation", "unknown")
            operations[op] = operations.get(op, 0) + 1
        return {"total_actions": total, "successful": successful, "failed": total - successful, "success_rate": successful / total if total > 0 else 0, "operations": operations}
