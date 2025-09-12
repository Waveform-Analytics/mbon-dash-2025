#!/usr/bin/env python3
"""
Marimo Variable Conflict Fixer

This script analyzes marimo notebook files (.py) and automatically fixes variable naming 
conflicts by renaming variables to be unique across all cells.

Marimo notebooks have globally scoped variables, so any variable defined in one cell 
is available in all other cells. This can cause conflicts when the same variable name
is used in multiple cells.

Usage:
    python fix_marimo_variables.py <notebook_file.py>
    python fix_marimo_variables.py <notebook_file.py> --dry-run
    python fix_marimo_variables.py <notebook_file.py> --backup
"""

import ast
import argparse
import re
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import sys


class VariableAnalyzer(ast.NodeVisitor):
    """Analyzes AST to find variable assignments and uses."""
    
    def __init__(self):
        self.assignments: Set[str] = set()
        self.uses: Set[str] = set()
        self.function_defs: Set[str] = set()
        self.imports: Set[str] = set()
        
    def visit_Assign(self, node):
        """Visit assignment nodes (var = value)"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assignments.add(target.id)
            elif isinstance(target, ast.Tuple):
                # Handle tuple unpacking: a, b = something
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.assignments.add(elt.id)
        self.generic_visit(node)
    
    def visit_AugAssign(self, node):
        """Visit augmented assignment nodes (var += value)"""
        if isinstance(node.target, ast.Name):
            self.assignments.add(node.target.id)
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Visit name nodes (variable references)"""
        if isinstance(node.ctx, ast.Load):
            self.uses.add(node.id)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        self.function_defs.add(node.name)
        # Don't visit function body to avoid internal variables
        
    def visit_Import(self, node):
        """Visit import statements"""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.add(name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from ... import statements"""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.add(name)
        self.generic_visit(node)


class MarimoCell:
    """Represents a single marimo cell."""
    
    def __init__(self, cell_text: str, start_line: int, end_line: int, function_name: str):
        self.cell_text = cell_text
        self.start_line = start_line
        self.end_line = end_line
        self.function_name = function_name
        self.assignments: Set[str] = set()
        self.uses: Set[str] = set()
        self.function_defs: Set[str] = set()
        self.imports: Set[str] = set()
        self.analyze_variables()
    
    def analyze_variables(self):
        """Analyze variables in this cell."""
        try:
            # Extract just the function body
            tree = ast.parse(self.cell_text)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == self.function_name:
                    analyzer = VariableAnalyzer()
                    # Visit the function body, not the function itself
                    for stmt in node.body:
                        analyzer.visit(stmt)
                    self.assignments = analyzer.assignments
                    self.uses = analyzer.uses
                    self.function_defs = analyzer.function_defs
                    self.imports = analyzer.imports
                    # print(f"Debug: Cell {self.function_name} analysis - assignments: {self.assignments}, uses: {self.uses}")
                    break
        except SyntaxError as e:
            # print(f"Debug: Syntax error in cell {self.function_name}: {e}")
            # If we can't parse it, skip analysis
            pass
    
    def get_conflicting_assignments(self, global_assignments: Set[str]) -> Set[str]:
        """Get variables assigned in this cell that conflict with global assignments."""
        return self.assignments & global_assignments


class MarimoVariableFixer:
    """Main class for fixing marimo variable conflicts."""
    
    def __init__(self, notebook_path: str):
        self.notebook_path = Path(notebook_path)
        self.content = self.notebook_path.read_text()
        self.lines = self.content.splitlines()
        self.cells: List[MarimoCell] = []
        self.global_assignments: Set[str] = set()
        self.conflicts: Dict[str, List[MarimoCell]] = defaultdict(list)
        self.parse_cells()
        self.find_conflicts()
    
    def parse_cells(self):
        """Parse the notebook file to extract marimo cells."""
        # Look for @app.cell decorator followed by def _(...):
        cell_start_pattern = r'^@app\.cell'
        function_def_pattern = r'^def (_+)\([^)]*\):'
        
        current_line = 0
        while current_line < len(self.lines):
            line = self.lines[current_line]
            
            # Look for @app.cell decorator
            if re.match(cell_start_pattern, line):
                # Find the corresponding function definition
                func_def_line = None
                for i in range(current_line + 1, min(current_line + 5, len(self.lines))):
                    if i < len(self.lines):
                        match = re.match(function_def_pattern, self.lines[i])
                        if match:
                            func_def_line = i
                            function_name = match.group(1)
                            break
                
                if func_def_line is not None:
                    start_line = current_line
                    
                    # Find the end of the cell by looking for the next @app.cell or end of file
                    end_line = len(self.lines)
                    for i in range(func_def_line + 1, len(self.lines)):
                        if re.match(cell_start_pattern, self.lines[i]):
                            end_line = i
                            break
                    
                    # Extract cell content
                    cell_lines = self.lines[start_line:end_line]
                    cell_text = '\n'.join(cell_lines)
                    
                    cell = MarimoCell(cell_text, start_line, end_line, function_name)
                    self.cells.append(cell)
                    
                    # Add to global assignments
                    self.global_assignments.update(cell.assignments)
                    
                    # print(f"Debug: Found cell '{function_name}' with {len(cell.assignments)} assignments: {cell.assignments}")
                    
                    current_line = end_line
                else:
                    current_line += 1
            else:
                current_line += 1
    
    def find_conflicts(self):
        """Find variable conflicts across cells."""
        assignment_counts = defaultdict(int)
        
        # Count assignments per variable
        for cell in self.cells:
            for var in cell.assignments:
                assignment_counts[var] += 1
        
        # Find conflicts (variables assigned in multiple cells)
        for var, count in assignment_counts.items():
            if count > 1:
                conflicting_cells = [cell for cell in self.cells if var in cell.assignments]
                self.conflicts[var] = conflicting_cells
    
    def generate_unique_name(self, base_name: str, cell_index: int, used_names: Set[str]) -> str:
        """Generate a unique variable name."""
        # Try semantic suffixes first based on common patterns
        semantic_suffixes = {
            'ax': ['_plot', '_chart', '_graph', '_viz'],
            'fig': ['_plot', '_chart', '_diagram'],
            'df': ['_data', '_temp', '_proc', '_clean'],
            'data': ['_raw', '_proc', '_clean', '_temp'],
            'result': ['_output', '_final', '_temp'],
        }
        
        # Try semantic naming first
        if base_name in semantic_suffixes:
            for suffix in semantic_suffixes[base_name]:
                candidate = f"{base_name}{suffix}"
                if candidate not in used_names:
                    return candidate
        
        # Fall back to numeric suffixes
        for i in range(1, 100):
            candidate = f"{base_name}_{i}"
            if candidate not in used_names:
                return candidate
        
        # Last resort - use cell index
        return f"{base_name}_cell_{cell_index}"
    
    def fix_conflicts(self) -> str:
        """Fix variable conflicts and return the modified content."""
        if not self.conflicts:
            print("No variable conflicts found!")
            return self.content
        
        print(f"Found {len(self.conflicts)} variable conflicts:")
        for var, cells in self.conflicts.items():
            print(f"  {var}: appears in {len(cells)} cells")
        
        modified_lines = self.lines[:]
        used_names = self.global_assignments.copy()
        
        # Process conflicts
        for var_name, conflicting_cells in self.conflicts.items():
            # Keep the first occurrence, rename others
            for i, cell in enumerate(conflicting_cells[1:], 1):
                new_name = self.generate_unique_name(var_name, i, used_names)
                used_names.add(new_name)
                
                print(f"  Renaming '{var_name}' to '{new_name}' in cell at line {cell.start_line + 1}")
                
                # Replace in cell content
                cell_lines = modified_lines[cell.start_line:cell.end_line]
                modified_cell_lines = []
                
                for line in cell_lines:
                    # Replace variable assignments and uses within this cell
                    # Be careful to only replace whole words
                    pattern = rf'\b{re.escape(var_name)}\b'
                    modified_line = re.sub(pattern, new_name, line)
                    modified_cell_lines.append(modified_line)
                
                # Update the modified lines
                modified_lines[cell.start_line:cell.end_line] = modified_cell_lines
        
        return '\n'.join(modified_lines)
    
    def report_conflicts(self):
        """Print a detailed report of conflicts."""
        if not self.conflicts:
            print("✅ No variable conflicts found!")
            return
        
        print(f"🔍 Found {len(self.conflicts)} variable conflicts in {self.notebook_path.name}:")
        print()
        
        for var_name, cells in self.conflicts.items():
            print(f"Variable '{var_name}' assigned in {len(cells)} cells:")
            for cell in cells:
                print(f"  - Line {cell.start_line + 1}: {cell.function_name}()")
            print()
        
        print("💡 Common conflict patterns:")
        common_vars = ['ax', 'fig', 'df', 'data', 'result', 'temp', 'output']
        found_common = [var for var in common_vars if var in self.conflicts]
        if found_common:
            print(f"  - Plot variables: {[v for v in found_common if v in ['ax', 'fig']]}")
            print(f"  - Data variables: {[v for v in found_common if v in ['df', 'data']]}")
            print(f"  - Temp variables: {[v for v in found_common if v in ['temp', 'result', 'output']]}")


def main():
    parser = argparse.ArgumentParser(description='Fix marimo notebook variable conflicts')
    parser.add_argument('notebook', help='Path to marimo notebook file (.py)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying file')
    parser.add_argument('--backup', action='store_true', help='Create backup before modifying')
    parser.add_argument('--report-only', action='store_true', help='Only report conflicts, don\'t fix them')
    
    args = parser.parse_args()
    
    notebook_path = Path(args.notebook)
    if not notebook_path.exists():
        print(f"Error: File {notebook_path} not found")
        sys.exit(1)
    
    if not notebook_path.suffix == '.py':
        print("Warning: File doesn't have .py extension. Continuing anyway...")
    
    try:
        fixer = MarimoVariableFixer(args.notebook)
        
        if args.report_only:
            fixer.report_conflicts()
            return
        
        if not fixer.conflicts:
            print(f"✅ No conflicts found in {notebook_path.name}")
            return
        
        # Show report
        fixer.report_conflicts()
        
        if args.dry_run:
            print("🔍 DRY RUN - showing changes that would be made:")
            modified_content = fixer.fix_conflicts()
            print("\n" + "="*50 + " MODIFIED CONTENT " + "="*50)
            print(modified_content[:2000] + "..." if len(modified_content) > 2000 else modified_content)
        else:
            # Create backup if requested
            if args.backup:
                backup_path = notebook_path.with_suffix('.py.backup')
                shutil.copy2(notebook_path, backup_path)
                print(f"📁 Backup created: {backup_path}")
            
            # Fix conflicts
            modified_content = fixer.fix_conflicts()
            
            # Write modified content
            notebook_path.write_text(modified_content)
            print(f"✅ Fixed conflicts in {notebook_path.name}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()