"""
Step 7: Repository Cleanup Script
=================================
This script will systematically clean up your repository and create
a professional structure for academic publication.
"""

import os
import shutil
from pathlib import Path

class RepositoryCleanup:
    def __init__(self):
        self.project_root = Path('.')
        self.backup_created = False
        
    def create_backup(self):
        """Create a backup of current state before cleanup"""
        print("=== Step 7.1: Creating Backup ===")
        
        backup_dir = self.project_root / 'backup_before_cleanup'
        
        if backup_dir.exists():
            print(f"Backup directory already exists: {backup_dir}")
            return
        
        # Create backup directory
        backup_dir.mkdir()
        
        # Files to backup (the step files we're about to delete)
        files_to_backup = [
            'rtf_integration_test.py',
            'step2_interface_inspection.py',
            'rtf_integration_bridge.py', 
            'step4_fix_domain_computation.py',
            'step4b_debug_domain_method.py',
            'step5_final_working_integration.py',
            'step6_corrected_algorithm.py'  # Keep backup of this too
        ]
        
        backed_up_count = 0
        for file_name in files_to_backup:
            source_file = self.project_root / file_name
            if source_file.exists():
                backup_file = backup_dir / file_name
                shutil.copy2(source_file, backup_file)
                print(f"  ✓ Backed up: {file_name}")
                backed_up_count += 1
            else:
                print(f"  - Not found: {file_name}")
        
        print(f"✓ Created backup with {backed_up_count} files in: {backup_dir}")
        self.backup_created = True
    
    def remove_development_files(self):
        """Remove development and debug files"""
        print("\n=== Step 7.2: Removing Development Files ===")
        
        files_to_remove = [
            'rtf_integration_test.py',
            'step2_interface_inspection.py',
            'rtf_integration_bridge.py',
            'step4_fix_domain_computation.py', 
            'step4b_debug_domain_method.py',
            'step5_final_working_integration.py'
        ]
        
        removed_count = 0
        for file_name in files_to_remove:
            file_path = self.project_root / file_name
            if file_path.exists():
                file_path.unlink()
                print(f"  ✓ Removed: {file_name}")
                removed_count += 1
            else:
                print(f"  - Not found: {file_name}")
        
        print(f"✓ Removed {removed_count} development files")
    
    def create_package_structure(self):
        """Create the new package directory structure"""
        print("\n=== Step 7.3: Creating Package Structure ===")
        
        # Directories to create
        directories = [
            'rtf_core',
            'examples', 
            'tests',
            'docs'
        ]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir()
                print(f"  ✓ Created directory: {dir_name}")
            else:
                print(f"  - Directory already exists: {dir_name}")
        
        # Create __init__.py files
        init_files = [
            'rtf_core/__init__.py',
            'examples/__init__.py', 
            'tests/__init__.py'
        ]
        
        for init_file in init_files:
            init_path = self.project_root / init_file
            if not init_path.exists():
                init_path.write_text('# Package initialization\n')
                print(f"  ✓ Created: {init_file}")
            else:
                print(f"  - Already exists: {init_file}")
    
    def move_core_files(self):
        """Move core files to their new locations"""
        print("\n=== Step 7.4: Moving Core Files ===")
        
        # File moves to perform
        moves = [
            ('step6_corrected_algorithm.py', 'rtf_core/multi_level_optimizer.py'),
            ('config.py', 'rtf_core/config.py')
        ]
        
        for source, destination in moves:
            source_path = self.project_root / source
            dest_path = self.project_root / destination
            
            if source_path.exists():
                if not dest_path.exists():
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  ✓ Moved: {source} → {destination}")
                else:
                    print(f"  - Destination exists: {destination}")
            else:
                print(f"  - Source not found: {source}")
    
    def create_rtf_core_init(self):
        """Create proper __init__.py for rtf_core package"""
        print("\n=== Step 7.5: Creating RTF Core Package Init ===")
        
        init_content = '''"""
RTF Multi-Level Analysis Package
================================
Right-to-be-Forgotten privacy protection through strategic cell deletion.

This package implements the complete multi-level analysis strategy for
achieving privacy protection while minimizing data utility loss.

Author: Your Name
Version: 1.0.0
"""

from .multi_level_optimizer import RTFCorrectedAlgorithm as RTFMultiLevelOptimizer
from .config import get_database_config, get_dataset_info, list_available_datasets

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = [
    'RTFMultiLevelOptimizer',
    'get_database_config',
    'get_dataset_info', 
    'list_available_datasets'
]
'''
        
        init_path = self.project_root / 'rtf_core' / '__init__.py'
        init_path.write_text(init_content)
        print(f"  ✓ Created comprehensive rtf_core/__init__.py")
    
    def verify_cleanup(self):
        """Verify the cleanup was successful"""
        print("\n=== Step 7.6: Verification ===")
        
        # Check that old files are gone
        old_files = [
            'rtf_integration_test.py',
            'step2_interface_inspection.py',
            'rtf_integration_bridge.py',
            'step4_fix_domain_computation.py',
            'step4b_debug_domain_method.py', 
            'step5_final_working_integration.py'
        ]
        
        files_still_present = []
        for file_name in old_files:
            if (self.project_root / file_name).exists():
                files_still_present.append(file_name)
        
        if files_still_present:
            print(f"  ⚠️ These old files still exist: {files_still_present}")
        else:
            print("  ✓ All development files successfully removed")
        
        # Check that new structure exists
        required_structure = [
            'rtf_core/__init__.py',
            'rtf_core/multi_level_optimizer.py',
            'rtf_core/config.py',
            'examples/__init__.py',
            'tests/__init__.py',
            'docs'
        ]
        
        missing_structure = []
        for item in required_structure:
            if not (self.project_root / item).exists():
                missing_structure.append(item)
        
        if missing_structure:
            print(f"  ⚠️ Missing structure: {missing_structure}")
        else:
            print("  ✓ New package structure successfully created")
    
    def run_complete_cleanup(self):
        """Execute the complete cleanup process"""
        print("🧹 RTF Repository Cleanup Starting...")
        print("=" * 50)
        
        try:
            self.create_backup()
            self.remove_development_files()
            self.create_package_structure()
            self.move_core_files()
            self.create_rtf_core_init()
            self.verify_cleanup()
            
            print("\n" + "=" * 50)
            print("🎉 Repository Cleanup Complete!")
            print("\nNext Steps:")
            print("1. Test the new structure with: python -c 'from rtf_core import RTFMultiLevelOptimizer; print(\"✓ Import successful\")'")
            print("2. Run Step 8 to create examples and documentation")
            print("3. Commit the cleaned repository")
            
            if self.backup_created:
                print(f"\n💾 Backup created in: backup_before_cleanup/")
                print("   You can delete this folder once you're satisfied with the cleanup")
            
        except Exception as e:
            print(f"\n❌ Error during cleanup: {e}")
            print("Check the backup_before_cleanup/ folder if you need to restore files")
            raise


def main():
    """Run the repository cleanup"""
    cleanup = RepositoryCleanup()
    cleanup.run_complete_cleanup()


if __name__ == '__main__':
    main()