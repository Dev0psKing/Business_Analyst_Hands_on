#!/bin/bash

# =====================================================
# RECURSIVE VIEWER GENERATOR FOR BUSINESS ANALYST
# Automatically creates/updates viewers in ALL folders
# =====================================================

BASE_DIR="/home/uwabor/Videos/Excel tutorial/Business Analyst"

# Find the first generate_viewer.py in the tree
GENERATOR_SCRIPT=$(find "$BASE_DIR" -name "generate_viewer.py" -type f 2>/dev/null | head -1)

# If no generator found, check if there's one in advanced-microsoft-excel
if [ -z "$GENERATOR_SCRIPT" ]; then
    if [ -f "$BASE_DIR/advanced-microsoft-excel/generate_viewer.py" ]; then
        GENERATOR_SCRIPT="$BASE_DIR/advanced-microsoft-excel/generate_viewer.py"
    else
        echo "❌ Error: generate_viewer.py not found"
        echo "   Please place generate_viewer.py in the advanced-microsoft-excel folder first"
        exit 1
    fi
fi

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Business Analyst Course Viewer Updater${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}🔍 Scanning: $BASE_DIR${NC}"
echo ""

total_folders=0
updated_folders=0

while IFS= read -r -d '' folder; do
    html_count=$(find "$folder" -maxdepth 1 -name "*.html" ! -name "viewer*.html" -type f 2>/dev/null | wc -l)
    
    if [ $html_count -gt 0 ]; then
        total_folders=$((total_folders + 1))
        
        rel_path="${folder#$BASE_DIR/}"
        [ -z "$rel_path" ] && rel_path="Business Analyst (root)"
        
        echo -e "${YELLOW}📂 $rel_path${NC}"
        echo "   HTML files: $html_count"
        
        if [ ! -f "$folder/generate_viewer.py" ]; then
            cp "$GENERATOR_SCRIPT" "$folder/" 2>/dev/null
            echo "   📋 Copied generator script"
        fi
        
        cd "$folder"
        if python3 generate_viewer.py > /dev/null 2>&1; then
            echo -e "   ${GREEN}✅ Viewer updated!${NC}"
            updated_folders=$((updated_folders + 1))
        else
            echo "   ❌ Error updating viewer"
        fi
        echo ""
    fi
done < <(find "$BASE_DIR" -type d -print0)

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Complete!${NC}"
echo -e "   Total folders with HTML: $total_folders"
echo -e "   Successfully updated: $updated_folders"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
