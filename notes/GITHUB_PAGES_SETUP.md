# GitHub Pages Automatic Deployment Setup

This document describes the automated deployment system for the Marine Acoustic Discovery Report.

## 🎯 Overview

The system automatically:
1. **Generates ML report figures** when notebooks change
2. **Renders QMD to HTML** using Quarto
3. **Copies files to `docs/` folder** at project root
4. **Deploys to GitHub Pages** automatically on every push

## 📁 File Structure

```
mbon-dash-2025/
├── docs/                           # 🌐 GitHub Pages deployment folder
│   ├── index.html                  # Main report (auto-generated)
│   ├── images/                     # All figures (auto-generated)
│   ├── .nojekyll                   # GitHub Pages optimization
│   └── README.md                   # Deployment info
├── .github/workflows/
│   └── deploy-report.yml           # 🤖 GitHub Actions workflow
└── python/acoustic_vs_environmental/
    ├── Marine_Acoustic_Discovery_Report_v2.qmd  # 📝 Source document
    ├── prepare_github_pages.py     # 🔧 Deployment script
    └── build_and_deploy_report.py  # 🔧 Netlify script (backup)
```

## 🚀 How It Works

### Automatic Triggers
The GitHub Actions workflow triggers when you push changes to:
- `python/acoustic_vs_environmental/Marine_Acoustic_Discovery_Report_v2.qmd`
- `python/acoustic_vs_environmental/output/**`
- `dashboard/public/views/notebooks/**`
- `python/scripts/notebooks/generate_ml_report_figures.py`
- `.github/workflows/deploy-report.yml`

### Deployment Process
1. **Setup Environment**: Python 3.11 + uv + Quarto
2. **Generate Figures**: Run ML figure generation script
3. **Render Report**: Convert QMD → HTML
4. **Copy to docs/**: Organize files for GitHub Pages
5. **Commit Changes**: Auto-commit docs/ folder
6. **Deploy**: Push to GitHub Pages

## ⚙️ Initial Setup Instructions

### Step 1: Enable GitHub Pages
1. Go to your repository **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main` (or `master`)
4. **Folder**: `/docs`
5. Click **Save**

### Step 2: Commit and Push
```bash
# From project root
git add docs/
git add .github/
git commit -m "Add GitHub Pages deployment structure"
git push
```

### Step 3: Verify Workflow
1. Go to **Actions** tab in GitHub
2. Watch the "Deploy Marine Acoustic Discovery Report" workflow
3. Once complete, visit: `https://[your-username].github.io/[repository-name]/`

## 🔧 Manual Operations

### Generate and Deploy Locally
```bash
# From python/acoustic_vs_environmental/
uv run python prepare_github_pages.py
```

### Just Render QMD
```bash
# From python/acoustic_vs_environmental/
quarto render Marine_Acoustic_Discovery_Report_v2.qmd
```

### Generate Just the ML Figures
```bash
# From python/
uv run python scripts/notebooks/generate_ml_report_figures.py
```

## 🌐 Access URLs

Once deployed, your report will be available at:
- **Live Site**: `https://[your-username].github.io/[repository-name]/`
- **Docs Folder**: Repository `/docs/` directory
- **Source**: Repository `/python/acoustic_vs_environmental/Marine_Acoustic_Discovery_Report_v2.qmd`

## 🔍 Troubleshooting

### If Deployment Fails
1. Check **Actions** tab for error messages
2. Verify all paths in `.github/workflows/deploy-report.yml`
3. Ensure `pyproject.toml` exists in `python/` directory
4. Confirm Quarto can render the QMD file locally

### If Images Don't Show
1. Check that figures exist in `/docs/images/`
2. Verify image paths in HTML use `images/filename.png`
3. Ensure `.nojekyll` file exists in `/docs/`

### If Changes Don't Trigger Deployment
1. Verify the file paths in the workflow trigger conditions
2. Check that your branch name matches (main vs master)
3. Make sure you're pushing to the correct branch

## 📊 Current Status

- ✅ **docs/ folder created**: Ready for GitHub Pages
- ✅ **GitHub Actions workflow**: Configured for automatic deployment
- ✅ **ML figures generated**: All visualization assets ready
- ✅ **QMD rendered**: HTML report created
- 🔄 **Next**: Enable GitHub Pages in repository settings

## 🎉 Benefits

- **Automatic updates**: Report updates whenever you push changes
- **Version control**: Full history of report changes
- **Easy sharing**: Public URL for collaborators
- **No manual deployment**: Set it and forget it
- **Professional presentation**: Clean, accessible structure

## 🛠️ Backup Options

If GitHub Pages doesn't work, you also have:
1. **Netlify deployment**: Use `build_and_deploy_report.py` → drag `netlify_deploy/` to Netlify
2. **Local HTML**: Open `docs/index.html` directly in browser
3. **Manual export**: Copy `docs/` contents to any web server

---

*This setup ensures your Marine Acoustic Discovery Report stays current with your latest research findings automatically!*