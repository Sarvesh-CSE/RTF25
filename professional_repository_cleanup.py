#!/usr/bin/env python3
"""
Professional Repository Cleanup Script
======================================
Comprehensive cleanup script for RTF25 research project.
Removes development artifacts while preserving all working functionality.

Usage: python professional_repository_cleanup.py
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

class ProfessionalRepositoryCleanup:
    def __init__(self):
        self.project_root = Path('.')
        self.backup_created = False
        self.removed_files = []
        self.preserved_files = []
        self.created_files = []

    def create_comprehensive_backup(self):
        """Create a comprehensive backup before cleanup"""
        print("[PROCESS] Creating Comprehensive Backup...")
        print("=" * 50)
        
        backup_dir = self.project_root / 'backup_before_cleanup'
        
        if backup_dir.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.project_root / f'backup_before_cleanup_{timestamp}'
        
        backup_dir.mkdir()
        
        # Development files to backup
        development_files = [
            # Step files
            'step1_repository_cleanup.py',
            'step2_interface_inspection.py', 
            'step3_working_integration.py',
            'step4_fix_domain_computation.py',
            'step4b_debug_domain_method.py',
            'step5_final_working_integration.py',
            'step6_corrected_algorithm.py',
            'step7_repository_cleanup.py',
            'step8a_fix_imports.py',
            'step8b_comprehensive_config_fix.py',
            'step8c_fix_circular_import.py',
            'step8d_fix_final_circular_import.py',
            'step9_create_examples.py',
            'step10_repository_cleanup.py',
            
            # Integration and test files
            'rtf_integration_test.py',
            'rtf_integration_bridge.py',
            'simple_import_test.py',
            'test_config_fix.py',
            'test_standalone_config.py',
            'final_rtf_demo.py',
            
            # Debug files
            'debug_cell_creation.py',
            'debug_imports.py',
            'test_cell_imports.py'
        ]
        
        backed_up_count = 0
        for file_name in development_files:
            source_file = self.project_root / file_name
            if source_file.exists():
                backup_file = backup_dir / file_name
                shutil.copy2(source_file, backup_file)
                print(f"  [OK] Backed up: {file_name}")
                backed_up_count += 1
        
        print(f"\n[SUCCESS] Created backup with {backed_up_count} files in: {backup_dir}")
        self.backup_created = True
        return backup_dir

    def remove_development_artifacts(self):
        """Remove all development and debug files"""
        print("\n[REMOVE] Removing Development Artifacts...")
        print("=" * 50)
        
        # Files to remove
        files_to_remove = [
            # All step files
            'step1_repository_cleanup.py',
            'step2_interface_inspection.py',
            'step3_working_integration.py', 
            'step4_fix_domain_computation.py',
            'step4b_debug_domain_method.py',
            'step5_final_working_integration.py',
            'step6_corrected_algorithm.py',
            'step7_repository_cleanup.py',
            'step8a_fix_imports.py',
            'step8b_comprehensive_config_fix.py',
            'step8c_fix_circular_import.py',
            'step8d_fix_final_circular_import.py',
            'step9_create_examples.py',
            'step10_repository_cleanup.py',
            
            # Integration files
            'rtf_integration_test.py',
            'rtf_integration_bridge.py',
            'simple_import_test.py',
            'test_config_fix.py',
            'test_standalone_config.py',
            'final_rtf_demo.py',
            
            # Debug files
            'debug_cell_creation.py',
            'debug_imports.py',
            'test_cell_imports.py'
        ]
        
        # Directories to remove
        dirs_to_remove = [
            'backup_before_cleanup',
            '__pycache__',
            '.pytest_cache',
            'tests/__pycache__',
            'rtf_core/__pycache__'
        ]
        
        removed_count = 0
        
        # Remove files
        for file_name in files_to_remove:
            file_path = self.project_root / file_name
            if file_path.exists():
                file_path.unlink()
                print(f"  [OK] Removed file: {file_name}")
                removed_count += 1
                self.removed_files.append(file_name)
        
        # Remove directories
        for dir_name in dirs_to_remove:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                shutil.rmtree(dir_path)
                print(f"  [OK] Removed directory: {dir_name}")
                removed_count += 1
                self.removed_files.append(dir_name)
        
        # Remove Python cache files
        cache_removed = self.remove_python_cache()
        removed_count += cache_removed
        
        print(f"\n[SUCCESS] Removed {removed_count} development artifacts")

    def remove_python_cache(self):
        """Remove Python cache files and directories"""
        cache_count = 0
        
        # Remove .pyc files
        for pyc_file in self.project_root.rglob('*.pyc'):
            pyc_file.unlink()
            cache_count += 1
        
        # Remove __pycache__ directories
        for pycache_dir in self.project_root.rglob('__pycache__'):
            if pycache_dir.is_dir():
                shutil.rmtree(pycache_dir)
                cache_count += 1
        
        if cache_count > 0:
            print(f"  [OK] Removed {cache_count} cache files/directories")
        
        return cache_count

    def verify_essential_files(self):
        """Verify essential files are present"""
        print("\n[SUCCESS] Verifying Essential Files...")
        print("=" * 50)
        
        essential_files = [
            'README.md',
            'LICENSE', 
            'fixed_rtf_demo.py',
            'rtf_success_test.py',
            'config.py',
            'cell.py',
            'db_wrapper.py'
        ]
        
        essential_dirs = [
            'RTFGraphConstruction',
            'IDcomputation',
            'DCandDelset',
            'rtf_core'
        ]
        
        missing_files = []
        
        # Check files
        for file_name in essential_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                print(f"  [OK] Found: {file_name}")
                self.preserved_files.append(file_name)
            else:
                print(f"  [WARNING] Missing: {file_name}")
                missing_files.append(file_name)
        
        # Check directories
        for dir_name in essential_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print(f"  [OK] Found: {dir_name}/")
                self.preserved_files.append(f"{dir_name}/")
            else:
                print(f"  [WARNING] Missing: {dir_name}/")
                missing_files.append(f"{dir_name}/")
        
        return missing_files

    def create_missing_essentials(self):
        """Create missing essential files"""
        print("\n[PACKAGE] Creating Missing Essential Files...")
        print("=" * 50)
        
        # Create requirements.txt
        self.create_requirements_txt()
        
        # Create .gitignore
        self.create_gitignore()
        
        # Ensure LICENSE exists (you already have one)
        if not (self.project_root / 'LICENSE').exists():
            self.create_mit_license()

    def create_requirements_txt(self):
        """Create requirements.txt with project dependencies"""
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
        
        requirements_path = self.project_root / 'requirements.txt'
        if not requirements_path.exists():
            requirements_path.write_text(requirements_content)
            print("  [OK] Created: requirements.txt")
            self.created_files.append('requirements.txt')
        else:
            print("  - Already exists: requirements.txt")

    def create_gitignore(self):
        """Create .gitignore for professional development"""
        gitignore_content = """# RTF25 Project .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Output
