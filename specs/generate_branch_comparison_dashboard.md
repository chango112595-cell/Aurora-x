# SpecV3: Generate Branch Comparison Dashboard

## Task
Create an interactive HTML dashboard that compares all changes between the 'draft' and 'main' branches in the Aurora-x repository. The dashboard should have clickable tabs, filters, sortable columns, and search functionality.

## Requirements
1. Run git commands to get the diff between origin/main and draft
2. Parse the output to extract:
   - File status (Added, Modified, Deleted)
   - File paths
   - Lines added/removed
   - File type categorization (Docs, Config, Code, Binary, Assets)
3. Generate a professional HTML file with:
   - Interactive tabs for filtering by status and type
   - Sortable table columns
   - Search box to filter by filename
   - Modern CSS styling with good UX
   - Summary statistics (total files, insertions, deletions)
4. Save the output as `BRANCH_COMPARISON_DASHBOARD.html`

## Function Signature
```python
def generate_branch_comparison_dashboard(base_branch: str = "origin/main", compare_branch: str = "draft", output_file: str = "BRANCH_COMPARISON_DASHBOARD.html") -> str
```

## Examples
```python
generate_branch_comparison_dashboard("origin/main", "draft", "BRANCH_COMPARISON_DASHBOARD.html")
# Returns: "Dashboard created: BRANCH_COMPARISON_DASHBOARD.html with 13 files compared"
```

## Post-conditions
- File must be valid HTML with embedded CSS and JavaScript
- All git diff data must be accurately represented
- Interactive features (tabs, search, sort) must work in browser
- Summary statistics must be calculated correctly
- File categorization must be logical (by extension and path)
