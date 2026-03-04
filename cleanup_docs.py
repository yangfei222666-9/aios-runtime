"""
AIOS Documentation Cleanup Script

Cleans up redundant and outdated documentation files.

Actions:
1. Create archive/ folder
2. Move old reports to archive/
3. Delete redundant files
4. Generate summary
"""
import shutil
from pathlib import Path

AIOS_ROOT = Path(__file__).resolve().parent

# Files to delete (redundant)
DELETE_FILES = [
    "README_TEST.md",
    "AIOS_简单介绍.md",
    "AIOS_详细介绍.md",
]

# Files to archive (historical)
ARCHIVE_FILES = [
    "test_report_2026-02-24.md",
    "TEST_REPORT_2026-02-25.md",
    "COMPLETION_REPORT_V05.md",
    "COMPLETION_REPORT_v1.3.md",
    "PHASE2_REPORT.md",
    "PHASE3_REPORT.md",
    "AUTO_DISPATCHER_INJECTION_COMPLETE.md",
    "OBSERVABILITY_INJECTION_REPORT.md",
    "EVENTBUS_INTEGRATION.md",
    "REACTOR_DEMO_REPORT.md",
    "SELF_IMPROVING_DEMO_REPORT.md",
    "QUICK_START_REPORT.md",
    "PRODUCTION_PERFORMANCE_REPORT.md",
    "PERFORMANCE_SUMMARY.md",
    "FINAL_SUMMARY.md",
    "FINAL_VALIDATION_REPORT.md",
    "FINAL_DIRECTORY_STRUCTURE.md",
    "CLEANUP_LOG.md",
    "MIGRATION_LOG.md",
    "CHECKLIST.md",
    "ANALYSIS_EVIDENCE.md",
    "agent_status_report.md",
]

# Core files to keep
KEEP_FILES = [
    "README.md",
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "IMPROVEMENT_REPORT.md",
    "TASK_QUEUE_INTEGRATION.md",
    "OPTIMIZATION_REPORT.md",
    "DOCS_STRUCTURE.md",
]


def main():
    print("=" * 70)
    print("AIOS Documentation Cleanup")
    print("=" * 70)
    
    # Create archive folder
    archive_dir = AIOS_ROOT / "archive"
    archive_dir.mkdir(exist_ok=True)
    print(f"\n[1] Created archive folder: {archive_dir}")
    
    # Delete redundant files
    print("\n[2] Deleting redundant files...")
    deleted_count = 0
    for filename in DELETE_FILES:
        file_path = AIOS_ROOT / filename
        if file_path.exists():
            file_path.unlink()
            print(f"  ✓ Deleted: {filename}")
            deleted_count += 1
    print(f"  Total deleted: {deleted_count}")
    
    # Archive historical files
    print("\n[3] Archiving historical files...")
    archived_count = 0
    for filename in ARCHIVE_FILES:
        file_path = AIOS_ROOT / filename
        if file_path.exists():
            dest_path = archive_dir / filename
            shutil.move(str(file_path), str(dest_path))
            print(f"  ✓ Archived: {filename}")
            archived_count += 1
    print(f"  Total archived: {archived_count}")
    
    # List remaining .md files
    print("\n[4] Remaining documentation files:")
    remaining_files = sorted([f.name for f in AIOS_ROOT.glob("*.md")])
    
    core_files = [f for f in remaining_files if f in KEEP_FILES]
    other_files = [f for f in remaining_files if f not in KEEP_FILES]
    
    print(f"\n  Core files ({len(core_files)}):")
    for filename in core_files:
        print(f"    ✓ {filename}")
    
    if other_files:
        print(f"\n  Other files ({len(other_files)}):")
        for filename in other_files:
            print(f"    - {filename}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Cleanup Summary:")
    print("=" * 70)
    print(f"  Deleted: {deleted_count} files")
    print(f"  Archived: {archived_count} files")
    print(f"  Remaining: {len(remaining_files)} files")
    print(f"    Core: {len(core_files)}")
    print(f"    Other: {len(other_files)}")
    print("\n✓ Cleanup completed!")


if __name__ == "__main__":
    main()
