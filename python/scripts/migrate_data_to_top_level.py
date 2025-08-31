#!/usr/bin/env python3
"""Migrate data from python/data to top-level data directory.

This script helps reorganize the data structure by moving data from the
python/data directory to a top-level data directory for better organization
and shared access between Python backend and Next.js frontend.
"""

import shutil
from pathlib import Path
import sys
import logging
from datetime import datetime


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data_migration.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def migrate_data():
    """Migrate data from python/data to top-level data directory."""
    logger = logging.getLogger(__name__)
    
    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    source_data_dir = script_dir.parent / "data"
    target_data_dir = project_root / "data"
    
    logger.info(f"Source data directory: {source_data_dir}")
    logger.info(f"Target data directory: {target_data_dir}")
    
    # Check if source exists
    if not source_data_dir.exists():
        logger.error(f"Source data directory does not exist: {source_data_dir}")
        return False
    
    # Check if target already exists
    if target_data_dir.exists():
        logger.warning(f"Target data directory already exists: {target_data_dir}")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            logger.info("Migration cancelled by user")
            return False
        else:
            logger.info("Removing existing target directory")
            shutil.rmtree(target_data_dir)
    
    try:
        # Create target directory
        target_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all contents from source to target
        logger.info("Copying data files...")
        shutil.copytree(source_data_dir, target_data_dir, dirs_exist_ok=True)
        
        # Create a backup of the original
        backup_dir = script_dir.parent / f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Creating backup at: {backup_dir}")
        shutil.copytree(source_data_dir, backup_dir)
        
        # Remove the original python/data directory
        logger.info("Removing original python/data directory")
        shutil.rmtree(source_data_dir)
        
        # Create a symlink or reference file for backward compatibility
        reference_file = script_dir.parent / "data_location.txt"
        with open(reference_file, 'w') as f:
            f.write(f"Data has been migrated to: {target_data_dir}\n")
            f.write(f"Migration date: {datetime.now().isoformat()}\n")
            f.write(f"Backup location: {backup_dir}\n")
        
        logger.info("Data migration completed successfully!")
        logger.info(f"Data is now located at: {target_data_dir}")
        logger.info(f"Backup created at: {backup_dir}")
        logger.info(f"Reference file created at: {reference_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False


def update_data_loader_paths():
    """Update data loader to use the new top-level data directory."""
    logger = logging.getLogger(__name__)
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    loader_file = script_dir.parent / "mbon_analysis" / "data" / "loaders.py"
    
    if not loader_file.exists():
        logger.warning(f"Loader file not found: {loader_file}")
        return False
    
    try:
        # Read the current loader file
        with open(loader_file, 'r') as f:
            content = f.read()
        
        # Update the default data root path
        old_path = 'current_file.parent.parent.parent / "data"'
        new_path = 'current_file.parent.parent.parent.parent / "data"'
        
        if old_path in content:
            content = content.replace(old_path, new_path)
            
            # Write the updated content
            with open(loader_file, 'w') as f:
                f.write(content)
            
            logger.info("Updated data loader paths")
            return True
        else:
            logger.info("No path updates needed in loader file")
            return True
            
    except Exception as e:
        logger.error(f"Error updating loader paths: {e}")
        return False


def update_view_generators():
    """Update view generators to use the new top-level data directory."""
    logger = logging.getLogger(__name__)
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Update generate_all_views.py
    views_script = script_dir / "generate_all_views.py"
    if views_script.exists():
        try:
            with open(views_script, 'r') as f:
                content = f.read()
            
            # Update the data root path
            old_path = 'current_dir / "data"'
            new_path = 'current_dir.parent / "data"'
            
            if old_path in content:
                content = content.replace(old_path, new_path)
                
                with open(views_script, 'w') as f:
                    f.write(content)
                
                logger.info("Updated generate_all_views.py paths")
            else:
                logger.info("No path updates needed in generate_all_views.py")
                
        except Exception as e:
            logger.error(f"Error updating generate_all_views.py: {e}")
    
    # Update other view generation scripts
    for script_name in ["generate_stations_view.py", "generate_acoustic_distributions.py"]:
        script_path = script_dir / script_name
        if script_path.exists():
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Update the data root path
                old_path = 'current_dir / "data"'
                new_path = 'current_dir.parent / "data"'
                
                if old_path in content:
                    content = content.replace(old_path, new_path)
                    
                    with open(script_path, 'w') as f:
                        f.write(content)
                    
                    logger.info(f"Updated {script_name} paths")
                else:
                    logger.info(f"No path updates needed in {script_name}")
                    
            except Exception as e:
                logger.error(f"Error updating {script_name}: {e}")
    
    return True


def main():
    """Main execution function."""
    logger = setup_logging()
    
    print("MBON Data Migration Tool")
    print("========================")
    print("This tool will migrate data from python/data to a top-level data directory.")
    print("This improves organization and allows both Python backend and Next.js frontend to access the same data.")
    print()
    
    response = input("Do you want to proceed with the migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled.")
        return
    
    print("\nStarting migration...")
    
    # Perform migration
    if migrate_data():
        print("\nMigration completed successfully!")
        
        # Update loader paths
        if update_data_loader_paths():
            print("Data loader paths updated.")
        else:
            print("Warning: Could not update data loader paths. You may need to update them manually.")
        
        # Update view generator paths
        if update_view_generators():
            print("View generator paths updated.")
        else:
            print("Warning: Could not update view generator paths. You may need to update them manually.")
        
        print("\nNext steps:")
        print("1. Update your .gitignore to include the new data directory if needed")
        print("2. Test that your Python scripts can still access the data")
        print("3. Update any hardcoded paths in your dashboard code")
        print("4. Consider updating your CDN sync process for the new data location")
        
    else:
        print("\nMigration failed! Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
