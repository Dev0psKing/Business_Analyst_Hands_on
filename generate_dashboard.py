# FILE: generate_dashboard.py
import os
import glob

# --- Configuration ---
BASE_PATH = "advanced-microsoft-excel"
DASHBOARD_TITLE = "Business Analyst Course Hub"
DASHBOARD_SUBTITLE = "Your Complete Excel Learning Journey"
# --- End Configuration ---

courses = []

# Helper function to assign icons based on course name
def get_course_icon(name):
    name = name.lower()
    if "exam" in name: return "fas fa-award"
    if "project" in name: return "fas fa-project-diagram"
    if "quiz" in name: return "fas fa-question-circle"
    if "pivot" in name: return "fas fa-table"
    if "database" in name: return "fas fa-database"
    return "fas fa-file-excel" # Default icon

# Scan for course folders
if not os.path.exists(BASE_PATH):
    print(f"❌ Error: Base path '{BASE_PATH}' not found. Make sure this script is in the correct root directory.")
    exit(1)

for folder in sorted(os.listdir(BASE_PATH)):
    folder_path = os.path.join(BASE_PATH, folder)
    if os.path.isdir(folder_path):
        # Handle nested project folders
        if folder in ["Excel Projects", "introduction-to-excel"]:
            for subfolder in sorted(os.listdir(folder_path)):
                subfolder_path = os.path.join(folder_path, subfolder)
                if os.path.isdir(subfolder_path):
                    viewer_path = os.path.join(subfolder_path, "viewer.html")
                    if os.path.exists(viewer_path):
                        html_count = len(glob.glob(f"{subfolder_path}/**/*.html", recursive=True)) - 1
                        if html_count > 0:
                            courses.append({
                                "name": subfolder.replace("-", " ").replace("_", " ").title(),
                                "path": os.path.join(BASE_PATH, folder, subfolder, "viewer.html").replace(os.path.sep, '/'),
                                "lessons": html_count
                            })
        else:
            # Regular course folders
            viewer_path = os.path.join(folder_path, "viewer.html")
            if os.path.exists(viewer_path):
                # Count HTML files recursively, excluding the viewer itself
                html_count = len(glob.glob(f"{folder_path}/**/*.html", recursive=True)) - 1
                if html_count > 0:
                     courses.append({
                        "name": folder.replace("-", " ").replace("_", " ").title(),
                        "path": os.path.join(BASE_PATH, folder, "viewer.html").replace(os.path.sep, '/'),
                        "lessons": html_count
                    })

# Generate HTML cards from the new template
course_cards_html = ""
for course in courses:
    is_project = "project" in course['name'].lower()
    badge_text = "Project" if is_project else "Course"
    badge_style = "background-color: var(--accent-purple);" if is_project else ""
    image_class = "project" if is_project else ""
    icon_class = get_course_icon(course['name'])

    course_cards_html += f"""
                <a href="{course['path']}" class="course-link">
                    <div class="course-card">
                        <span class="course-badge" style="{badge_style}">{badge_text}</span>
                        <div class="course-image {image_class}">
                            <i class="{icon_class}"></i>
                        </div>
                        <div class="course-content">
                            <h3 class="course-title">{course['name']}</h3>
                            <div class="course-info">
                                <div class="course-meta">
                                    <i class="fas fa-book-reader"></i>
                                    <span>{course['lessons']} lessons</span>
                                </div>
                            </div>
                            <div class="course-actions">
                                <span class="course-status not-started">Ready to start</span>
                                <button class="btn btn-primary btn-sm">View Course <i class="fas fa-arrow-right"></i></button>
                            </div>
                        </div>
                    </div>
                </a>"""

total_lessons = sum(c['lessons'] for c in courses)
total_courses = len(courses)

