"""Data migration utilities for MBON project."""

import shutil
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional


class DataMigrator:
    """Handle data migration from python/data to top-level data directory."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the data migrator.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.logger = self._setup_logging()
        
        # Determine paths
        self.script_dir = Path(__file__).parent.parent.parent
        self.project_root = self.script_dir.parent
        
        self.source_data_dir = self.script_dir / "data"
        self.target_data_dir = self.project_root / "data"
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        level = logging.INFO if self.verbose else logging.WARNING
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data_migration.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def migrate(self, force: bool = False) -> bool:
        """Migrate data from python/data to top-level data directory.
        
        Args:
            force: Force migration even if target exists
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Source data directory: {self.source_data_dir}")
        self.logger.info(f"Target data directory: {self.target_data_dir}")
        
        # Check if source exists
        if not self.source_data_dir.exists():
            self.logger.error(f"Source data directory does not exist: {self.source_data_dir}")
            return False
        
        # Check if target already exists
        if self.target_data_dir.exists():
            if not force:
                self.logger.warning(f"Target data directory already exists: {self.target_data_dir}")
                return False
            else:
                self.logger.info("Removing existing target directory")
                shutil.rmtree(self.target_data_dir)
        
        try:
            # Create target directory
            self.target_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all contents from source to target
            self.logger.info("Copying data files...")
            shutil.copytree(self.source_data_dir, self.target_data_dir, dirs_exist_ok=True)
            
            # Create a backup of the original
            backup_dir = self.script_dir / f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.logger.info(f"Creating backup at: {backup_dir}")
            shutil.copytree(self.source_data_dir, backup_dir)
            
            # Remove the original python/data directory
            self.logger.info("Removing original python/data directory")
            shutil.rmtree(self.source_data_dir)
            
            # Create a reference file for backward compatibility
            reference_file = self.script_dir / "data_location.txt"
            with open(reference_file, 'w') as f:
                f.write(f"Data has been migrated to: {self.target_data_dir}\n")
                f.write(f"Migration date: {datetime.now().isoformat()}\n")
                f.write(f"Backup location: {backup_dir}\n")
            
            self.logger.info("Data migration completed successfully!")
            self.logger.info(f"Data is now located at: {self.target_data_dir}")
            self.logger.info(f"Backup created at: {backup_dir}")
            self.logger.info(f"Reference file created at: {reference_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during migration: {e}")
            return False
    
    def update_data_loader_paths(self) -> bool:
        """Update data loader to use the new top-level data directory."""
        loader_file = self.script_dir / "mbon_analysis" / "data" / "loaders.py"
        
        if not loader_file.exists():
            self.logger.warning(f"Loader file not found: {loader_file}")
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
                
                self.logger.info("Updated data loader paths")
                return True
            else:
                self.logger.info("No path updates needed in loader file")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating loader paths: {e}")
            return False
    
    def update_view_generators(self) -> bool:
        """Update view generators to use the new top-level data directory."""
        # Update generate_all_views.py
        views_script = self.script_dir / "scripts" / "generate_all_views.py"
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
                    
                    self.logger.info("Updated generate_all_views.py paths")
                else:
                    self.logger.info("No path updates needed in generate_all_views.py")
                    
            except Exception as e:
                self.logger.error(f"Error updating generate_all_views.py: {e}")
        
        # Update other view generation scripts
        for script_name in ["generate_stations_view.py", "generate_acoustic_distributions.py"]:
            script_path = self.script_dir / "scripts" / script_name
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
                        
                        self.logger.info(f"Updated {script_name} paths")
                    else:
                        self.logger.info(f"No path updates needed in {script_name}")
                        
                except Exception as e:
                    self.logger.error(f"Error updating {script_name}: {e}")
        
        return True
