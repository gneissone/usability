#!flask/bin/python
from app import app
from app.routes import init_db
init_db()
app.run(debug=True)
