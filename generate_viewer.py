# FILE: generate_viewer.py (place this inside each course folder and run)
import os
import glob

# --- This script is designed to be run from within a course folder ---

# Automatically determine the course title from the current folder name
current_folder_name = os.path.basename(os.getcwd())
COURSE_TITLE = current_folder_name.replace("-", " ").replace("_", " ").title()

# Find all HTML files recursively in the current directory and its subdirectories
html_files = []
for root, dirs, files in os.walk("."):
    # Exclude hidden directories (like .git)
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for file in files:
        if file.endswith('.html') and 'viewer.html' not in file.lower():
            # Create a relative path from the current directory
            rel_path = os.path.relpath(os.path.join(root, file), ".").replace(os.path.sep, '/')
            html_files.append(rel_path)

# Sort files for consistent order
html_files.sort()

if len(html_files) == 0:
    print(f"❌ No lesson HTML files found in '{current_folder_name}'.")
    exit(1)

# Format the file list for injection into JavaScript
files_js = "[\n    " + ",\n    ".join([f'"{f}"' for f in html_files]) + "\n]"

# The new, world-class viewer HTML template
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{COURSE_TITLE} Viewer</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary-blue: #4a6ee0; --secondary-dark-blue: #2c4da5; --accent-purple: #8b5cf6; --light-bg: #f8fafc; --white-bg: #ffffff; --text-dark: #1e293b; --text-gray: #64748b; --border-light: #e2e8f0; --sidebar-bg: #111827; --sidebar-text: #d1d5db; --sidebar-text-hover: #ffffff; --border-radius-md: 8px; --transition-ease: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .dark-mode {{
            --light-bg: #111827; --white-bg: #1f2937; --border-light: #374151; --text-dark: #f9fafb; --text-gray: #9ca3af; --sidebar-bg: #0d1117;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; display: flex; height: 100vh; overflow: hidden; background-color: var(--light-bg); color: var(--text-dark); transition: var(--transition-ease); }}
        #sidebar {{ width: 320px; flex-shrink: 0; background: var(--sidebar-bg); color: var(--sidebar-text); display: flex; flex-direction: column; transition: var(--transition-ease); border-right: 1px solid var(--border-light); }}
        .sidebar-header {{ padding: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }}
        .sidebar-title h1 {{ font-size: 20px; font-weight: 700; color: #ffffff; line-height: 1.3; margin-bottom: 4px; }}
        .sidebar-title p {{ font-size: 14px; color: var(--text-gray); }}
        .search-wrapper {{ padding: 15px 20px; position: relative; }}
        #search {{ width: 100%; padding: 12px 15px 12px 40px; border: 1px solid var(--border-light); border-radius: var(--border-radius-md); background-color: #2c3548; color: white; font-size: 14px; outline: none; transition: var(--transition-ease); }}
        #search::placeholder {{ color: var(--text-gray); }}
        #search:focus {{ background-color: #38435c; border-color: var(--primary-blue); }}
        .search-wrapper i {{ position: absolute; left: 35px; top: 50%; transform: translateY(-50%); color: var(--text-gray); }}
        #fileList {{ flex-grow: 1; overflow-y: auto; padding: 0 10px 10px 10px; }}
        .file-item {{ padding: 12px 15px; margin: 2px 0; border-radius: var(--border-radius-md); cursor: pointer; transition: var(--transition-ease); font-weight: 500; display: flex; align-items: flex-start; gap: 12px; }}
        .file-item:hover {{ background-color: rgba(255, 255, 255, 0.08); color: var(--sidebar-text-hover); }}
        .file-item.active {{ background-color: var(--primary-blue); color: white; font-weight: 600; }}
        .file-number {{ color: var(--text-gray); font-weight: 400; }}
        .file-item.active .file-number {{ color: rgba(255, 255, 255, 0.7); }}
        #viewer-container {{ flex-grow: 1; display: flex; flex-direction: column; background-color: var(--white-bg); transition: var(--transition-ease); }}
        #viewer-topbar {{ display: flex; justify-content: space-between; align-items: center; padding: 0 25px; height: 65px; border-bottom: 1px solid var(--border-light); flex-shrink: 0; transition: var(--transition-ease); }}
        #breadcrumbs {{ font-weight: 500; color: var(--text-gray); }}
        #breadcrumbs span {{ color: var(--text-dark); font-weight: 600; }}
        .topbar-actions {{ display: flex; align-items: center; gap: 10px; }}
        .nav-btn {{ height: 40px; padding: 0 16px; border: 1px solid var(--border-light); background-color: var(--white-bg); color: var(--text-dark); border-radius: var(--border-radius-md); font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: var(--transition-ease); }}
        .nav-btn:hover:not(:disabled) {{ border-color: var(--text-gray); background-color: var(--light-bg); }}
        .nav-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        .icon-btn {{ width: 40px; height: 40px; font-size: 16px; padding: 0; justify-content: center; }}
        #progress-bar-container {{ height: 4px; background-color: var(--border-light); flex-shrink: 0; }}
        #progress-bar {{ height: 100%; width: 0%; background-color: var(--primary-blue); transition: width 0.5s ease-out; }}
        #content-wrapper {{ flex-grow: 1; position: relative; }}
        iframe {{ width: 100%; height: 100%; border: none; position: absolute; top: 0; left: 0; background-color: var(--white-bg); }}
        #empty-state {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-gray); flex-direction: column; gap: 20px; text-align: center; }}
        #empty-state i {{ font-size: 4rem; opacity: 0.4; }}
        #empty-state h2 {{ font-size: 1.5rem; color: var(--text-dark); }}
        ::-webkit-scrollbar {{ width: 8px; }} ::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.1); }} ::-webkit-scrollbar-thumb {{ background: #4b5563; border-radius: 4px; }} ::-webkit-scrollbar-thumb:hover {{ background: #6b7280; }}
        @media (max-width: 768px) {{ body {{ flex-direction: column; }} #sidebar {{ width: 100%; height: 40%; flex-shrink: 0; }} #viewer-topbar {{ height: 60px; padding: 0 15px; }} .nav-btn span {{ display: none; }} }}
    </style>
</head>
<body>
<aside id="sidebar">
    <div class="sidebar-header">
        <div class="sidebar-title"><h1>{COURSE_TITLE}</h1><p id="lesson-count"></p></div>
    </div>
    <div class="search-wrapper"><i class="fas fa-search"></i><input type="text" id="search" placeholder="Search lessons..."></div>
    <div id="fileList"></div>
</aside>
<main id="viewer-container">
    <div id="viewer-topbar">
        <div id="breadcrumbs">Select a lesson to begin</div>
        <div class="topbar-actions">
            <a href="../../index.html" class="nav-btn icon-btn" title="Back to Dashboard"><i class="fas fa-home"></i></a>
            <button class="nav-btn" id="prevBtn" onclick="navigatePrev()" disabled><i class="fas fa-arrow-left"></i> <span>Previous</span></button>
            <button class="nav-btn" id="nextBtn" onclick="navigateNext()" disabled><span>Next</span> <i class="fas fa-arrow-right"></i></button>
            <button class="nav-btn icon-btn" onclick="toggleDarkMode()" title="Toggle Dark Mode"><i class="fas fa-moon"></i></button>
        </div>
    </div>
    <div id="progress-bar-container"><div id="progress-bar"></div></div>
    <div id="content-wrapper">
        <iframe id="content" style="display:none;"></iframe>
        <div id="empty-state">
            <i class="fas fa-graduation-cap"></i>
            <h2>Welcome to {COURSE_TITLE}</h2>
            <p>Select a lesson from the sidebar to start your learning journey.</p>
        </div>
    </div>
</main>
<script>
    const files = {files_js};
    let currentIndex = -1;
    const courseTitle = "{COURSE_TITLE}";

    const fileListDiv = document.getElementById('fileList');
    const contentFrame = document.getElementById('content');
    const emptyStateDiv = document.getElementById('empty-state');
    const breadcrumbsDiv = document.getElementById('breadcrumbs');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const searchInput = document.getElementById('search');
    const progressBar = document.getElementById('progress-bar');
    const lessonCountP = document.getElementById('lesson-count');

    function cleanFileName(path) {{
        let name = path.split('/').pop().replace(/\\.html$/, '').replace(/[_-]/g, ' ');
        // Basic cleaning of common prefixes/suffixes
        name = name.replace(/Course Exam：/i, '').replace(/Practice Exam：/i, '');
        name = name.replace(/｜ 365 Data Science/i, '').replace(/\\(d{2}_d{2}_d{4} d{2}：d{2}：d{2}\\)/, '');
        return name.trim().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }}

    function loadFileList() {{
        fileListDiv.innerHTML = '';
        files.forEach((file, index) => {{
            const div = document.createElement('div');
            div.className = 'file-item';
            div.dataset.index = index;
            div.innerHTML = `<span class="file-number">${{String(index + 1).padStart(2, '0')}}</span><span>${{cleanFileName(file)}}</span>`;
            div.onclick = () => loadFile(index);
            fileListDiv.appendChild(div);
        }});
        lessonCountP.textContent = `${{files.length}} Lessons`;
    }}

    function loadFile(index) {{
        if (index < 0 || index >= files.length) return;
        currentIndex = index;
        const file = files[index];

        contentFrame.src = encodeURI(file);
        contentFrame.style.display = 'block';
        emptyStateDiv.style.display = 'none';

        breadcrumbsDiv.innerHTML = `${{courseTitle}} / <span>Lesson ${{index + 1}}</span>`;
        
        document.querySelectorAll('.file-item').forEach(item => {{
            item.classList.toggle('active', parseInt(item.dataset.index) === index);
        }});
        
        prevBtn.disabled = index === 0;
        nextBtn.disabled = index === files.length - 1;

        const progress = ((index + 1) / files.length) * 100;
        progressBar.style.width = `${{progress}}%`;
        
        localStorage.setItem(`lastLesson_${{courseTitle}}`, index);
    }}

    function navigatePrev() {{ if (currentIndex > 0) loadFile(currentIndex - 1); }}
    function navigateNext() {{ if (currentIndex < files.length - 1) loadFile(currentIndex + 1); }}

    function toggleDarkMode() {{
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    }}

    searchInput.addEventListener('input', function() {{
        const filter = this.value.toLowerCase();
        document.querySelectorAll('.file-item').forEach(item => {{
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(filter) ? 'flex' : 'none';
        }});
    }});

    window.onload = () => {{
        loadFileList();
        if (localStorage.getItem('darkMode') === 'true') {{
            document.body.classList.add('dark-mode');
        }}
        const lastLesson = localStorage.getItem(`lastLesson_${{courseTitle}}`);
        if (lastLesson !== null) {{
            loadFile(parseInt(lastLesson));
        }}
    }};
</script>
</body>
</html>"""

# Write the final HTML to viewer.html
with open("viewer.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Generated new viewer.html for '{COURSE_TITLE}' with {len(html_files)} lessons!")
