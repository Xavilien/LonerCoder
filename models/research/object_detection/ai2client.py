from threading import Thread
import requests


HOST = 'localhost'
PORT = 8080

r = requests.get('http://localhost:8080')
print(r.json())