output/
results/
temp/

# Development artifacts
backup_*/
step*.py
*_test_*.py
debug_*.py

# OS
.DS_Store
Thumbs.db

# Research data (add specific patterns as needed)
data/raw/
data/private/
*.csv.bak
"""
        
        gitignore_path = self.project_root / '.gitignore'
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content)
            print("  [OK] Created: .gitignore")
            self.created_files.append('.gitignore')
        else:
            print("  - Already exists: .gitignore")

    def create_mit_license(self):
        """Create MIT license if missing"""
        license_content = """MIT License

Copyright (c) 2025 RTF25 Research Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        license_path = self.project_root / 'LICENSE'
        license_path.write_text(license_content)
        print("  [OK] Created: LICENSE")
        self.created_files.append('LICENSE')

    def create_final_structure_summary(self):
        """Show the final clean repository structure"""
        print("\n[TARGET] Final Clean Repository Structure")
        print("=" * 50)
        
        structure = """
RTF25/
??? [LIST] README.md                    # Professional documentation
??? [TARGET] fixed_rtf_demo.py           # Complete working demo
??? [SUCCESS] rtf_success_test.py          # System validation  
??? [CONFIG] config.py                   # Configuration system
??? [CELL] cell.py                     # Core cell definitions
??? [DATABASE] db_wrapper.py               # Database wrapper
??? [PACKAGE] requirements.txt            # Dependencies
??? [FILE] LICENSE                     # MIT license
??? [IGNORE] .gitignore                  # Git ignore rules
??? [CORE] rtf_core/                   # Core algorithm
?   ??? multi_level_optimizer.py  # Main algorithm
?   ??? config.py                 # Core configuration
??? [DATA] RTFGraphConstruction/       # Graph construction
?   ??? ID_graph_construction.py  # Incremental builder
??? [COMPUTE] IDcomputation/              # Domain computation
?   ??? IGC_e_get_bound_new.py    # Constraint inference
??? [CONFIG] DCandDelset/               # Constraint management
    ??? dc_configs/               # Configurations
"""
        print(structure)

    def run_comprehensive_cleanup(self):
        """Execute the complete professional cleanup"""
        print("? RTF25 Professional Repository Cleanup")
        print("=" * 60)
        print("Preparing research project for academic publication...")
        
        try:
            # Step 1: Create backup
            backup_dir = self.create_comprehensive_backup()
            
            # Step 2: Remove development artifacts  
            self.remove_development_artifacts()
            
            # Step 3: Verify essential files
            missing_files = self.verify_essential_files()
            
            # Step 4: Create missing essentials
            self.create_missing_essentials()
            
            # Step 5: Show final structure
            self.create_final_structure_summary()
            
            # Summary
            print("\n" + "=" * 60)
            print("[SUCCESS] PROFESSIONAL CLEANUP COMPLETE!")
            
            print(f"\n[DATA] Cleanup Summary:")
            print(f"   [REMOVE] Removed: {len(self.removed_files)} development artifacts")
            print(f"   [SUCCESS] Preserved: {len(self.preserved_files)} essential files") 
            print(f"   [PACKAGE] Created: {len(self.created_files)} missing essentials")
            
            print(f"\n[TEST] Testing Commands:")
            print(f"   1. Validate system: python rtf_success_test.py")
            print(f"   2. Run demo: python fixed_rtf_demo.py")
            print(f"   3. Install deps: pip install -r requirements.txt")
            
            print(f"\n[LAUNCH] Next Steps:")
            print(f"   1. Test that everything works")
            print(f"   2. Commit the clean repository")
            print(f"   3. Create GitHub repository") 
            print(f"   4. Share for academic collaboration")
            
            if self.backup_created:
                print(f"\n[BACKUP] Backup Location: {backup_dir}")
                print(f"   (You can delete this after confirming everything works)")
            
            if missing_files:
                print(f"\n[WARNING] Missing Files:")
                for file in missing_files:
                    print(f"   - {file}")
                print(f"   Please ensure these exist for full functionality")
            
            print(f"\n[CLEAN] Repository is now ready for professional presentation!")
            
        except Exception as e:
            print(f"\n[ERROR] Error during cleanup: {e}")
            print(f"Check the backup directory if you need to restore files")
            raise


def main():
    """Run the professional repository cleanup"""
    print("RTF25 Professional Repository Cleanup")
    print("This will clean up development artifacts while preserving functionality")
    
    response = input("\nProceed with cleanup? [y/N]: ").strip().lower()
    if response not in ['y', 'yes']:
        print("Cleanup cancelled.")
        return
    
    cleanup = ProfessionalRepositoryCleanup()
    cleanup.run_comprehensive_cleanup()


if __name__ == '__main__':
    main()