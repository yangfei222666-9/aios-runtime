"""
AIOS Demo: File Monitor + Auto Organizer

Real-world scenario: Monitor a folder for new files and automatically organize them.

Scenario:
1. Monitor downloads/ folder
2. New file detected → classify by extension
3. Move to appropriate folder (documents/images/videos/archives)
4. Log the action

This demonstrates:
- EventBus (file events)
- Reactor (auto-response to events)
- Scheduler (task execution)
- Real-world automation
"""
import sys
import time
import json
from pathlib import Path

# Add AIOS to path
AIOS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(AIOS_ROOT))

# Use in-memory EventBus (no storage)
from core.event import Event


class SimpleEventBus:
    """Simple in-memory event bus for demo."""
    
    def __init__(self):
        self._subscribers = {}
    
    def emit(self, event: Event):
        """Emit an event."""
        # Notify exact match
        if event.type in self._subscribers:
            for callback in self._subscribers[event.type]:
                callback(event)
        
        # Notify wildcard subscribers
        for pattern, callbacks in self._subscribers.items():
            if "*" in pattern:
                prefix = pattern.replace("*", "")
                if event.type.startswith(prefix):
                    for callback in callbacks:
                        callback(event)
    
    def subscribe(self, event_type: str, callback):
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)


def create_event(event_type: str, data: dict) -> Event:
    """Create an event."""
    import uuid
    return Event(
        id=str(uuid.uuid4()),
        type=event_type,
        source="demo",
        timestamp=int(time.time() * 1000),
        payload=data
    )


class FileMonitor:
    """Monitor a folder for new files."""
    
    def __init__(self, watch_dir: Path, event_bus: SimpleEventBus):
        self.watch_dir = watch_dir
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self._bus = event_bus
        self._seen_files = set(f.name for f in self.watch_dir.iterdir() if f.is_file())
    
    def check(self):
        """Check for new files."""
        current_files = set(f.name for f in self.watch_dir.iterdir() if f.is_file())
        new_files = current_files - self._seen_files
        
        for filename in new_files:
            file_path = self.watch_dir / filename
            self._bus.emit(create_event(
                "file.new",
                {
                    "path": str(file_path),
                    "name": filename,
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix.lower(),
                }
            ))
            print(f"[Monitor] New file detected: {filename}")
        
        self._seen_files = current_files
        return len(new_files)


class FileOrganizer:
    """Organize files by extension."""
    
    # File type mappings
    CATEGORIES = {
        "documents": [".txt", ".pdf", ".doc", ".docx", ".md", ".rtf"],
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
        "archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "code": [".py", ".js", ".java", ".cpp", ".c", ".h", ".html", ".css"],
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    }
    
    def __init__(self, base_dir: Path, event_bus: SimpleEventBus):
        self.base_dir = base_dir
        self._bus = event_bus
        
        # Create category folders
        for category in self.CATEGORIES.keys():
            (self.base_dir / category).mkdir(parents=True, exist_ok=True)
        (self.base_dir / "others").mkdir(parents=True, exist_ok=True)
        
        # Subscribe to file events
        self._bus.subscribe("file.new", self.handle_new_file)
    
    def handle_new_file(self, event):
        """Handle new file event."""
        file_path = Path(event.payload["path"])
        extension = event.payload["extension"]
        
        # Determine category
        category = "others"
        for cat, exts in self.CATEGORIES.items():
            if extension in exts:
                category = cat
                break
        
        # Move file
        dest_dir = self.base_dir / category
        dest_path = dest_dir / file_path.name
        
        try:
            file_path.rename(dest_path)
            print(f"[Organizer] Moved {file_path.name} → {category}/")
            
            # Publish success event
            self._bus.emit(create_event(
                "file.organized",
                {
                    "original_path": str(file_path),
                    "new_path": str(dest_path),
                    "category": category,
                    "extension": extension,
                }
            ))
        except Exception as e:
            print(f"[Organizer] Error moving {file_path.name}: {e}")
            
            # Publish error event
            self._bus.emit(create_event(
                "file.organize_failed",
                {
                    "path": str(file_path),
                    "error": str(e),
                }
            ))


class ActionLogger:
    """Log all file actions."""
    
    def __init__(self, log_file: Path, event_bus: SimpleEventBus):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._bus = event_bus
        
        # Subscribe to all file events
        self._bus.subscribe("file.*", self.log_event)
    
    def log_event(self, event):
        """Log an event."""
        log_entry = {
            "timestamp": event.timestamp,
            "type": event.type,
            "data": event.payload,
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def create_demo_files(watch_dir: Path):
    """Create some demo files for testing."""
    demo_files = [
        ("report.pdf", "documents"),
        ("photo.jpg", "images"),
        ("video.mp4", "videos"),
        ("archive.zip", "archives"),
        ("script.py", "code"),
        ("song.mp3", "audio"),
        ("readme.txt", "documents"),
        ("unknown.xyz", "others"),
    ]
    
    print("\n[Demo] Creating test files...")
    for filename, expected_category in demo_files:
        file_path = watch_dir / filename
        file_path.write_text(f"Demo file: {filename}")
        print(f"  Created: {filename} (should go to {expected_category}/)")
        time.sleep(0.2)  # Small delay to simulate real-world timing


def main():
    """Run the demo."""
    print("=" * 70)
    print("AIOS Demo: File Monitor + Auto Organizer")
    print("=" * 70)
    print("\nScenario:")
    print("  1. Monitor downloads/ folder")
    print("  2. New file detected → classify by extension")
    print("  3. Move to appropriate folder (documents/images/videos/etc.)")
    print("  4. Log all actions")
    print("\nThis demonstrates:")
    print("  - EventBus (file events)")
    print("  - Reactor (auto-response to events)")
    print("  - Real-world automation")
    print("=" * 70)
    
    # Setup
    demo_dir = AIOS_ROOT / "demo_data" / "file_monitor"
    watch_dir = demo_dir / "downloads"
    log_file = demo_dir / "actions.log"
    
    # Clean up previous demo
    if demo_dir.exists():
        import shutil
        shutil.rmtree(demo_dir)
    
    # Initialize components
    event_bus = SimpleEventBus()
    monitor = FileMonitor(watch_dir, event_bus)
    organizer = FileOrganizer(demo_dir, event_bus)
    logger = ActionLogger(log_file, event_bus)
    
    print("\n[Setup] Components initialized")
    print(f"  Watch folder: {watch_dir}")
    print(f"  Log file: {log_file}")
    
    # Create demo files
    create_demo_files(watch_dir)
    
    # Monitor and organize
    print("\n[Monitor] Checking for new files...")
    time.sleep(0.5)
    
    new_count = monitor.check()
    print(f"\n[Monitor] Found {new_count} new files")
    
    # Wait for organization to complete
    time.sleep(1)
    
    # Show results
    print("\n" + "=" * 70)
    print("Results:")
    print("=" * 70)
    
    for category in ["documents", "images", "videos", "archives", "code", "audio", "others"]:
        category_dir = demo_dir / category
        if category_dir.exists():
            files = list(category_dir.iterdir())
            if files:
                print(f"\n{category.upper()}/ ({len(files)} files):")
                for f in files:
                    print(f"  - {f.name}")
    
    # Show log
    print("\n" + "=" * 70)
    print("Action Log:")
    print("=" * 70)
    
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                print(f"[{entry['type']}] {entry['data']}")
    
    print("\n" + "=" * 70)
    print("Demo completed! ✓")
    print("=" * 70)
    print(f"\nDemo files saved to: {demo_dir}")
    print("You can inspect the organized files and action log.")


if __name__ == "__main__":
    main()
