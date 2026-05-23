"""Configuration management for FileWatch-Organizer"""
import os, json
from pathlib import Path
from typing import Dict, List, Any, Optional

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "watch_paths": [],
    "organization_rules": [],
    "global_settings": {
        "recursive": True, "follow_symlinks": False, "ignore_hidden": True,
        "dry_run": False, "log_level": "INFO", "max_workers": 4, "debounce_seconds": 1.0
    },
    "file_types": {
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
        "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md"],
        "spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
        "presentations": [".ppt", ".pptx", ".odp"],
        "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
        "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
        "code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".rb", ".php"],
        "executables": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".AppImage"],
        "data": [".json", ".xml", ".yaml", ".yml", ".sql", ".db", ".sqlite"]
    },
    "ignore_patterns": ["*.tmp", "*.temp", "*.swp", "*.swo", ".DS_Store", "Thumbs.db", "desktop.ini", "~$*"]
}

class Config:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        config_dir = Path.home() / ".config" / "filewatch-organizer"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return self._merge_config(DEFAULT_CONFIG, config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load config: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save(self) -> None:
        try:
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    @property
    def watch_paths(self) -> List[str]: return self._config.get("watch_paths", [])
    @watch_paths.setter
    def watch_paths(self, paths: List[str]) -> None: self._config["watch_paths"] = paths
    @property
    def organization_rules(self) -> List[Dict]: return self._config.get("organization_rules", [])
    @property
    def global_settings(self) -> Dict: return self._config.get("global_settings", {})
    @property
    def file_types(self) -> Dict[str, List[str]]: return self._config.get("file_types", {})
    @property
    def ignore_patterns(self) -> List[str]: return self._config.get("ignore_patterns", [])
    
    def add_watch_path(self, path: str, recursive: Optional[bool] = None) -> None:
        watch_entry = {"path": os.path.abspath(path), "recursive": recursive if recursive is not None else self.global_settings.get("recursive", True)}
        if watch_entry not in self._config["watch_paths"]:
            self._config["watch_paths"].append(watch_entry)
    
    def remove_watch_path(self, path: str) -> None:
        self._config["watch_paths"] = [wp for wp in self._config["watch_paths"] if wp.get("path") != os.path.abspath(path)]
    
    def add_organization_rule(self, rule: Dict) -> None:
        if "name" not in rule: raise ValueError("Rule must have a 'name' field")
        self._config["organization_rules"].append(rule)
    
    def create_default_config(self) -> None:
        self._config = DEFAULT_CONFIG.copy()
        self.save()

def get_preset_config(preset_name: str) -> Dict[str, Any]:
    presets = {
        "downloads": {
            "name": "Downloads Folder Organizer",
            "description": "Organize Downloads folder by file type and date",
            "rules": [
                {"name": "sort_by_type", "enabled": True, "action": "organize_by_type", "target_folder": "{watch_path}/Organized/{file_type}"},
                {"name": "sort_by_date", "enabled": True, "action": "organize_by_date", "date_format": "%Y/%m", "target_folder": "{watch_path}/ByDate/{date}"}
            ]
        },
        "workspace": {
            "name": "Development Workspace",
            "description": "Organize development workspace by project type",
            "rules": [
                {"name": "project_detection", "enabled": True, "action": "detect_project_type", "target_folder": "{watch_path}/Projects/{project_type}"},
                {"name": "archive_old", "enabled": True, "action": "archive_by_age", "max_age_days": 90, "target_folder": "{watch_path}/Archive"}
            ]
        },
        "documents": {
            "name": "Document Library",
            "description": "Organize documents by category and date",
            "rules": [
                {"name": "by_category", "enabled": True, "action": "categorize_documents", "target_folder": "{watch_path}/{category}"},
                {"name": "deduplicate", "enabled": True, "action": "remove_duplicates", "method": "hash"}
            ]
        }
    }
    return presets.get(preset_name, {})
