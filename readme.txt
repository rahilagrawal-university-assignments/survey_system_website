# External python libraries:
Werkzeug 0.12.2
progressbar2 3.34.3
Flask 0.12.2
Flask-Login 0.4.0
Flask-Script 2.0.6
Jinja2 2.9.6

# Command:
python3 run.py start
http://127.0.0.1:5000

# Tests:
py tests.py
Adding course:
    - with incorrect input
Enrol user:
    - in course that doesn't exist
Adding questions:
    - mandatory multiple choice
    - mandatory text-based
    - optional multiple choice
    - optional text-based
    - with no text
    - with no options selected
Create survey:
    - without question
    - without course
    - with course that doesn't exist
Add user:
    - without ID
