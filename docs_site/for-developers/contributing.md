# Contributing

Guidelines for contributing to the MBON dashboard project.

## Getting Started

### Development Environment
```bash
# Clone repository
git clone [repository-url]
cd mbon-dash-2025

# Install dependencies
uv sync              # Python
npm install          # Node.js

# Get and process data
npm run download-data
npm run process-data
npm run validate-data

# Start development
npm run dev
```

### Project Structure Understanding
Before contributing, familiarize yourself with:
- **[Architecture overview](architecture.md)** - System design and data flow
- **[Data structure documentation](../data/structure.md)** - How data is organized
- **[Command reference](../reference/commands.md)** - Available development commands

## Development Workflow

### Data Processing Changes
If modifying data processing logic:

1. **Test with existing data first**:
   ```bash
   # Run validation to establish baseline
   npm run validate-data
   npm run data-stats
   
   # Make your changes to processing scripts
   
   # Re-run validation to compare results
   npm run validate-data
   npm run data-stats
   ```

2. **Document data structure changes**:
   - Update TypeScript interfaces in `src/types/data.ts`
   - Update data structure documentation
   - Add validation rules for new fields

3. **Test pipeline steps individually**:
   ```bash
   # Test specific processing steps
   uv run scripts/pipeline/steps/1_process_raw_data.py
   uv run scripts/pipeline/steps/2_align_temporal_windows.py
   # etc.
   ```

### Frontend Changes  
If modifying dashboard components:

1. **Maintain type safety**:
   ```bash
   # Check types before committing
   npm run type-check
   
   # Fix linting issues
   npm run lint
   ```

2. **Test data loading hooks**:
   - Verify data still loads correctly after interface changes
   - Test error handling for malformed data
   - Check loading states and user feedback

3. **Validate chart rendering**:
   - Test with different data subsets
   - Verify responsive behavior
   - Check accessibility

## Code Standards

### Python Code Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and returns
- Document functions with docstrings
- Handle errors gracefully with informative messages

```python
def process_acoustic_indices(
    file_path: str, 
    station: str, 
    year: int
) -> pd.DataFrame:
    """
    Process acoustic indices from CSV file.
    
    Args:
        file_path: Path to acoustic indices CSV file
        station: Station identifier (e.g., "9M")
        year: Year of data collection
        
    Returns:
        DataFrame with processed acoustic indices
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If required columns are missing
    """
    try:
        df = pd.read_csv(file_path)
        # Processing logic here
        return df
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        raise
```

### TypeScript Code Style
- Use strict TypeScript configuration
- Prefer interfaces over types for object shapes
- Use meaningful variable and function names
- Comment complex business logic

```typescript
interface ChartProps {
  data: AcousticIndicesRecord[]
  selectedIndices: string[]
  onIndexSelect: (indices: string[]) => void
  height?: number
}

export function AcousticIndicesChart({ 
  data, 
  selectedIndices, 
  onIndexSelect,
  height = 400 
}: ChartProps) {
  // Component implementation
}
```

### Documentation Standards
- Update documentation when changing functionality
- Include code examples in documentation
- Explain biological/scientific context for acoustic indices
- Use clear, jargon-free language for scientists unfamiliar with web development

## Testing Guidelines

### Data Processing Tests
```python
def test_acoustic_indices_processing():
    """Test that acoustic indices are processed correctly."""
    # Create test data
    test_data = pd.DataFrame({
        'datetime': ['2021-05-01T10:00:00'],
        'ZCR': [0.123],
        'ACI': [0.456]
    })
    
    # Process data
    result = process_acoustic_indices(test_data, '9M', 2021)
    
    # Verify results
    assert 'station' in result.columns
    assert result['station'].iloc[0] == '9M'
    assert not result['ZCR'].isna().any()
```

