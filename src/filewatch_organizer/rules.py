"""Rule engine for file organization decisions"""
import os, re, hashlib
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

class RuleEngine:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.file_types = self.config.get("file_types", {})
        self.rules: List[Dict] = []
        self._action_handlers = {
            "organize_by_type": self._action_organize_by_type,
            "organize_by_date": self._action_organize_by_date,
            "organize_by_size": self._action_organize_by_size,
            "detect_project_type": self._action_detect_project_type,
            "categorize_documents": self._action_categorize_documents,
            "archive_by_age": self._action_archive_by_age,
            "remove_duplicates": self._action_remove_duplicates,
            "custom_pattern": self._action_custom_pattern,
        }
    
    def add_rule(self, rule: Dict) -> None:
        if "name" not in rule: raise ValueError("Rule must have a 'name' field")
        if "action" not in rule: raise ValueError("Rule must have an 'action' field")
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        original_len = len(self.rules)
        self.rules = [r for r in self.rules if r.get("name") != rule_name]
        return len(self.rules) < original_len
    
    def get_file_type(self, filepath: str) -> str:
        ext = Path(filepath).suffix.lower()
        for file_type, extensions in self.file_types.items():
            if ext in extensions: return file_type
        return "others"
    
    def get_file_hash(self, filepath: str, algorithm: str = "md5", chunk_size: int = 8192) -> Optional[str]:
        try:
            hasher = hashlib.new(algorithm)
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size): hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError): return None
    
    def find_duplicates(self, directory: str, method: str = "hash") -> Dict[str, List[str]]:
        duplicates = {}
        if method == "hash":
            file_hashes = {}
            for root, _, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    file_hash = self.get_file_hash(filepath)
                    if file_hash:
                        if file_hash in file_hashes:
                            if file_hash not in duplicates: duplicates[file_hash] = [file_hashes[file_hash]]
                            duplicates[file_hash].append(filepath)
                        else: file_hashes[file_hash] = filepath
        elif method == "name_size":
            file_keys = {}
            for root, _, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        stat = os.stat(filepath)
                        key = (filename, stat.st_size)
                        if key in file_keys:
                            if key not in duplicates: duplicates[key] = [file_keys[key]]
                            duplicates[key].append(filepath)
                        else: file_keys[key] = filepath
                    except (OSError, IOError): continue
        return duplicates
    
    def evaluate_rules(self, filepath: str, context: Optional[Dict] = None) -> List[Dict]:
        results = []
        context = context or {}
        try:
            stat = os.stat(filepath)
            file_info = {"path": filepath, "filename": os.path.basename(filepath), "extension": Path(filepath).suffix.lower(),
                        "size": stat.st_size, "mtime": stat.st_mtime, "is_directory": os.path.isdir(filepath), "file_type": self.get_file_type(filepath)}
        except (OSError, IOError): return results
        
        for rule in self.rules:
            if not rule.get("enabled", True): continue
            action = rule.get("action")
            if action in self._action_handlers:
                try:
                    result = self._action_handlers[action](file_info, rule, context)
                    if result: results.append({"rule_name": rule["name"], "action": action, "result": result})
                except Exception as e: print(f"Error evaluating rule '{rule['name']}': {e}")
        return results
    
    def _action_organize_by_type(self, file_info: Dict, rule: Dict, context: Dict) -> Optional[Dict]:
        if file_info["is_directory"]: return None
        file_type = file_info["file_type"]
        target_folder = rule.get("target_folder", "{watch_path}/{file_type}")
        watch_path = context.get("watch_path", os.path.dirname(file_info["path"]))
        target = target_folder.format(watch_path=watch_path, file_type=file_type, filename=file_info["filename"])
        return {"operation": "move", "source": file_info["path"], "destination": os.path.join(target, file_info["filename"]), "create_dirs": True}
    
    def _action_organize_by_date(self, file_info: Dict, rule: Dict, context: Dict) -> Optional[Dict]:
        if file_info["is_directory"]: return None
        date_format = rule.get("date_format", "%Y/%m")
        mtime = datetime.fromtimestamp(file_info["mtime"])
        date_folder = mtime.strftime(date_format)
        target_folder = rule.get("target_folder", "{watch_path}/{date}")
        watch_path = context.get("watch_path", os.path.dirname(file_info["path"]))
        target = target_folder.format(watch_path=watch_path, date=date_folder, filename=file_info["filename"])
        return {"operation": "move", "source": file_info["path"], "destination": os.path.join(target, file_info["filename"]), "create_dirs": True}
    
    def _action_organize_by_size(self, file_info: Dict, rule: Dict, context: Dict) -> Optional[Dict]:
        if file_info["is_directory"]: return None
        size = file_info["size"]
        size_cat = "small" if size < 1024 * 1024 else "medium" if size < 100 * 1024 * 1024 else "large"
        target_folder = rule.get("target_folder", "{watch_path}/{size_cat}")
        watch_path = context.get("watch_path", os.path.dirname(file_info["path"]))
        target = target_folder.format(watch_path=watch_path, size_cat=size_cat, filename=file_info["filename"])
        return {"operation": "move", "source": file_info["path"], "destination": os.path.join(target, file_info["filename"]), "create_dirs": True}
    
    def _action_detect_project_type(self, file_info: Dict, rule: Dict, context: Dict) -> Optional[Dict]:
        if not file_info["is_directory"]: return None
        project_indicators = {"python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"], "nodejs": ["package.json", "package-lock.json", "yarn.lock", "node_modules"],
                           "rust": ["Cargo.toml", "Cargo.lock"], "go": ["go.mod", "go.sum"], "java": ["pom.xml", "build.gradle", "gradlew"],
                           "dotnet": [".csproj", ".sln"], "docker": ["Dockerfile", "docker-compose.yml", ".dockerignore"]}
        detected_type = "generic"
        path = file_info["path"]
        try:
            entries = os.listdir(path)
            for proj_type, indicators in project_indicators.items():
                for indicator in indicators:
                    if indicator in entries: detected_type = proj_type; break
                if detected_type != "generic": break
        except OSError: pass
        target_folder = rule.get("target_folder", "{watch_path}/{project_type}")
        watch_path = context.get("watch_path", os.path.dirname(path))
        target = target_folder.format(watch_path=watch_path, project_type=detected_type, filename=file_info["filename"])
        return {"operation": "move", "source": path, "destination": os.path.join(target, file_info["filename"]), "create_dirs": True}
    
    def _action_categorize_documents(self, file_info: Dict, rule: Dict, context: Dict) -> Optional[Dict]:
        if file_info["is_directory"]: return None
        ext = file_info["extension"]
        categories = {"work": [".doc", ".docx", ".pdf", ".odt"], "spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
                     "presentations": [".ppt", ".pptx", ".odp"], "text": [".txt", ".md", ".rtf"]}
        category = "others"
        for cat, extensions in categories.items():
            if ext in extensions: category = cat; break
        target_folder = rule.get("target_folder", "{watch_path}/{category}")
        watch_path = context.get("watch_path", os.path.dirname(file_info["path"]))
        target = target_folder.format(watch_path=watch_path, category=category, filename=file_info["filename"])
        return {"operation": "move", "source": file_info["path"], "destination": os.path.join(target, file_info["filename"]), "create_dirs": True}
    
    def _action_archive_by_age(self, file_info: Dict, rule: Dict, context: Dict) -> Optional[Dict]:
        max_age_days = rule.get("max_age_days", 90)
        import time
        age_days = (time.time() - file_info["mtime"]) / (24 * 3600)
        if age_days < max_age_days: return None
        target_folder = rule.get("target_folder", "{watch_path}/Archive")
        watch_path = context.get("watch_path", os.path.dirname(file_info["path"]))
        target = target_folder.format(watch_path=watch_path, filename=file_info["filename"])
        return {"operation": "move", "source": file_info["path"], "destination": os.path.join(target, file_info["filename"]), "create_dirs": True}
    
    def _action_remove_duplicates(self, file_info: Dict, rule: Dict, context: Dict) -> Optional[Dict]:
        if file_info["is_directory"]: return None
        method = rule.get("method", "hash")
        directory = os.path.dirname(file_info["path"])
        duplicates = self.find_duplicates(directory, method)
        for key, paths in duplicates.items():
            if file_info["path"] in paths and file_info["path"] != paths[0]:
                return {"operation": "delete", "source": file_info["path"], "reason": f"Duplicate of {paths[0]}"}
        return None
    
    def _action_custom_pattern(self, file_info: Dict, rule: Dict, context: Dict) -> Optional[Dict]:
        pattern = rule.get("pattern")
        if not pattern: return None
        try:
            if re.search(pattern, file_info["filename"]):
                target_folder = rule.get("target_folder", "{watch_path}/Matched")
                watch_path = context.get("watch_path", os.path.dirname(file_info["path"]))
                target = target_folder.format(watch_path=watch_path, filename=file_info["filename"])
                return {"operation": "move", "source": file_info["path"], "destination": os.path.join(target, file_info["filename"]), "create_dirs": True}
        except re.error: pass
        return None
