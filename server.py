#!/usr/bin/env python3
import http.server, socketserver, os, webbrowser, threading, time

PORT = 8080
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def open_browser():
    time.sleep(0.5)
    webbrowser.open(f'http://127.0.0.1:{PORT}/visualizer.html')

threading.Thread(target=open_browser, daemon=True).start()

with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
    print(f'Visualizer → http://127.0.0.1:{PORT}/visualizer.html')
    print('Press Ctrl+C to stop.')
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
