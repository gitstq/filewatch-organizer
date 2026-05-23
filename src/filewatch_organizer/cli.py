"""Command Line Interface for FileWatch-Organizer"""
import os, sys, argparse, json
from pathlib import Path
from typing import Optional, List
from . import __version__
from .config import Config, get_preset_config
from .watcher import FileWatcher, FileEvent
from .organizer import FileOrganizer
from .rules import RuleEngine
from .tui import create_tui

class FileWatchCLI:
    def __init__(self):
        self.config: Optional[Config] = None
        self.watcher: Optional[FileWatcher] = None
        self.organizer: Optional[FileOrganizer] = None
        self.rule_engine: Optional[RuleEngine] = None
        self.tui = create_tui()
        self.events: List[dict] = []
    
    def run(self, args: Optional[List[str]] = None) -> int:
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        if parsed_args.version: print(f"FileWatch-Organizer v{__version__}"); return 0
        self.config = Config(parsed_args.config)
        self._init_components()
        if parsed_args.command == "watch": return self.cmd_watch(parsed_args)
        elif parsed_args.command == "organize": return self.cmd_organize(parsed_args)
        elif parsed_args.command == "config": return self.cmd_config(parsed_args)
        elif parsed_args.command == "rules": return self.cmd_rules(parsed_args)
        elif parsed_args.command == "tui": return self.cmd_tui()
        elif parsed_args.command == "preset": return self.cmd_preset(parsed_args)
        else: parser.print_help(); return 0
    
    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="filewatch-organizer", description="Lightweight File System Intelligent Monitoring & Auto-Organization Engine")
        parser.add_argument("--version", action="store_true", help="Show version information")
        parser.add_argument("--config", "-c", help="Path to configuration file")
        parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be done without making changes")
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        watch_parser = subparsers.add_parser("watch", help="Watch directories for changes")
        watch_parser.add_argument("paths", nargs="*", help="Paths to watch")
        watch_parser.add_argument("--recursive", "-r", action="store_true", default=True, help="Watch recursively")
        watch_parser.add_argument("--auto-organize", "-a", action="store_true", help="Automatically organize files on change")
        
        organize_parser = subparsers.add_parser("organize", help="Organize files in directory")
        organize_parser.add_argument("path", help="Path to organize")
        organize_parser.add_argument("--preset", "-p", choices=["downloads", "workspace", "documents"], help="Use configuration preset")
        organize_parser.add_argument("--by-type", action="store_true", help="Organize by file type")
        organize_parser.add_argument("--by-date", action="store_true", help="Organize by modification date")
        organize_parser.add_argument("--dedup", action="store_true", help="Remove duplicate files")
        
        config_parser = subparsers.add_parser("config", help="Manage configuration")
        config_parser.add_argument("--init", action="store_true", help="Initialize default configuration")
        config_parser.add_argument("--show", action="store_true", help="Show current configuration")
        config_parser.add_argument("--add-path", metavar="PATH", help="Add watch path")
        config_parser.add_argument("--remove-path", metavar="PATH", help="Remove watch path")
        
        rules_parser = subparsers.add_parser("rules", help="Manage organization rules")
        rules_parser.add_argument("--list", "-l", action="store_true", help="List all rules")
        rules_parser.add_argument("--add", help="Add rule from JSON string")
        rules_parser.add_argument("--remove", metavar="NAME", help="Remove rule by name")
        
        subparsers.add_parser("tui", help="Launch interactive TUI dashboard")
        
        preset_parser = subparsers.add_parser("preset", help="Apply configuration presets")
        preset_parser.add_argument("name", choices=["downloads", "workspace", "documents"], help="Preset name")
        preset_parser.add_argument("--path", "-p", required=True, help="Target path for preset")
        return parser
    
    def _init_components(self) -> None:
        global_settings = self.config.global_settings
        self.watcher = FileWatcher(global_settings)
        self.organizer = FileOrganizer(global_settings, dry_run=self.config.get("dry_run", False))
        self.rule_engine = RuleEngine({"file_types": self.config.file_types})
        for rule in self.config.organization_rules: self.rule_engine.add_rule(rule)
        self.watcher.on_event(self._on_file_event)
        self.organizer.on_action(self._on_organize_action)
    
    def _on_file_event(self, event: FileEvent) -> None:
        event_dict = {"event_type": event.event_type, "filename": event.filename, "src_path": event.src_path, "timestamp": event.timestamp}
        self.events.append(event_dict)
        if len(self.events) > 100: self.events.pop(0)
        if hasattr(self, 'auto_organize') and self.auto_organize: self._auto_organize(event)
    
    def _on_organize_action(self, result: dict) -> None:
        print(f"{'✓' if result.get('success') else '✗'} {result.get('message', '')}")
    
    def _auto_organize(self, event: FileEvent) -> None:
        if event.event_type in (FileEvent.EVENT_CREATED, FileEvent.EVENT_MOVED):
            context = {"watch_path": os.path.dirname(event.src_path)}
            actions = self.rule_engine.evaluate_rules(event.src_path, context)
            for action_result in actions:
                action = action_result.get("result")
                if action: self.organizer.execute_action(action)
    
    def cmd_watch(self, args) -> int:
        import signal
        if args.paths:
            for path in args.paths:
                if self.watcher.add_watch_path(path, args.recursive): print(f"Added watch path: {path}")
        else:
            for wp in self.config.watch_paths:
                if self.watcher.add_watch_path(wp["path"], wp.get("recursive", True)): print(f"Added watch path from config: {wp['path']}")
        if not self.watcher.watch_paths: print("Error: No watch paths configured"); return 1
        self.auto_organize = args.auto_organize
        def signal_handler(sig, frame): print("\nStopping watcher..."); self.watcher.stop(); sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        self.watcher.start()
        print(f"Watching {len(self.watcher.watch_paths)} path(s)... Press Ctrl+C to stop")
        try:
            while self.watcher.is_running(): import time; time.sleep(1)
        except KeyboardInterrupt: pass
        finally: self.watcher.stop()
        return 0
    
    def cmd_organize(self, args) -> int:
        path = os.path.abspath(args.path)
        if not os.path.exists(path): print(f"Error: Path does not exist: {path}"); return 1
        if args.preset:
            preset = get_preset_config(args.preset)
            for rule in preset.get("rules", []): self.rule_engine.add_rule(rule)
            print(f"Applied preset: {preset.get('name')}")
        if args.by_type: self.rule_engine.add_rule({"name": "cli_by_type", "enabled": True, "action": "organize_by_type", "target_folder": os.path.join(path, "{file_type}")})
        if args.by_date: self.rule_engine.add_rule({"name": "cli_by_date", "enabled": True, "action": "organize_by_date", "date_format": "%Y/%m", "target_folder": os.path.join(path, "ByDate", "{date}")})
        print(f"Scanning: {path}")
        files_to_process = []
        for root, _, files in os.walk(path):
            for filename in files: files_to_process.append(os.path.join(root, filename))
        print(f"Found {len(files_to_process)} files")
        actions_executed = 0
        for filepath in files_to_process:
            context = {"watch_path": path}
            results = self.rule_engine.evaluate_rules(filepath, context)
            for result in results:
                action = result.get("result")
                if action: self.organizer.execute_action(action); actions_executed += 1
        if args.dedup:
            print("Checking for duplicates...")
            duplicates = self.rule_engine.find_duplicates(path, method="hash")
            dup_count = sum(len(paths) - 1 for paths in duplicates.values() if len(paths) > 1)
            print(f"Found {dup_count} duplicate files")
            for file_hash, paths in duplicates.items():
                if len(paths) > 1:
                    for dup_path in paths[1:]: self.organizer.execute_action({"operation": "delete", "source": dup_path, "reason": f"Duplicate of {paths[0]}"})
        stats = self.organizer.get_stats()
        print(f"\nOrganization complete!\n  Actions executed: {stats['total_actions']}\n  Successful: {stats['successful']}\n  Failed: {stats['failed']}")
        return 0
    
    def cmd_config(self, args) -> int:
        if args.init: self.config.create_default_config(); print(f"Created default configuration at: {self.config.config_path}"); return 0
        if args.show: print(json.dumps({"config_path": self.config.config_path, "watch_paths": self.config.watch_paths, "global_settings": self.config.global_settings, "file_types_count": len(self.config.file_types)}, indent=2)); return 0
        if args.add_path: self.config.add_watch_path(args.add_path); self.config.save(); print(f"Added watch path: {args.add_path}"); return 0
        if args.remove_path: self.config.remove_watch_path(args.remove_path); self.config.save(); print(f"Removed watch path: {args.remove_path}"); return 0
        print(f"Configuration file: {self.config.config_path}\nWatch paths: {len(self.config.watch_paths)}\nOrganization rules: {len(self.config.organization_rules)}\n\nUse --init to create default config, --show to view full config")
        return 0
    
    def cmd_rules(self, args) -> int:
        if args.list:
            rules = self.config.organization_rules
            if not rules: print("No rules configured")
            else:
                print(f"Organization Rules ({len(rules)}):")
                for i, rule in enumerate(rules, 1): print(f"  {i}. [{'✓' if rule.get('enabled', True) else '✗'}] {rule['name']} ({rule.get('action', 'unknown')})")
            return 0
        if args.add:
            try: rule = json.loads(args.add); self.config.add_organization_rule(rule); self.config.save(); print(f"Added rule: {rule['name']}")
            except json.JSONDecodeError as e: print(f"Error: Invalid JSON - {e}"); return 1
            return 0
        if args.remove:
            if self.config.remove_rule(args.remove): self.config.save(); print(f"Removed rule: {args.remove}")
            else: print(f"Rule not found: {args.remove}"); return 1
            return 0
        print("Use --list to view rules, --add to add a rule, --remove to remove a rule")
        return 0
    
    def cmd_tui(self) -> int:
        self.tui.clear()
        stats = {"watcher_status": "Running" if self.watcher and self.watcher.is_running() else "Stopped", "watch_paths": len(self.config.watch_paths) if self.config else 0, "rules_active": len([r for r in (self.config.organization_rules if self.config else []) if r.get("enabled", True)]), "events_tracked": len(self.events), "files_organized": self.organizer.get_stats().get("successful", 0) if self.organizer else 0}
        self.tui.draw_main_dashboard(stats=stats, watch_paths=self.config.watch_paths if self.config else [], rules=self.config.organization_rules if self.config else [], events=self.events)
        input("\nPress Enter to exit TUI...")
        return 0
    
    def cmd_preset(self, args) -> int:
        preset = get_preset_config(args.name)
        if not preset: print(f"Unknown preset: {args.name}"); return 1
        path = os.path.abspath(args.path)
        if not os.path.exists(path): print(f"Creating directory: {path}"); os.makedirs(path, exist_ok=True)
        self.config.add_watch_path(path)
        for rule in preset.get("rules", []):
            if "target_folder" in rule: rule["target_folder"] = rule["target_folder"].replace("{watch_path}", path)
            self.config.add_organization_rule(rule)
        self.config.save()
        print(f"Applied preset: {preset['name']}\nDescription: {preset['description']}\nWatch path: {path}\nRules added: {len(preset.get('rules', []))}")
        return 0

def main(args: Optional[List[str]] = None) -> int:
    cli = FileWatchCLI()
    return cli.run(args)

if __name__ == "__main__": sys.exit(main())
