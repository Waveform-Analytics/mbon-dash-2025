# Archived Documentation

These documents have been archived as their content has been reorganized into the MkDocs documentation site at `docs_site/`.

## Migration Status

### ✅ Fully Migrated
- **ACOUSTIC_INDICES_INTEGRATION_PLAN.md** → See `docs_site/for-scientists/acoustic-indices.md` and `docs_site/analysis/pca-workflow.md`
- **Research context** → See `docs_site/for-scientists/research-questions.md`
- **Data structure info** → See `docs_site/data/structure.md`

### 📌 Useful Reference (Not Migrated)
These documents contain implementation details or historical planning that may still be useful:

- **CLOUDFLARE_R2_SETUP.md** - Step-by-step CDN deployment guide
- **adding-stations-to-map-guide.md** - Detailed map implementation tutorial
- **dashboard_plan.md** - Original project planning
- **site-restructuring-plan.md** - Dashboard page restructuring plans
- **species-activity-timeline-design.md** - Component design specifications
- **future-improvements.md** - Feature roadmap

## Accessing Current Documentation

The active documentation is now maintained in MkDocs format:

```bash
# View documentation locally
cd docs_site
uv run mkdocs serve

# Or view markdown files directly in docs_site/
```

The MkDocs site provides better organization with separate sections for:
- Scientists (`docs_site/for-scientists/`)
- Developers (`docs_site/for-developers/`)
- Analysis workflows (`docs_site/analysis/`)
- Reference materials (`docs_site/reference/`)