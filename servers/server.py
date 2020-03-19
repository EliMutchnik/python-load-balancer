#!/usr/local/bin/python3

from flask import Flask, request
import socket, os

app = Flask(__name__)
username = os.environ["USERNAME"]

def get_my_ip():
    return socket.gethostbyname(socket.gethostname())

@app.route('/', methods=['GET'])
def health_check():
    return f"Hello World! (from: {get_my_ip()})"

@app.route('/login', methods=['GET'])
def login():
    return f"This is a Login page from: {get_my_ip()}"

@app.route('/register', methods=['POST'])
def register():
    if request.args["username"] == username:
        return f"Registration call back from: {get_my_ip()} CORRECT", 200
    elif request.args["username"] == None:
        return f"Registration call back from: {get_my_ip()} INVALID/MISSING DATA", 422
    else:
        return f"Registration call back from: {get_my_ip()} FAILED", 403

@app.route('/changePassword', methods=['POST'])
def change_password():
    if request.args["username"] == username:
        return f"Change Password call back from: {get_my_ip()} CORRECT", 200
    elif request.args["username"] == None:
        return f"Registration call back from: {get_my_ip()} INVALID/MISSING DATA", 422
    else:
        return f"Change Password call back from: {get_my_ip()} FAILED", 403

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