# The full, new world-class HTML template for index.html
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{DASHBOARD_TITLE}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary-blue: #4a6ee0; --secondary-dark-blue: #2c4da5; --accent-green: #34d399; --accent-orange: #f59e0b; --accent-purple: #8b5cf6; --light-bg: #f8fafc; --white-bg: #ffffff; --text-dark: #1e293b; --text-gray: #64748b; --border-light: #e2e8f0; --border-radius-lg: 16px; --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1); --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.15); --transition-ease: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background-color: var(--light-bg); color: var(--text-dark); line-height: 1.6; min-height: 100vh; }}
        a {{ text-decoration: none; color: inherit; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 0 25px; }}
        main {{ flex-grow: 1; padding: 40px 0; }}
        .dashboard-header {{ text-align: center; margin-bottom: 50px; }}
        .dashboard-header h1 {{ font-size: 48px; font-weight: 800; color: var(--text-dark); margin-bottom: 15px; }}
        .dashboard-header p {{ color: var(--text-gray); font-size: 20px; max-width: 600px; margin: 0 auto; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 25px; margin-bottom: 50px; }}
        .stat-card {{ background: var(--white-bg); border-radius: var(--border-radius-lg); padding: 28px; box-shadow: var(--shadow-md); display: flex; align-items: center; gap: 20px; transition: var(--transition-ease); border: 1px solid var(--border-light); }}
        .stat-card:hover {{ transform: translateY(-7px); box-shadow: var(--shadow-lg); }}
        .stat-icon {{ width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 26px; flex-shrink: 0; }}
        .stat-icon.blue {{ background: rgba(74, 110, 224, 0.1); color: var(--primary-blue); }}
        .stat-icon.green {{ background: rgba(52, 211, 153, 0.1); color: var(--accent-green); }}
        .stat-info h3 {{ font-size: 30px; font-weight: 800; margin-bottom: 4px; }}
        .stat-info p {{ color: var(--text-gray); font-size: 14px; font-weight: 500; }}
        .section-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .section-title {{ font-size: 28px; font-weight: 700; }}
        .courses-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px; margin-bottom: 50px; }}
        .course-card {{ background: var(--white-bg); border-radius: var(--border-radius-lg); overflow: hidden; box-shadow: var(--shadow-md); transition: var(--transition-ease); position: relative; border: 1px solid var(--border-light); display: flex; flex-direction: column; }}
        .course-card:hover {{ transform: translateY(-10px); box-shadow: var(--shadow-lg); }}
        .course-badge {{ position: absolute; top: 15px; right: 15px; background: var(--primary-blue); color: white; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; z-index: 2; }}
        .course-image {{ height: 180px; background: linear-gradient(135deg, var(--primary-blue) 0%, #63b3ed 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 56px; }}
        .course-image.project {{ background: linear-gradient(135deg, var(--accent-purple) 0%, #c4b5fd 100%); }}
        .course-content {{ padding: 25px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
        .course-title {{ font-size: 19px; font-weight: 700; margin-bottom: 10px; line-height: 1.4; }}
        .course-info {{ display: flex; gap: 15px; font-size: 14px; color: var(--text-gray); }}
        .course-meta {{ display: flex; align-items: center; gap: 6px; font-weight: 500; }}
        .course-meta i {{ color: var(--primary-blue); }}
        .course-actions {{ display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding-top: 15px; border-top: 1px solid var(--border-light); }}
        .course-status {{ font-size: 14px; font-weight: 600; color: var(--text-gray); }}
        .btn {{ padding: 12px 24px; border-radius: 30px; border: none; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: var(--transition-ease); }}
        .btn-primary {{ background: var(--primary-blue); color: white; }}
        .btn-primary:hover {{ background: var(--secondary-dark-blue); }}
        .btn-sm {{ padding: 9px 18px; font-size: 14px; }}
        .footer {{ text-align: center; padding: 40px 0; color: var(--text-gray); font-size: 14px; border-top: 1px solid var(--border-light); margin-top: 50px; }}
    </style>
</head>
<body>
<main>
    <div class="container">
        <section class="dashboard-header">
            <h1>📊 {DASHBOARD_TITLE}</h1>
            <p>{DASHBOARD_SUBTITLE}</p>
        </section>
        <section class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon blue"><i class="fas fa-book"></i></div>
                <div class="stat-info">
                    <h3>{total_courses}</h3><p>Total Courses</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon green"><i class="fas fa-check-circle"></i></div>
                <div class="stat-info">
                    <h3>{total_lessons}</h3><p>Total Lessons</p>
                </div>
            </div>
        </section>
        <section>
            <div class="section-header"><h2 class="section-title">Available Courses</h2></div>
            <div class="courses-grid">{course_cards_html}</div>
        </section>
    </div>
</main>
<footer class="footer">
    <p>&copy; 2024 Business Analyst Course Hub. All rights reserved.</p>
</footer>
</body>
</html>
"""

# Write the final HTML to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"✅ Generated index.html with {total_courses} courses and {total_lessons} total lessons!")
