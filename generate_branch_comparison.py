#!/usr/bin/env python3
import json
import html

# Read branch analysis
try:
    with open('branch_analysis.json', 'r') as f:
        branches = json.load(f)
except:
    branches = {}

# Generate HTML
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aurora - Branch Comparison Analysis</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a0a3e 100%);
            color: #e0e0e0;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(90deg, #1a3a52 0%, #663399 100%);
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 5px solid #00ff88;
        }
        
        .header h1 {
            color: #00ff88;
            margin-bottom: 10px;
            font-size: 2.2em;
        }
        
        .header p {
            color: #b0b0b0;
            margin-bottom: 15px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #00ff88;
        }
        
        .stat-value {
            font-size: 1.8em;
            color: #00ff88;
            font-weight: bold;
        }
        
        .stat-label {
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .search-bar {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
        }
        
        .search-bar input {
            flex: 1;
            padding: 12px;
            background: rgba(255,255,255,0.1);
            border: 1px solid #00ff88;
            border-radius: 6px;
            color: #fff;
            font-size: 1em;
        }
        
        .search-bar input::placeholder {
            color: #666;
        }
        
        .branches-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
        }
        
        .branch-card {
            background: rgba(20, 20, 50, 0.8);
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .branch-card:hover {
            background: rgba(30, 30, 80, 0.9);
            border-color: #00ff88;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
        }
        
        .branch-name {
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
            word-break: break-word;
        }
        
        .branch-meta {
            font-size: 0.85em;
            color: #999;
            margin-bottom: 10px;
            line-height: 1.6;
        }
        
        .branch-changes {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #333;
        }
        
        .change-stat {
            padding: 8px;
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
            font-size: 0.85em;
        }
        
        .added {
            color: #00ff88;
        }
        
        .removed {
            color: #ff6b6b;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.75em;
            margin-right: 5px;
        }
        
        .status-ahead {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }
        
        .status-behind {
            background: rgba(255, 107, 107, 0.2);
            color: #ff6b6b;
        }
        
        .last-commit {
            font-size: 0.8em;
            color: #666;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #222;
            word-break: break-word;
        }
        
        .no-results {
            grid-column: 1 / -1;
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌌 Aurora Branch Comparison Analysis</h1>
        <p>Compare all branches to main branch - see what each branch adds, removes, and what works</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">''' + str(len(branches)) + '''</div>
                <div class="stat-label">Total Branches</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">''' + str(sum(1 for b in branches.values() if int(b.get('ahead', 0)) > 0)) + '''</div>
                <div class="stat-label">Ahead of Main</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">''' + str(sum(1 for b in branches.values() if int(b.get('removed_files', 0)) > 0)) + '''</div>
                <div class="stat-label">Modified Structure</div>
            </div>
        </div>
    </div>
    
    <div style="max-width: 1400px; margin: 0 auto;">
        <div class="search-bar">
            <input type="text" id="searchInput" placeholder="Search branches by name or commit..." onkeyup="filterBranches()">
        </div>
        
        <div id="branchesContainer" class="branches-container">'''

# Sort branches by various metrics
branch_list = sorted(branches.items(), key=lambda x: (
    -int(x[1].get('ahead', 0)),
    -int(x[1].get('removed_files', 0)),
    -int(x[1].get('added_files', 0))
))

for branch_name, data in branch_list:
    ahead = int(data.get('ahead', 0))
    behind = int(data.get('behind', 0))
    added = data.get('added_files', 0)
    removed = data.get('removed_files', 0)
    
    status = ""
    if ahead > 0:
        status += f'<span class="status-badge status-ahead">+{ahead} commits</span>'
    if behind > 0:
        status += f'<span class="status-badge status-behind">{behind} behind</span>'
    
    changes = ""
    if added > 0:
        changes += f'<div class="change-stat"><span class="added">✓ +{added} files</span></div>'
    if removed > 0:
        changes += f'<div class="change-stat"><span class="removed">✗ -{removed} files</span></div>'
    
    html_content += f'''
        <div class="branch-card" data-search="{branch_name.lower()} {data.get('last_commit', '').lower()}">
            <div class="branch-name">{html.escape(branch_name)}</div>
            <div class="branch-meta">
                {status}
                <div style="margin-top: 5px;">Total files: {data.get('total_files', 0)}</div>
            </div>
            {changes if changes else '<div style="color: #666;">No changes vs main</div>'}
            <div class="last-commit">
                <strong>Last commit:</strong> {html.escape(data.get('last_commit', 'N/A')[:60])}
            </div>
        </div>'''

html_content += '''
        </div>
    </div>
    
    <script>
        function filterBranches() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.branch-card');
            let visibleCount = 0;
            
            cards.forEach(card => {
                const searchText = card.getAttribute('data-search');
                if (searchText.includes(searchTerm)) {
                    card.style.display = '';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            if (visibleCount === 0) {
                const container = document.getElementById('branchesContainer');
                container.innerHTML = '<div class="no-results">No branches match your search</div>';
            }
        }
    </script>
</body>
</html>'''

with open('AURORA_BRANCH_COMPARISON.html', 'w') as f:
    f.write(html_content)

print("✅ Branch comparison generated: AURORA_BRANCH_COMPARISON.html")
