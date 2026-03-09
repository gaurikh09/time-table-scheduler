@echo off
echo ========================================
echo Pushing Code to GitHub
echo ========================================
echo.

cd /d "e:\Time table\TT\university_scheduler"

echo Initializing git repository...
git init

echo Adding remote repository...
git remote add origin https://github.com/sanatanisher01/time-table-scheduler.git

echo Adding all files...
git add .

echo Committing changes...
git commit -m "Modern SaaS-style UI redesign with improved dashboard, forms, and timetable views"

echo Pushing to GitHub...
git branch -M main
git push -u origin main --force

echo.
echo ========================================
echo Done! Code pushed to GitHub
echo ========================================
pause
