#!/usr/local/bin/python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import requests, logging, psutil
from concurrent.futures import ThreadPoolExecutor, as_completed

SERVERS = open("/app/servers.txt").read().splitlines()
NUM_OF_SERVERS = len(SERVERS)
SERVER_INDEX = 1

DEFAULT_TIMEOUT = 1 # seconds
TIMEOUT_BACKOFF_RATE = 2
MAX_TIMEOUT = 60

# Handles a single post request
def do_single_post(server, path, data, timeout):
    try:
        logging.info(f"-> will send to: {server}")
        response = requests.post(
            url = f"{server}{path}",
            data=data,
            timeout=timeout
        )

        if response.status_code != 200:
            logging.info(f"-> server {server} failed with {response.status_code}: {response.text}")
            return None

        logging.info(f"-> server {server} did OK: {response.text}")
        return response.text
    
    except requests.exceptions.Timeout:
        logging.info(f"-> server {server} timed out ({timeout} seconds)")
        return None  

# Execute post requests for all servers and return the first response (valid/invalid)
def get_first_post_response(path, data, timeout):
    with ThreadPoolExecutor(max_workers=NUM_OF_SERVERS) as executer:
        futures = {
            executer.submit(do_single_post, server, path, data, timeout): server
            for server in SERVERS
        }

        valid_response = None
        valid_server = None

        for future in as_completed(futures):
            
            # The server that completed the task.
            finished_server = futures[future]
            future_result = future.result()
            
            if future_result:
                # Completed successfully! (result contains the POST response)
                valid_response = future_result
                valid_server = finished_server
                break

        return {
            "response": valid_response,
            "server": valid_server
        }

# Keep trying post requests until getting valid response
def handle_post_request(path, data):
    timeout = DEFAULT_TIMEOUT

    while timeout < MAX_TIMEOUT:
        task_result = get_first_post_response(path, data, timeout)

        if task_result["response"] != None:
            logging.info(f" -> got answer after {timeout} seconds, from {task_result['server']}")
            return task_result["response"]

        timeout *= TIMEOUT_BACKOFF_RATE
    return f"No valid response found under {MAX_TIMEOUT} sec timeout"

# GET requests implementing Round Robin technique
def get_req(url_path):
    global SERVER_INDEX

    if SERVER_INDEX > NUM_OF_SERVERS:
        SERVER_INDEX = 1

    req = requests.get(url = f"{SERVERS[SERVER_INDEX-1]}{url_path}")
    SERVER_INDEX += 1

    return req.text

# Return the basic metrics of the machine
def get_metrics():
    return "CPU: {}% | Memory: {}% | Disk: {}%".format(
        psutil.cpu_percent(interval=None), 
        psutil.virtual_memory().percent, 
        psutil.disk_usage('/').percent
    )

class LoadBalancer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            resp = get_metrics()
        else:
            resp = get_req(self.path)

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(resp.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        resp = handle_post_request(self.path, post_data)

        self.send_response(201)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(resp.encode())
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("The servers are: {}".format(SERVERS))
    httpd = HTTPServer(('', 8000), LoadBalancer)
    httpd.serve_forever()