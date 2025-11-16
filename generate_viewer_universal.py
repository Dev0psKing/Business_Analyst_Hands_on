# FILE: generate_viewer.py (place this inside each course folder)
import os
import glob

# --- This script is designed to be run from within a course folder ---

# Automatically determine the course title from the current folder name
current_folder_name = os.path.basename(os.getcwd())
COURSE_TITLE = current_folder_name.replace("-", " ").replace("_", " ").title()

# Find all HTML files recursively in the current directory and its subdirectories
html_files = []
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for file in files:
        if file.endswith('.html') and 'viewer.html' not in file.lower():
            rel_path = os.path.relpath(os.path.join(root, file), ".").replace(os.path.sep, '/')
            html_files.append(rel_path)

html_files.sort()

if len(html_files) == 0:
    print(f"❌ No lesson HTML files found in '{current_folder_name}'.")
    exit(1)

files_js = "[\n    " + ",\n    ".join([f'"{f}"' for f in html_files]) + "\n]"

# The world-class viewer HTML template
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{COURSE_TITLE} Viewer</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --sidebar-bg: linear-gradient(160deg, #1e6440 0%, #124027 100%); --light-bg: #f8fafc; --white-bg: #ffffff; --border-light: #e2e8f0; --text-dark: #1e293b; --text-light: #e2e8f0; --text-gray: #64748b; --accent-green: #4ade80; --accent-yellow: #facc15; --border-radius-md: 8px; --transition-ease: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
        .dark-mode {{ --sidebar-bg: linear-gradient(160deg, #1a1d21 0%, #0f1012 100%); --light-bg: #111827; --white-bg: #1f2937; --border-light: #374151; --text-dark: #f9fafb; --text-light: #9ca3af; --text-gray: #9ca3af; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; display: flex; height: 100vh; overflow: hidden; background-color: var(--light-bg); color: var(--text-dark); transition: var(--transition-ease); }}
        #sidebar {{ width: 320px; flex-shrink: 0; background: var(--sidebar-bg); color: var(--text-light); display: flex; flex-direction: column; padding: 25px; transition: var(--transition-ease); }}
        .sidebar-header {{ display: flex; align-items: center; gap: 15px; padding-bottom: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }}
        .sidebar-icon {{ font-size: 28px; color: var(--accent-green); }}
        .sidebar-title h1 {{ font-size: 22px; font-weight: 700; color: #ffffff; line-height: 1.2; }}
        .sidebar-title p {{ font-size: 14px; opacity: 0.8; }}
        .sidebar-controls {{ padding: 20px 0; }}
        .search-wrapper {{ position: relative; margin-bottom: 15px; }}
        #search {{ width: 100%; padding: 12px 15px 12px 40px; border: none; border-radius: var(--border-radius-md); background-color: rgba(0,0,0,0.2); color: white; font-size: 14px; outline: none; transition: var(--transition-ease); }}
        #search::placeholder {{ color: rgba(255,255,255,0.6); }}
        #search:focus {{ background-color: rgba(0,0,0,0.4); }}
        .search-wrapper i {{ position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: rgba(255,255,255,0.6); }}
        .sidebar-btn {{ width: 100%; padding: 12px; border-radius: 50px; border: 1px solid rgba(255,255,255,0.2); background: transparent; color: white; font-weight: 600; cursor: pointer; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; gap: 10px; transition: var(--transition-ease); }}
        .sidebar-btn:hover {{ background-color: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.4); }}
        #fileList {{ flex-grow: 1; overflow-y: auto; margin-right: -15px; padding-right: 15px; }}
        .file-item {{ padding: 14px 12px; margin: 4px 0; border-radius: var(--border-radius-md); cursor: pointer; transition: var(--transition-ease); border-left: 4px solid transparent; font-weight: 500; }}
        .file-item:hover {{ background-color: rgba(255, 255, 255, 0.08); transform: translateX(5px); }}
        .file-item.active {{ background-color: rgba(255, 255, 255, 0.15); border-left-color: var(--accent-yellow); color: white; font-weight: 600; }}
        .file-number {{ opacity: 0.7; margin-right: 10px; }}
        #viewer-container {{ flex-grow: 1; display: flex; flex-direction: column; background-color: var(--white-bg); transition: var(--transition-ease); }}
        #viewer-topbar {{ display: flex; justify-content: space-between; align-items: center; padding: 15px 25px; border-bottom: 1px solid var(--border-light); flex-shrink: 0; transition: var(--transition-ease); }}
        #lesson-status {{ font-weight: 600; color: var(--text-gray); }}
        #navigation {{ display: flex; gap: 10px; }}
        .nav-btn {{ padding: 8px 16px; border: 1px solid var(--border-light); background-color: var(--white-bg); color: var(--text-dark); border-radius: var(--border-radius-md); font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: var(--transition-ease); }}
        .nav-btn:hover:not(:disabled) {{ border-color: var(--text-gray); background-color: var(--light-bg); }}
        .nav-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        #content-wrapper {{ flex-grow: 1; position: relative; }}
        iframe {{ width: 100%; height: 100%; border: none; position: absolute; top: 0; left: 0; }}
        #empty-state {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-gray); font-size: 1.2rem; flex-direction: column; gap: 15px; }}
        #empty-state i {{ font-size: 3rem; opacity: 0.5; }}
        ::-webkit-scrollbar {{ width: 8px; }} ::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.1); }} ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.3); border-radius: 4px; }} ::-webkit-scrollbar-thumb:hover {{ background: rgba(255,255,255,0.5); }}
        @media (max-width: 768px) {{ body {{ flex-direction: column; }} #sidebar {{ width: 100%; height: 250px; flex-shrink: 0; padding: 15px; }} .sidebar-header {{ padding-bottom: 10px; }} .sidebar-title h1 {{ font-size: 20px; }} .sidebar-controls {{ display: none; }} #fileList {{ margin-right: -10px; padding-right: 10px; }} }}
    </style>
</head>
<body>
<aside id="sidebar">
    <div class="sidebar-header">
        <a href="../../index.html" style="text-decoration: none; color: inherit; display: flex; align-items: center; gap: 15px;">
            <div class="sidebar-icon"><i class="fas fa-file-excel"></i></div>
            <div class="sidebar-title"><h1>{COURSE_TITLE}</h1></div>
        </a>
    </div>
    <div class="sidebar-controls">
        <div class="search-wrapper"><i class="fas fa-search"></i><input type="text" id="search" placeholder="Search lessons..."></div>
        <button class="sidebar-btn" onclick="openAllTabs()"><i class="fas fa-external-link-alt"></i> Open All in Tabs</button>
        <button class="sidebar-btn" onclick="toggleDarkMode()"><i class="fas fa-moon"></i> Toggle Dark Mode</button>
        <a href="../../index.html" class="sidebar-btn" style="justify-content: center;"><i class="fas fa-arrow-left"></i> Back to Dashboard</a>
    </div>
    <div id="fileList"></div>
</aside>
<main id="viewer-container">
    <div id="viewer-topbar"><div id="lesson-status">Select a lesson to begin</div><div id="navigation"><button class="nav-btn" id="prevBtn" onclick="navigatePrev()" disabled><i class="fas fa-arrow-left"></i> Previous</button><button class="nav-btn" id="nextBtn" onclick="navigateNext()" disabled>Next <i class="fas fa-arrow-right"></i></button></div></div>
    <div id="content-wrapper"><iframe id="content" style="display:none;"></iframe><div id="empty-state"><i class="fas fa-hand-pointer"></i><span>Select a lesson to start learning</span></div></div>
</main>
<script>
    const files = {files_js};
    let currentIndex = -1;
    const courseTitle = "{COURSE_TITLE}";
    const fileListDiv = document.getElementById('fileList'), contentFrame = document.getElementById('content'), emptyStateDiv = document.getElementById('empty-state'), lessonStatusDiv = document.getElementById('lesson-status'), prevBtn = document.getElementById('prevBtn'), nextBtn = document.getElementById('nextBtn'), searchInput = document.getElementById('search');
    function cleanFileName(path) {{ return path.split('/').pop().replace(/\\.html$/, '').replace(/[_-]/g, ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '); }}
    function loadFileList() {{ fileListDiv.innerHTML = ''; files.forEach((file, index) => {{ const div = document.createElement('div'); div.className = 'file-item'; div.dataset.index = index; div.innerHTML = `<span class="file-number">${{index + 1}}.</span>${{cleanFileName(file)}}`; div.onclick = () => loadFile(index); fileListDiv.appendChild(div); }}); document.querySelector('.sidebar-title').insertAdjacentHTML('beforeend', `<p>${{files.length}} Lessons</p>`); }}
    function loadFile(index) {{ if (index < 0 || index >= files.length) return; currentIndex = index; const file = files[index]; contentFrame.src = encodeURI(file); contentFrame.style.display = 'block'; emptyStateDiv.style.display = 'none'; lessonStatusDiv.textContent = `Lesson ${{index + 1}} of ${{files.length}}: ${{cleanFileName(file)}}`; document.querySelectorAll('.file-item').forEach(item => {{ item.classList.toggle('active', parseInt(item.dataset.index) === index); }}); prevBtn.disabled = index === 0; nextBtn.disabled = index === files.length - 1; localStorage.setItem(`lastLesson_${{courseTitle}}`, index); }}
    function navigatePrev() {{ if (currentIndex > 0) loadFile(currentIndex - 1); }}
    function navigateNext() {{ if (currentIndex < files.length - 1) loadFile(currentIndex + 1); }}
    function openAllTabs() {{ if (confirm(`This will open ${{files.length}} new tabs. Are you sure?`)) {{ files.forEach(file => window.open(encodeURI(file), '_blank')); }} }}
    function toggleDarkMode() {{ document.body.classList.toggle('dark-mode'); localStorage.setItem('darkMode', document.body.classList.contains('dark-mode')); }}
    searchInput.addEventListener('input', function() {{ const filter = this.value.toLowerCase(); document.querySelectorAll('.file-item').forEach(item => {{ const text = item.textContent.toLowerCase(); item.style.display = text.includes(filter) ? 'block' : 'none'; }}); }});
    window.onload = () => {{ loadFileList(); if (localStorage.getItem('darkMode') === 'true') document.body.classList.add('dark-mode'); const lastLesson = localStorage.getItem(`lastLesson_${{courseTitle}}`); if (lastLesson !== null) loadFile(parseInt(lastLesson)); }};
</script>
</body>
</html>"""

with open("viewer.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Generated viewer.html for '{COURSE_TITLE}' with {len(html_files)} lessons!")
