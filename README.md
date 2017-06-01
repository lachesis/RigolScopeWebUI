Rigol Scope Web UI
------------------
A simple web-UI for the Rigol 1054Z/1104Z oscilloscope. Shows the scope screen, refreshing every 5 seconds, with a command input box.

Running
-------
Works in Python2 for now. Will eventually run in Py3 & Py2. Only dependency is Tornado right now. Proper setup.py & such coming soon.

    pip install tornado
    python server.py 8080
    
Then go to http://localhost:8080 and have fun!
