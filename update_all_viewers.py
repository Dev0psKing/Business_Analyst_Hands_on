# FILE: update_all_viewers.py
# PURPOSE: To run from the root folder (e.g., 'Business Analyst') and automatically
#          generate a modern viewer.html for every single course subfolder with CORRECT paths.
import os

print("🚀 Starting viewer generation process...")

# --- Configuration ---
# This is the main folder that contains all your course categories like 'advanced-microsoft-excel'
# Since this script is in the root, we look for folders in the current directory.
ROOT_SEARCH_PATHS = ["advanced-microsoft-excel", "introduction-to-excel"] # Add other main folders if you have them
# --- End Configuration ---

course_folders = []

# Find all the individual course folders
for search_path in ROOT_SEARCH_PATHS:
    if not os.path.exists(search_path):
        print(f"⚠️ Warning: Search path '{search_path}' not found. Skipping.")
        continue
    
    for item in sorted(os.listdir(search_path)):
        full_path = os.path.join(search_path, item)
        if os.path.isdir(full_path):
            # Special handling for nested project folders
            if item in ["Excel Projects"]:
                for sub_item in sorted(os.listdir(full_path)):
                    sub_full_path = os.path.join(full_path, sub_item)
                    if os.path.isdir(sub_full_path):
                        course_folders.append(sub_full_path)
            else:
                course_folders.append(full_path)


if not course_folders:
    print("❌ Error: No course folders found. Make sure your ROOT_SEARCH_PATHS are correct.")
    exit(1)

print(f"Found {len(course_folders)} course folders to process.")

