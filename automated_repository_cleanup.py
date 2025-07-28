#!/usr/bin/env python3
"""
Automated Repository Cleanup Script
===================================
Complete automated cleanup for RTF25 research project.
Safely removes development artifacts while preserving all functionality.

Usage: python automated_repository_cleanup.py
"""

import os
import shutil
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import glob

class AutomatedRepositoryCleanup:
    def __init__(self):
        self.project_root = Path('.')
        self.backup_dir = None
        self.removed_files = []
        self.preserved_files = []
        self.created_files = []
        self.errors = []
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "ERROR":
            print(f"[ERROR] [{timestamp}] {message}")
            self.errors.append(message)
        elif level == "WARNING":
            print(f"[WARNING] [{timestamp}] {message}")
        elif level == "SUCCESS":
            print(f"[SUCCESS] [{timestamp}] {message}")
        else:
            print(f"?? [{timestamp}] {message}")

    def create_safety_backup(self):
        """Create a comprehensive safety backup"""
        self.log("Creating comprehensive safety backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / f'safety_backup_{timestamp}'
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Copy all Python files and important files
            important_patterns = ['*.py', '*.md', '*.txt', 'LICENSE', '*.json', '*.yml', '*.yaml']
            backed_up_count = 0
            
            for pattern in important_patterns:
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file() and not file_path.name.startswith('safety_backup_'):
                        backup_file = self.backup_dir / file_path.name
                        shutil.copy2(file_path, backup_file)
                        backed_up_count += 1
            
            # Also backup key directories
            key_dirs = ['rtf_core', 'RTFGraphConstruction', 'IDcomputation', 'DCandDelset']
            for dir_name in key_dirs:
                source_dir = self.project_root / dir_name
                if source_dir.exists():
                    dest_dir = self.backup_dir / dir_name
                    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
                    backed_up_count += len(list(source_dir.rglob('*')))
            
            self.log(f"Safety backup created: {self.backup_dir}", "SUCCESS")
            self.log(f"Backed up {backed_up_count} files/directories", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to create backup: {e}", "ERROR")
            return False

    def verify_essential_files(self):
        """Verify that essential files exist before cleanup"""
        self.log("Verifying essential files exist...")
        
        essential_files = [
            'README.md',
            'LICENSE',
            'fixed_rtf_demo.py',
            'rtf_success_test.py',
            'config.py'
        ]
        
        essential_dirs = [
            'RTFGraphConstruction',
            'IDcomputation',
            'DCandDelset'
        ]
        
        missing_essentials = []
        
        # Check files
        for file_name in essential_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log(f"Found essential file: {file_name}")
                self.preserved_files.append(file_name)
            else:
                self.log(f"Missing essential file: {file_name}", "WARNING")
                missing_essentials.append(file_name)
        
        # Check directories
        for dir_name in essential_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                self.log(f"Found essential directory: {dir_name}/")
                self.preserved_files.append(f"{dir_name}/")
            else:
                self.log(f"Missing essential directory: {dir_name}/", "WARNING")
                missing_essentials.append(f"{dir_name}/")
        
        if missing_essentials:
            self.log(f"Missing {len(missing_essentials)} essential items", "WARNING")
            return False
        else:
            self.log("All essential files verified", "SUCCESS")
            return True

    def test_current_functionality(self):
        """Test that current system works before cleanup"""
        self.log("Testing current system functionality...")
        
        try:
            # Test rtf_success_test.py
            if (self.project_root / 'rtf_success_test.py').exists():
                self.log("Testing rtf_success_test.py...")
                result = subprocess.run([sys.executable, 'rtf_success_test.py'], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    self.log("rtf_success_test.py passed", "SUCCESS")
                else:
                    self.log(f"rtf_success_test.py failed: {result.stderr[:200]}", "WARNING")
            
            # Test fixed_rtf_demo.py
            if (self.project_root / 'fixed_rtf_demo.py').exists():
                self.log("Testing fixed_rtf_demo.py...")
                result = subprocess.run([sys.executable, 'fixed_rtf_demo.py'], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    self.log("fixed_rtf_demo.py passed", "SUCCESS")
                else:
                    self.log(f"fixed_rtf_demo.py failed: {result.stderr[:200]}", "WARNING")
            
            # Test basic imports
            self.log("Testing basic imports...")
            test_import_code = """
try:
    import config
    from cell import Cell, Attribute
    print("SUCCESS: Core imports working")
except Exception as e:
    print(f"ERROR: Import failed: {e}")
"""
            result = subprocess.run([sys.executable, '-c', test_import_code], 
                                  capture_output=True, text=True, timeout=30)
            if "SUCCESS" in result.stdout:
                self.log("Basic imports working", "SUCCESS")
            else:
                self.log(f"Import issues: {result.stdout}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"Functionality test failed: {e}", "ERROR")
            return False

    def remove_development_artifacts(self):
        """Remove all development artifacts systematically"""
        self.log("Removing development artifacts...")
        
        # Files to remove
        files_to_remove = [
            # Step files
            'step*.py',
            # Integration files  
            'rtf_integration*.py',
            '*integration*.py',
            # Debug files
            'debug_*.py',
            'test_*.py',  # Will preserve rtf_success_test.py separately
            # Other development files
            'simple_import_test.py',
            'final_rtf_demo.py',
            'test_config_fix.py',
            'test_standalone_config.py'
        ]
        
        # Directories to remove
        dirs_to_remove = [
            'backup_before_cleanup',
            'backup_*'
        ]
        
        removed_count = 0
        
        # Remove files using glob patterns
        for pattern in files_to_remove:
            matching_files = glob.glob(pattern)
            for file_path in matching_files:
                file_obj = Path(file_path)
                # Special protection for rtf_success_test.py
                if file_obj.name == 'rtf_success_test.py':
                    self.log(f"Preserving: {file_path}")
                    continue
                    
                try:
                    if file_obj.exists():
                        file_obj.unlink()
                        self.log(f"Removed file: {file_path}")
                        self.removed_files.append(file_path)
                        removed_count += 1
                except Exception as e:
                    self.log(f"Failed to remove {file_path}: {e}", "ERROR")
        
        # Remove directories
        for pattern in dirs_to_remove:
            matching_dirs = glob.glob(pattern)
            for dir_path in matching_dirs:
                dir_obj = Path(dir_path)
                # Don't remove our safety backup
                if 'safety_backup_' in dir_path:
                    continue
                    
                try:
                    if dir_obj.exists() and dir_obj.is_dir():
                        shutil.rmtree(dir_obj)
                        self.log(f"Removed directory: {dir_path}")
                        self.removed_files.append(dir_path)
                        removed_count += 1
                except Exception as e:
                    self.log(f"Failed to remove {dir_path}: {e}", "ERROR")
        
        # Clean Python cache
        cache_removed = self.clean_python_cache()
        removed_count += cache_removed
        
        self.log(f"Removed {removed_count} development artifacts", "SUCCESS")
        return removed_count

    def clean_python_cache(self):
        """Remove Python cache files and directories"""
        self.log("Cleaning Python cache files...")
        cache_count = 0
        
        try:
            # Remove .pyc files
            for pyc_file in self.project_root.rglob('*.pyc'):
                pyc_file.unlink()
                cache_count += 1
            
            # Remove .pyo files
            for pyo_file in self.project_root.rglob('*.pyo'):
                pyo_file.unlink()
                cache_count += 1
            
            # Remove __pycache__ directories
            for pycache_dir in self.project_root.rglob('__pycache__'):
                if pycache_dir.is_dir():
                    shutil.rmtree(pycache_dir)
                    cache_count += 1
            
            if cache_count > 0:
                self.log(f"Cleaned {cache_count} cache files/directories")
            
        except Exception as e:
            self.log(f"Error cleaning cache: {e}", "ERROR")
        
        return cache_count

    def create_professional_files(self):
        """Create missing professional files"""
        self.log("Creating professional files...")
        
        # Create requirements.txt
        self.create_requirements_txt()
        
        # Enhance .gitignore
        self.enhance_gitignore()

    def create_requirements_txt(self):
        """Create or enhance requirements.txt"""
        requirements_path = self.project_root / 'requirements.txt'
        
        if not requirements_path.exists():
            requirements_content = """# RTF25 - Right-to-be-Forgotten Multi-Level Optimizer
# Research project dependencies

# Core dependencies
mysql-connector-python>=8.0.0
pymysql>=1.0.0
pandas>=1.3.0
numpy>=1.20.0

# Graph and computation libraries
networkx>=2.6
scipy>=1.7.0

# Development dependencies (optional)
pytest>=6.0.0
pytest-cov>=2.12.0

# Documentation (optional)
sphinx>=4.0.0
sphinx-rtd-theme>=1.0.0
"""
            
            requirements_path.write_text(requirements_content)
            self.log("Created requirements.txt", "SUCCESS")
            self.created_files.append('requirements.txt')
        else:
            self.log("requirements.txt already exists")

    def enhance_gitignore(self):
        """Enhance .gitignore with professional patterns"""
        gitignore_path = self.project_root / '.gitignore'
        
        additional_patterns = """
# RTF25 Development artifacts
step*.py
*_test_*.py
debug_*.py
backup_*/
safety_backup_*/
final_backup_*/

# RTF specific
output/
logs/
*.csv.bak
data/private/
"""
        
        try:
            if gitignore_path.exists():
                current_content = gitignore_path.read_text()
                if 'RTF25 Development artifacts' not in current_content:
                    with open(gitignore_path, 'a') as f:
                        f.write(additional_patterns)
                    self.log("Enhanced .gitignore", "SUCCESS")
                else:
                    self.log(".gitignore already enhanced")
            else:
                gitignore_path.write_text(additional_patterns.strip())
                self.log("Created .gitignore", "SUCCESS")
                self.created_files.append('.gitignore')
                
        except Exception as e:
            self.log(f"Failed to enhance .gitignore: {e}", "ERROR")

    def verify_post_cleanup_functionality(self):
        """Test that system still works after cleanup"""
        self.log("Verifying functionality after cleanup...")
        
        success_count = 0
        total_tests = 0
        
        try:
            # Test rtf_success_test.py
            if (self.project_root / 'rtf_success_test.py').exists():
                total_tests += 1
                self.log("Testing rtf_success_test.py after cleanup...")
                result = subprocess.run([sys.executable, 'rtf_success_test.py'], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0 and 'SUCCESS' in result.stdout:
                    self.log("[SUCCESS] rtf_success_test.py PASSED", "SUCCESS")
                    success_count += 1
                else:
                    self.log(f"[ERROR] rtf_success_test.py FAILED", "ERROR")
                    self.log(f"Output: {result.stdout[-300:]}", "ERROR")
            
            # Test fixed_rtf_demo.py
            if (self.project_root / 'fixed_rtf_demo.py').exists():
                total_tests += 1
                self.log("Testing fixed_rtf_demo.py after cleanup...")
                result = subprocess.run([sys.executable, 'fixed_rtf_demo.py'], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0 and ('SUCCESS' in result.stdout or 'Privacy achieved' in result.stdout):
                    self.log("[SUCCESS] fixed_rtf_demo.py PASSED", "SUCCESS")
                    success_count += 1
                else:
                    self.log(f"[ERROR] fixed_rtf_demo.py FAILED", "ERROR")
                    self.log(f"Output: {result.stdout[-300:]}", "ERROR")
            
            # Test imports
            total_tests += 1
            self.log("Testing core imports after cleanup...")
            test_import_code = """
try:
    import config
    from cell import Cell, Attribute
    print("SUCCESS: Core imports working")
except Exception as e:
    print(f"ERROR: Import failed: {e}")
    import traceback
    traceback.print_exc()
"""
            result = subprocess.run([sys.executable, '-c', test_import_code], 
                                  capture_output=True, text=True, timeout=30)
            if "SUCCESS" in result.stdout:
                self.log("[SUCCESS] Core imports PASSED", "SUCCESS")
                success_count += 1
            else:
                self.log(f"[ERROR] Core imports FAILED", "ERROR")
                self.log(f"Error: {result.stdout}", "ERROR")
            
            success_rate = success_count / total_tests if total_tests > 0 else 0
            
            if success_rate >= 0.8:
                self.log(f"[SUCCESS] FUNCTIONALITY VERIFIED: {success_count}/{total_tests} tests passed", "SUCCESS")
                return True
            else:
                self.log(f"[WARNING] PARTIAL SUCCESS: {success_count}/{total_tests} tests passed", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Verification failed: {e}", "ERROR")
            return False

    def show_final_structure(self):
        """Display the final clean repository structure"""
        self.log("Final repository structure:")
        
        print("\n[FOLDER] FINAL CLEAN REPOSITORY STRUCTURE")
        print("=" * 50)
        
        # Show Python files
        print("\n[PYTHON] Python Files:")
        py_files = sorted([f for f in self.project_root.glob('*.py') if not f.name.startswith('safety_backup_')])
        for py_file in py_files:
            print(f"  ??? {py_file.name}")
        
        # Show other important files
        print("\n[FILE] Documentation & Config:")
        other_files = ['README.md', 'LICENSE', 'requirements.txt', '.gitignore']
        for file_name in other_files:
            if (self.project_root / file_name).exists():
                print(f"  ??? {file_name}")
        
        # Show directories
        print("\n[FOLDER] Core Directories:")
        core_dirs = ['rtf_core', 'RTFGraphConstruction', 'IDcomputation', 'DCandDelset']
        for dir_name in core_dirs:
            if (self.project_root / dir_name).exists():
                print(f"  ??? {dir_name}/")
        
        print(f"\n[DATA] Cleanup Summary:")
        print(f"  [REMOVE] Removed: {len(self.removed_files)} development artifacts")
        print(f"  [SUCCESS] Preserved: {len(self.preserved_files)} essential files")
        print(f"  [PACKAGE] Created: {len(self.created_files)} professional files")
        print(f"  [TOOLS] Errors: {len(self.errors)} issues encountered")

    def provide_recovery_instructions(self):
        """Provide recovery instructions in case of issues"""
        print(f"\n[RECOVERY] RECOVERY INSTRUCTIONS")
        print("=" * 30)
        print(f"If you need to restore files, your backup is at:")
        print(f"  {self.backup_dir}")
        print(f"\nTo restore everything:")
        print(f"  cp -r {self.backup_dir}/* .")
        print(f"\nTo restore specific files:")
        print(f"  cp {self.backup_dir}/filename.py .")

    def run_complete_cleanup(self):
        """Execute the complete automated cleanup process"""
        print("? RTF25 AUTOMATED REPOSITORY CLEANUP")
        print("=" * 60)
        print("Safely cleaning repository for professional presentation...")
        print("")
        
        try:
            # Phase 1: Safety & Verification
            if not self.create_safety_backup():
                print("[ERROR] FAILED: Could not create backup. Aborting.")
                return False
            
            if not self.verify_essential_files():
                print("[WARNING] WARNING: Some essential files missing, but continuing...")
            
            if not self.test_current_functionality():
                print("[WARNING] WARNING: Some functionality issues detected, but continuing...")
            
            # Phase 2: Cleanup
            removed_count = self.remove_development_artifacts()
            
            # Phase 3: Professional touch
            self.create_professional_files()
            
            # Phase 4: Verification
            functionality_ok = self.verify_post_cleanup_functionality()
            
            # Phase 5: Report
            self.show_final_structure()
            
            if functionality_ok and len(self.errors) == 0:
                print("\n[SUCCESS] CLEANUP SUCCESSFULLY COMPLETED!")
                print("[SUCCESS] Repository is now professionally clean")
                print("[SUCCESS] All functionality preserved")
                print("[SUCCESS] Ready for academic publication")
                
                print(f"\n[LAUNCH] Next Steps:")
                print(f"  1. Test: python rtf_success_test.py")
                print(f"  2. Demo: python fixed_rtf_demo.py")
                print(f"  3. Commit: git add . && git commit -m 'Professional cleanup'")
                print(f"  4. Share: Ready for GitHub and collaboration!")
                
            elif functionality_ok:
                print("\n[WARNING] CLEANUP COMPLETED WITH MINOR ISSUES")
                print("[SUCCESS] Core functionality preserved")
                print("[WARNING] Some non-critical issues encountered")
                print("[SUCCESS] Repository is usable and professional")
                
            else:
                print("\n[ERROR] CLEANUP COMPLETED BUT FUNCTIONALITY ISSUES DETECTED")
                print("[RECOVERY] Use recovery instructions below if needed")
            
            # Always provide recovery info
            self.provide_recovery_instructions()
            
            # Clean up our own backup after a delay (optional)
            print(f"\n[BACKUP] Backup will be kept at: {self.backup_dir}")
            print(f"   You can delete it once you confirm everything works")
            
            return functionality_ok
            
        except Exception as e:
            print(f"\n[ERROR] CRITICAL ERROR during cleanup: {e}")
            print("[RECOVERY] Your backup is safe. Use recovery instructions above.")
            self.provide_recovery_instructions()
            return False


def main():
    """Run the automated repository cleanup"""
    print("RTF25 Automated Repository Cleanup")
    print("This will safely remove development artifacts while preserving functionality")
    print("")
    
    # Simple confirmation
    try:
        response = input("Proceed with automated cleanup? [y/N]: ").strip().lower()
        if response not in ['y', 'yes']:
            print("Cleanup cancelled.")
            return
    except KeyboardInterrupt:
        print("\nCleanup cancelled.")
        return
    
    print("")
    cleanup = AutomatedRepositoryCleanup()
    success = cleanup.run_complete_cleanup()
    
    if success:
        print("\n[CLEAN] Cleanup successful! Your repository is ready for professional use.")
    else:
        print("\n[TOOLS] Cleanup completed but please check the messages above.")
    
    return success


if __name__ == '__main__':
    main()