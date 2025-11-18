#!/bin/bash
cd "/home/uwabor/Videos/Excel tutorial/Business Analyst"
echo "📚 Updating course viewers..."
./update_all_viewers.py
echo ""
echo "🏠 Updating dashboard..."
python3 generate_dashboard.py
echo ""
echo "🎉 Everything updated! Open index.html to see changes."
