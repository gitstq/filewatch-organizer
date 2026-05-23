"""Terminal User Interface for FileWatch-Organizer"""
import os, sys, shutil
from typing import List, Dict, Optional
from datetime import datetime

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = "\033[30m", "\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m", "\033[37m"
    BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW = "\033[90m", "\033[91m", "\033[92m", "\033[93m"
    BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE = "\033[94m", "\033[95m", "\033[96m", "\033[97m"

class TUI:
    def __init__(self):
        self.term_width = shutil.get_terminal_size().columns
        self.term_height = shutil.get_terminal_size().lines
        self.use_colors = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        self.message_queue: List[str] = []
        self.max_messages = 100
    
    def color(self, text: str, *color_codes: str) -> str:
        if not self.use_colors: return text
        return f"{''.join(color_codes)}{text}{Colors.RESET}"
    
    def clear(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def draw_header(self, title: str, subtitle: str = "") -> None:
        self.term_width = shutil.get_terminal_size().columns
        print(self.color("═" * self.term_width, Colors.CYAN))
        title_padding = (self.term_width - len(title)) // 2
        print(self.color(" " * title_padding + title, Colors.BOLD + Colors.CYAN))
        if subtitle:
            sub_padding = (self.term_width - len(subtitle)) // 2
            print(self.color(" " * sub_padding + subtitle, Colors.DIM + Colors.CYAN))
        print(self.color("═" * self.term_width, Colors.CYAN))
    
    def draw_stats_panel(self, stats: Dict) -> None:
        print(self.color("\n📊 Statistics", Colors.BOLD + Colors.YELLOW))
        print(self.color("─" * 40, Colors.DIM))
        for key, value in stats.items():
            key_formatted = key.replace("_", " ").title()
            value_str = f"{value:.2f}" if isinstance(value, float) else str(value)
            print(f"  {self.color(key_formatted + ':', Colors.CYAN):<20} {self.color(value_str, Colors.BRIGHT_GREEN)}")
    
    def draw_watch_paths(self, watch_paths: List[Dict]) -> None:
        print(self.color("\n👁️  Watch Paths", Colors.BOLD + Colors.YELLOW))
        print(self.color("─" * 40, Colors.DIM))
        if not watch_paths: print(self.color("  No paths configured", Colors.DIM)); return
        for i, wp in enumerate(watch_paths, 1):
            path = wp.get("path", "Unknown")
            recursive = "recursive" if wp.get("recursive", True) else "flat"
            status_icon = self.color("✓", Colors.GREEN) if os.path.exists(path) else self.color("✗", Colors.RED)
            print(f"  {status_icon} {i}. {self.color(path, Colors.BRIGHT_WHITE)} ({self.color(recursive, Colors.DIM)})")
    
    def draw_rules(self, rules: List[Dict]) -> None:
        print(self.color("\n📋 Organization Rules", Colors.BOLD + Colors.YELLOW))
        print(self.color("─" * 40, Colors.DIM))
        if not rules: print(self.color("  No rules configured", Colors.DIM)); return
        for i, rule in enumerate(rules, 1):
            name = rule.get("name", "Unnamed")
            action = rule.get("action", "unknown")
            enabled = self.color("●", Colors.GREEN) if rule.get("enabled", True) else self.color("○", Colors.DIM)
            print(f"  {enabled} {i}. {self.color(name, Colors.BRIGHT_WHITE)} ({self.color(action, Colors.CYAN)})")
    
    def draw_recent_events(self, events: List[Dict], max_events: int = 10) -> None:
        print(self.color("\n📁 Recent Events", Colors.BOLD + Colors.YELLOW))
        print(self.color("─" * 40, Colors.DIM))
        if not events: print(self.color("  No recent events", Colors.DIM)); return
        event_icons = {"created": self.color("+", Colors.GREEN), "modified": self.color("~", Colors.YELLOW),
                      "deleted": self.color("-", Colors.RED), "moved": self.color("→", Colors.BLUE)}
        for event in events[-max_events:]:
            event_type = event.get("event_type", "unknown")
            filename = event.get("filename", "Unknown")
            icon = event_icons.get(event_type, self.color("?", Colors.DIM))
            print(f"  {icon} {self.color(event_type.upper(), Colors.DIM):<10} {filename}")
    
    def draw_log(self, max_lines: int = 8) -> None:
        print(self.color("\n📝 Log", Colors.BOLD + Colors.YELLOW))
        print(self.color("─" * 40, Colors.DIM))
        messages = self.message_queue[-max_lines:]
        if not messages: print(self.color("  No messages", Colors.DIM))
        else:
            for msg in messages: print(f"  {msg}")
    
    def draw_main_dashboard(self, stats: Dict, watch_paths: List[Dict], rules: List[Dict], events: List[Dict]) -> None:
        self.clear()
        self.draw_header("📁 FileWatch-Organizer", "Lightweight File System Intelligent Monitoring & Auto-Organization Engine")
        self.draw_stats_panel(stats)
        self.draw_watch_paths(watch_paths)
        self.draw_rules(rules)
        self.draw_recent_events(events)
        self.draw_log()
        print(self.color("\n" + "─" * self.term_width, Colors.DIM))
        print(self.color("Commands: [s]tart [p]ause [o]rganize [c]onfig [q]uit", Colors.DIM))
    
    def log_message(self, message: str, level: str = "info") -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_colors = {"info": Colors.WHITE, "success": Colors.GREEN, "warning": Colors.YELLOW, "error": Colors.RED, "debug": Colors.DIM}
        self.message_queue.append(f"[{timestamp}] {self.color(message, level_colors.get(level, Colors.WHITE))}")
        if len(self.message_queue) > self.max_messages: self.message_queue.pop(0)
    
    def show_message(self, message: str, level: str = "info") -> None:
        level_colors = {"info": Colors.BLUE, "success": Colors.GREEN, "warning": Colors.YELLOW, "error": Colors.RED}
        icon = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(level, "•")
        print(f"\n{icon} {self.color(message, level_colors.get(level, Colors.WHITE))}\n")

def create_tui() -> TUI: return TUI()
