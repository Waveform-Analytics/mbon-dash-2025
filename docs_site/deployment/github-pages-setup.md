# GitHub Pages Setup Guide

This guide shows how to deploy the MkDocs documentation site to GitHub Pages with automatic deployment.

## Overview

The documentation site is automatically deployed to GitHub Pages using GitHub Actions whenever changes are pushed to the main branch that affect documentation files.

## Setup Steps

### 1. Enable GitHub Pages

1. Go to your repository: https://github.com/Waveform-Analytics/mbon-dash-2025/
2. Navigate to **Settings** → **Pages**
3. Under "Source", select **GitHub Actions**
4. The workflow will handle the rest automatically

### 2. Verify Workflow Files

The following files should be in your repository:

```
.github/workflows/docs.yml    # GitHub Actions workflow
pyproject.toml               # Python dependencies (including MkDocs)
mkdocs.yml                   # MkDocs configuration
docs_site/                   # Documentation content
```

### 3. Test Local Deployment

Before pushing changes, test the documentation locally:

```bash
# Install dependencies with uv
uv sync

# Serve locally
uv run mkdocs serve

# Visit http://localhost:8000
```

### 4. Trigger Deployment

Deployment is triggered automatically when you:

- Push changes to the `main` branch
- Modify files in `docs_site/` directory
- Update `mkdocs.yml` configuration
- Change the workflow file itself

You can also trigger deployment manually:

1. Go to **Actions** tab in GitHub
2. Select "Deploy MkDocs to GitHub Pages"
3. Click "Run workflow"

## Site URL

Once deployed, your documentation will be available at:

**https://waveform-analytics.github.io/mbon-dash-2025/**

## Workflow Features

### Automatic Triggers
- Pushes to main branch affecting documentation
- Manual workflow dispatch
- Only rebuilds when documentation files change

### Performance Optimizations
- Caches Python dependencies between runs
- Only runs when documentation files are modified
- Concurrent deployment protection

### Build Process
1. **Checkout**: Downloads repository code
2. **Install uv**: Installs the uv package manager
3. **Setup Python**: Installs Python 3.12 via uv
4. **Install Dependencies**: Runs `uv sync` to install from pyproject.toml
5. **Build Site**: Runs `uv run mkdocs build` to generate static HTML
6. **Deploy**: Uploads to GitHub Pages

## Configuration

### MkDocs Configuration
Key settings in `mkdocs.yml`:

```yaml
site_name: MBON Marine Biodiversity Dashboard
repo_url: https://github.com/Waveform-Analytics/mbon-dash-2025/
docs_dir: docs_site
site_dir: site

theme:
  name: material
  palette:
    - scheme: default
      primary: blue
      accent: cyan
```

### GitHub Action Configuration
Key workflow settings in `.github/workflows/docs.yml`:

```yaml
# Trigger conditions
on:
  push:
    branches: [ main ]
    paths:
      - 'docs_site/**'
      - 'mkdocs.yml'
      - '.github/workflows/docs.yml'

# Permissions for GitHub Pages
permissions:
  contents: read
  pages: write
  id-token: write
```

## Troubleshooting

### Common Issues

!!! warning "Build Failure"
    **Problem**: GitHub Action fails during build
    
    **Solutions**:
    - Check the Actions tab for detailed error logs
    - Verify `mkdocs.yml` syntax is valid
    - Ensure all referenced files exist in `docs_site/`
    - Test locally with `mkdocs build --strict`

!!! info "Site Not Updating"
    **Problem**: Changes not appearing on GitHub Pages
    
    **Solutions**:
    - Check if the workflow was triggered (Actions tab)
    - GitHub Pages can take a few minutes to update
    - Clear your browser cache
    - Verify changes were pushed to the main branch

!!! error "Permission Denied"
    **Problem**: Workflow can't deploy to Pages
    
    **Solutions**:
    - Ensure GitHub Pages is set to "GitHub Actions" source
    - Check repository settings → Actions → General permissions
    - Verify the workflow has `pages: write` permission

### Debugging Steps

1. **Check workflow status**:
   - Go to Actions tab in GitHub repository
   - Look for red X (failed) or green checkmark (success)
   - Click on failed runs to see error details

2. **Test locally**:
   ```bash
   # Install exact same dependencies as GitHub
   uv sync
   
   # Build with strict mode (same as GitHub Action)
   uv run mkdocs build --clean --strict
   ```

3. **Validate configuration**:
   ```bash
   # Check MkDocs config syntax
   uv run mkdocs config
   
   # List all pages that will be built
   uv run mkdocs build --clean --verbose
   ```

## Customization

### Adding New Pages
1. Create markdown file in `docs_site/`
2. Add to navigation in `mkdocs.yml`
3. Push to main branch
4. Site rebuilds automatically

### Changing Theme
Update `mkdocs.yml` theme settings:

```yaml
theme:
  name: material
  palette:
    - scheme: default
      primary: blue    # Change primary color
      accent: cyan     # Change accent color
```

### Adding Plugins
1. Add plugin to `pyproject.toml` dependencies
2. Configure in `mkdocs.yml` plugins section
3. Run `uv sync` to install locally

## Best Practices

### Content Organization
- Keep documentation in logical sections
- Use descriptive file names
- Include navigation in `mkdocs.yml`
- Test all links and references

### Performance
- Optimize images and diagrams
- Use caching for large builds
- Keep plugin usage minimal
- Monitor build times in Actions

### Maintenance
- Update dependencies regularly
- Test major changes locally first
- Monitor GitHub Actions for failures
- Keep documentation current with code changes

---

!!! success "Ready to Deploy"
    Your documentation site is now configured for automatic deployment to GitHub Pages! Every time you update documentation files and push to main, the site will rebuild automatically.

*Next: [CDN Setup](cdn-setup.md)*