### Frontend Tests
```typescript
import { render, screen } from '@testing-library/react'
import { AcousticIndicesChart } from './AcousticIndicesChart'

test('displays chart with provided data', () => {
  const testData: AcousticIndicesRecord[] = [
    {
      station: '9M',
      year: 2021,
      datetime: '2021-05-01T10:00:00Z',
      ZCR: 0.123,
      ACI: 0.456
    }
  ]
  
  render(
    <AcousticIndicesChart 
      data={testData}
      selectedIndices={['ZCR', 'ACI']}
      onIndexSelect={() => {}}
    />
  )
  
  expect(screen.getByRole('img')).toBeInTheDocument()
})
```

### Integration Tests
```bash
# Test full pipeline with sample data
npm run build-data
npm run validate-data

# Verify dashboard loads with processed data
npm run dev
# Manual verification that pages load without errors
```

## Pull Request Process

### Before Submitting
1. **Run full validation**:
   ```bash
   npm run type-check
   npm run lint
   npm run validate-data
   ```

2. **Test changes locally**:
   - Process data with your changes
   - Start dashboard and verify functionality
   - Test different data subsets and edge cases

3. **Update documentation**:
   - Update relevant documentation files
   - Add code examples if introducing new APIs
   - Update command reference if adding new scripts

### PR Description Template
```markdown
## Changes Made
Brief description of what changed and why.

## Data Impact
- [ ] No changes to data structure
- [ ] Modified data processing logic
- [ ] Added new data fields
- [ ] Changed analysis methods

## Testing
- [ ] Ran data validation successfully
- [ ] Tested dashboard functionality
- [ ] Updated relevant tests
- [ ] Verified backward compatibility

## Documentation  
- [ ] Updated relevant documentation
- [ ] Added code examples where needed
- [ ] Updated TypeScript interfaces if needed

## Deployment Notes
Any special considerations for deploying these changes.
```

## Issue Reporting

### Data Processing Issues
When reporting data processing problems:

```markdown
**Data Processing Issue**

**Expected Behavior**: What should happen
**Actual Behavior**: What actually happens
**Error Messages**: Include full error text
**Data Context**: 
- Which files are affected
- Station/year combinations
- Data size/scope

**Reproduction Steps**:
1. Run command X
2. See error Y

**Environment**:
- Python version: 
- uv version:
- Operating system:
```

### Dashboard Issues  
When reporting dashboard problems:

```markdown
**Dashboard Issue**

**Bug Description**: Clear description of the problem
**Steps to Reproduce**:
1. Navigate to page X
2. Click button Y
3. See error Z

**Expected vs Actual**:
- Expected: Should display chart
- Actual: Shows error message

**Environment**:
- Browser and version:
- Screen size/device:
- Console errors (if any):
```

## Scientific Context

### Understanding the Research
Contributors should understand:
- **Goal**: Identify acoustic indices that predict marine biodiversity
- **Data types**: Species detections, acoustic indices, environmental measurements
- **Analysis methods**: PCA for dimensionality reduction, correlation analysis
- **Output**: Recommendations for cost-effective monitoring approaches

### Domain Knowledge
Helpful to understand:
- **Acoustic indices**: Mathematical summaries of soundscape recordings
- **Marine biodiversity**: Species detection through hydrophone recordings
- **PCA (Principal Component Analysis)**: Statistical method for reducing data dimensions
- **Temporal alignment**: Matching different data collection frequencies

### Research Sensitivity
Be aware that:
- This is active research - findings may influence marine monitoring practices
- Data processing errors could affect scientific conclusions
- Clear documentation helps researchers understand and trust the analysis
- Reproducibility is critical for scientific validity

## Communication

### Getting Help
- **Technical questions**: Create GitHub issues with detailed context
- **Scientific questions**: Include biological context and research goals
- **Data questions**: Provide specific file names and error messages

### Code Reviews
- Focus on correctness and maintainability
- Consider impacts on research reproducibility  
- Suggest improvements for scientific workflow
- Ask questions if biological context isn't clear

### Documentation Contributions
Particularly valuable:
- Examples showing how to use new features
- Explanations of scientific concepts for developers
- Troubleshooting guides for common issues
- Cross-references between data processing and dashboard features

Contributing to this project helps advance marine biodiversity research by making acoustic monitoring more accessible and cost-effective.