# --- The HTML Template (with a new placeholder for the dynamic home path) ---
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{COURSE_TITLE} Viewer</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary-green: #16a34a; --primary-green-dark: #15803d; --accent-yellow: #facc15; --light-bg: #f8fafc; --white-bg: #ffffff; --text-dark: #1e293b; --text-gray: #64748b; --border-light: #e2e8f0; --sidebar-bg: #1e293b; --sidebar-text: #d1d5db; --sidebar-text-hover: #ffffff; --sidebar-active-bg: #334155; --border-radius-md: 8px; --transition-ease: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .dark-mode {{
            --light-bg: #111827; --white-bg: #1f2937; --border-light: #374151; --text-dark: #f9fafb; --text-gray: #9ca3af; --sidebar-bg: #0f172a; --sidebar-active-bg: #1e293b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; display: flex; height: 100vh; overflow: hidden; background-color: var(--light-bg); color: var--text-dark; transition: var(--transition-ease); }}
        #sidebar {{ width: 320px; flex-shrink: 0; background: var(--sidebar-bg); color: var(--sidebar-text); display: flex; flex-direction: column; transition: var(--transition-ease); border-right: 1px solid var(--border-light); }}
        .sidebar-header {{ padding: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; gap: 15px; }}
        .sidebar-icon {{ font-size: 28px; color: var(--primary-green); }}
        .sidebar-title h1 {{ font-size: 20px; font-weight: 700; color: #ffffff; line-height: 1.3; margin-bottom: 4px; }}
        .sidebar-title p {{ font-size: 14px; color: var(--text-gray); }}
        .sidebar-controls {{ padding: 15px 20px; }}
        .search-wrapper {{ position: relative; margin-bottom: 10px; }}
        #search {{ width: 100%; padding: 10px 15px 10px 40px; border: 1px solid #475569; border-radius: var(--border-radius-md); background-color: #334155; color: white; font-size: 14px; outline: none; transition: var(--transition-ease); }}
        #search::placeholder {{ color: var(--text-gray); }}
        #search:focus {{ background-color: #475569; border-color: var(--primary-green); }}
        .search-wrapper i {{ position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: var(--text-gray); }}
        .sidebar-btn {{ width: 100%; padding: 10px; border-radius: var(--border-radius-md); border: 1px solid #475569; background: transparent; color: var(--sidebar-text); font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: var(--transition-ease); }}
        .sidebar-btn:hover {{ background-color: #334155; border-color: #64748b; color: var(--sidebar-text-hover); }}
        #fileList {{ flex-grow: 1; overflow-y: auto; padding: 0 10px 10px 10px; }}
        .file-item {{ padding: 12px 15px; margin: 2px 0; border-radius: var(--border-radius-md); cursor: pointer; transition: var(--transition-ease); font-weight: 500; display: flex; align-items: flex-start; gap: 12px; border-left: 3px solid transparent; }}
        .file-item:hover {{ background-color: var(--sidebar-active-bg); color: var(--sidebar-text-hover); }}
        .file-item.active {{ background-color: var(--sidebar-active-bg); color: white; font-weight: 600; border-left-color: var(--accent-yellow); }}
        .file-number {{ color: var(--text-gray); font-weight: 400; }}
        .file-item.active .file-number {{ color: rgba(255, 255, 255, 0.7); }}
        #viewer-container {{ flex-grow: 1; display: flex; flex-direction: column; background-color: var(--white-bg); transition: var(--transition-ease); }}
        #viewer-topbar {{ display: flex; justify-content: space-between; align-items: center; padding: 0 25px; height: 65px; border-bottom: 1px solid var(--border-light); flex-shrink: 0; transition: var(--transition-ease); }}
        #lesson-status {{ font-weight: 500; color: var(--text-gray); }}
        #lesson-status span {{ color: var(--text-dark); font-weight: 600; }}
        .topbar-actions {{ display: flex; align-items: center; gap: 10px; }}
        .nav-btn {{ height: 40px; padding: 0 16px; border: 1px solid var(--border-light); background-color: var(--white-bg); color: var(--text-dark); border-radius: var(--border-radius-md); font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: var(--transition-ease); }}
        .nav-btn:hover:not(:disabled) {{ border-color: var(--text-gray); background-color: var(--light-bg); }}
        .nav-btn.nav-primary {{ background-color: var(--primary-green); color: white; border-color: var(--primary-green); }}
        .nav-btn.nav-primary:hover:not(:disabled) {{ background-color: var(--primary-green-dark); border-color: var(--primary-green-dark); }}
        .nav-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        .icon-btn {{ width: 40px; height: 40px; font-size: 16px; padding: 0; justify-content: center; }}
        #progress-bar-container {{ height: 4px; background-color: var(--border-light); flex-shrink: 0; }}
        #progress-bar {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--primary-green) 0%, var(--accent-yellow) 100%); transition: width 0.5s ease-out; }}
        #content-wrapper {{ flex-grow: 1; position: relative; }}
        iframe {{ width: 100%; height: 100%; border: none; position: absolute; top: 0; left: 0; background-color: var(--white-bg); }}
        #empty-state {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-gray); flex-direction: column; gap: 20px; text-align: center; }}
        #empty-state i {{ font-size: 4rem; opacity: 0.4; color: var(--primary-green); }}
        #empty-state h2 {{ font-size: 1.5rem; color: var(--text-dark); }}
        ::-webkit-scrollbar {{ width: 8px; }} ::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.1); }} ::-webkit-scrollbar-thumb {{ background: #4b5569; border-radius: 4px; }} ::-webkit-scrollbar-thumb:hover {{ background: #64748b; }}
        @media (max-width: 768px) {{ body {{ flex-direction: column; }} #sidebar {{ width: 100%; height: 40%; flex-shrink: 0; }} #viewer-topbar {{ height: 60px; padding: 0 15px; }} .nav-btn span {{ display: none; }} }}
    </style>
</head>
<body>
<aside id="sidebar">
    <div class="sidebar-header">
        <div class="sidebar-icon"><i class="fas fa-file-excel"></i></div>
        <div class="sidebar-title"><h1>{COURSE_TITLE}</h1><p id="lesson-count"></p></div>
    </div>
    <div class="sidebar-controls">
        <div class="search-wrapper"><i class="fas fa-search"></i><input type="text" id="search" placeholder="Search lessons..."></div>
        <button class="sidebar-btn" onclick="toggleDarkMode()"><i class="fas fa-moon"></i> Toggle Dark Mode</button>
    </div>
    <div id="fileList"></div>
</aside>
<main id="viewer-container">
    <div id="viewer-topbar">
        <div id="lesson-status">Select a lesson to begin</div>
        <div class="topbar-actions">
            <a href="{HOME_PATH}" class="nav-btn icon-btn" title="Back to Dashboard"><i class="fas fa-home"></i></a>
            <button class="nav-btn" id="prevBtn" onclick="navigatePrev()" disabled><i class="fas fa-arrow-left"></i> <span>Previous</span></button>
            <button class="nav-btn nav-primary" id="nextBtn" onclick="navigateNext()" disabled><span>Next</span> <i class="fas fa-arrow-right"></i></button>
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
    const files = {FILES_JS};
    let currentIndex = -1;
    const courseTitle = "{COURSE_TITLE}";

    const fileListDiv = document.getElementById('fileList'), contentFrame = document.getElementById('content'), emptyStateDiv = document.getElementById('empty-state'), lessonStatusDiv = document.getElementById('lesson-status'), prevBtn = document.getElementById('prevBtn'), nextBtn = document.getElementById('nextBtn'), searchInput = document.getElementById('search'), progressBar = document.getElementById('progress-bar'), lessonCountP = document.getElementById('lesson-count');

    function cleanFileName(path) {{
        let name = path.split('/').pop().replace(/\\.html$/, '').replace(/[_-]/g, ' ');
        name = name.replace(/Course Exam：/gi, '').replace(/Practice Exam：/gi, '').replace(/Solution/gi, '');
        name = name.replace(/｜ 365 Data Science/gi, '').replace(/\\(d{{2}}_d{{2}}_d{{4}} d{{2}}：d{{2}}：d{{2}}\\)/, '');
        return name.trim().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }}

    function loadFileList() {{
        fileListDiv.innerHTML = '';
        files.forEach((file, index) => {{
            const div = document.createElement('div');
            div.className = 'file-item';
            div.dataset.index = index;
            div.innerHTML = `<span class="file-number">${{String(index + 1).padStart(2, '0')}}.</span><span>${{cleanFileName(file)}}</span>`;
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

        lessonStatusDiv.innerHTML = `Lesson <span>${{index + 1}} of ${{files.length}}</span>: ${{cleanFileName(file)}}`;
        
        document.querySelectorAll('.file-item').forEach(item => {{
            const itemIndex = parseInt(item.dataset.index);
            item.classList.toggle('active', itemIndex === index);
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
# --- End of Template ---


# Loop through each found course folder and generate a viewer
for course_path in course_folders:
    print(f"\nProcessing: {course_path}")
    
    # Sanitize folder name for the title
    course_title = os.path.basename(course_path).replace("-", " ").replace("_", " ").title()

    # Find all HTML files for this specific course
    html_files = []
    for root, dirs, files in os.walk(course_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')] # ignore hidden dirs
        for file in files:
            if file.endswith('.html') and 'viewer.html' not in file.lower():
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, course_path).replace(os.path.sep, '/')
                html_files.append(relative_path)
    
    html_files.sort()

    if not html_files:
        print(f"  -> ⚠️ No lesson files found. Skipping.")
        continue

    # Prepare the list of files for JavaScript injection
    files_js_string = "[\n    " + ",\n    ".join([f'"{f}"' for f in html_files]) + "\n]"

    # ================================================================= #
    # ===== NEW: Dynamically calculate the path back to index.html ==== #
    # ================================================================= #
    depth = len(course_path.split(os.path.sep))
    home_path = os.path.join(*(['..'] * depth), 'index.html').replace(os.path.sep, '/')
    
    # Populate the template with course-specific data, including the new home_path
    final_html = html_template.format(
        COURSE_TITLE=course_title, 
        FILES_JS=files_js_string, 
        HOME_PATH=home_path
    )

    # Write the new viewer.html file inside the course folder
    viewer_file_path = os.path.join(course_path, "viewer.html")
    try:
        with open(viewer_file_path, "w", encoding="utf-8") as f:
            f.write(final_html)
        print(f"  -> ✅ Successfully generated '{viewer_file_path}' with {len(html_files)} lessons and correct home path '{home_path}'.")
    except Exception as e:
        print(f"  -> ❌ Error writing file for {course_path}: {e}")

print("\n\n🎉 All viewers have been updated with correct paths! Please hard-refresh your browser (Ctrl+Shift+R or Cmd+Shift+R).")
