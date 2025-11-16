#!/bin/bash
set -e

BASE_DIR="/home/uwabor/Videos/Excel tutorial/Business Analyst"
cd "$BASE_DIR"

echo "🚀 Starting complete automated setup..."

# Step 1: Create a universal generate_viewer.py that works everywhere
cat > generate_viewer_universal.py << 'VIEWER_EOF'
import os
import glob

# Find all HTML files recursively
html_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith('.html') and 'viewer' not in file.lower():
            rel_path = os.path.relpath(os.path.join(root, file), ".")
            html_files.append(rel_path)

html_files.sort()

if len(html_files) == 0:
    print("❌ No HTML files found")
    exit(1)

files_js = "[\n    " + ",\n    ".join([f'"{f}"' for f in html_files]) + "\n]"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Excel 365 Course Viewer</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; height: 100vh; background: #f5f5f5; }
#sidebar { width: 320px; background: linear-gradient(135deg, #217346 0%, #1a5c37 100%); color: white; overflow-y: auto; padding: 20px; box-shadow: 2px 0 10px rgba(0,0,0,0.1); }
#sidebar h1 { font-size: 20px; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 2px solid rgba(255,255,255,0.3); }
.file-item { background: rgba(255,255,255,0.1); padding: 10px; margin: 6px 0; border-radius: 5px; cursor: pointer; transition: all 0.3s; }
.file-item:hover { background: rgba(255,255,255,0.2); transform: translateX(5px); }
.file-item.active { background: rgba(255,255,255,0.25); }
#viewer { flex: 1; display: flex; flex-direction: column; }
iframe { flex: 1; border: none; width: 100%; height: 100%; }
#bottombar { background: white; padding: 12px 20px; border-top: 1px solid #ddd; display: flex; align-items: center; justify-content: space-between; }
.nav-btn { padding: 10px 20px; background: #217346; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
.nav-btn:disabled { background: #ccc; cursor: not-allowed; }
</style>
</head>
<body>
<div id="sidebar">
<h1>📚 Course Lessons</h1>
<p style="opacity:0.8;margin-bottom:15px;font-size:13px;">""" + str(len(html_files)) + """ Files</p>
<div id="fileList"></div>
</div>
<div id="viewer">
<iframe id="content" style="display:none;"></iframe>
<div id="bottombar">
<button class="nav-btn" id="prevBtn" onclick="navigatePrev()" disabled>← Previous</button>
<div id="current-file" style="flex:1;text-align:center;font-weight:bold;">Select a lesson</div>
<button class="nav-btn" id="nextBtn" onclick="navigateNext()" disabled>Next →</button>
</div>
</div>
<script>
const files = """ + files_js + """;
let currentIndex = -1;
function loadFileList() {
    const fileListDiv = document.getElementById('fileList');
    files.forEach((file, index) => {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `<div><span style="font-weight:bold;margin-right:8px;">${index + 1}.</span>${file.split('/').pop()}</div>`;
        div.onclick = () => loadFile(index);
        fileListDiv.appendChild(div);
    });
}
function loadFile(index) {
    currentIndex = index;
    document.getElementById('content').src = files[index];
    document.getElementById('content').style.display = 'block';
    document.getElementById('current-file').textContent = `${index + 1} of ${files.length}`;
    document.querySelectorAll('.file-item').forEach((item, i) => item.classList.toggle('active', i === index));
    document.getElementById('prevBtn').disabled = index === 0;
    document.getElementById('nextBtn').disabled = index === files.length - 1;
}
function navigatePrev() { if (currentIndex > 0) loadFile(currentIndex - 1); }
function navigateNext() { if (currentIndex < files.length - 1) loadFile(currentIndex + 1); }
loadFileList();
</script>
</body>
</html>"""

with open("viewer.html", "w") as f:
    f.write(html_content)

print(f"✅ Generated viewer.html with {len(html_files)} files!")
VIEWER_EOF

# Step 2: Deploy viewers to all folders with HTML files
echo "📦 Deploying viewers to all course folders..."
find "advanced-microsoft-excel" -type f -name "*.html" -not -name "viewer.html" | while read htmlfile; do
    folder=$(dirname "$htmlfile")
    if [ ! -f "$folder/viewer.html" ]; then
        echo "  Creating viewer in: $folder"
        cp generate_viewer_universal.py "$folder/"
        (cd "$folder" && python3 generate_viewer_universal.py)
    fi
done

# Step 3: Generate dashboard that finds all viewers
echo "📊 Generating dashboard..."
python3 << 'DASHBOARD_EOF'
import os
import glob

courses = []
base = "advanced-microsoft-excel"

# Find all viewer.html files
for viewer in glob.glob(f"{base}/**/viewer.html", recursive=True):
    folder = os.path.dirname(viewer)
    folder_name = os.path.basename(folder)
    parent = os.path.basename(os.path.dirname(folder))
    
    # Count HTML files
    html_count = len([f for f in glob.glob(os.path.join(folder, "**/*.html"), recursive=True) if 'viewer' not in f])
    
    if html_count > 0:
        display_name = f"{parent} - {folder_name}" if parent in ["Excel Projects", "introduction-to-excel"] else folder_name
        courses.append({
            "name": display_name.replace("-", " ").replace("_", " ").title(),
            "path": viewer,
            "lessons": html_count
        })

courses.sort(key=lambda x: x['name'])

cards = "".join([f'''<a href="{c['path']}" class="course-card">
<div class="course-icon">📚</div>
<div class="course-title">{c['name']}</div>
<div class="course-info">{c['lessons']} lessons</div>
<span class="course-badge">Course</span>
</a>
''' for c in courses])

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Business Analyst Course Hub</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
.container{{max-width:1400px;width:100%}}
.header{{text-align:center;color:white;margin-bottom:50px}}
.header h1{{font-size:48px;margin-bottom:10px;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}}
.courses-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:25px}}
.course-card{{background:white;border-radius:15px;padding:25px;box-shadow:0 10px 30px rgba(0,0,0,0.2);transition:transform 0.3s;cursor:pointer;text-decoration:none;color:inherit;display:block}}
.course-card:hover{{transform:translateY(-10px)}}
.course-icon{{font-size:42px;margin-bottom:12px}}
.course-title{{font-size:20px;font-weight:bold;color:#333;margin-bottom:8px}}
.course-info{{color:#666;font-size:13px;margin-bottom:12px}}
.course-badge{{display:inline-block;background:#667eea;color:white;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:bold}}
.stats{{background:rgba(255,255,255,0.2);border-radius:15px;padding:20px;margin-top:30px;color:white;text-align:center}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>📊 Business Analyst Course Hub</h1>
<p style="font-size:18px;opacity:0.9">Your Complete Excel Learning Journey</p>
</div>
<div class="courses-grid">
{cards}
</div>
<div class="stats">
<h3>📈 Progress</h3>
<p>{sum(c['lessons'] for c in courses)} Lessons • {len(courses)} Courses</p>
</div>
</div>
</body>
</html>'''

with open("index.html", "w") as f:
    f.write(html)

print(f"✅ Dashboard created with {len(courses)} courses!")
DASHBOARD_EOF

echo ""
echo "✅ COMPLETE! All viewers created and dashboard updated."
echo "   Refresh your browser: http://localhost:8000/index.html"

