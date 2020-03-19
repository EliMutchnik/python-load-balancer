# Python Load Balancer
This project implements a load balancer which operates under these rules:
* GET requests are forwarded to a single server, selected in a round-robin fashion
* Each POST request is forwarded to N servers. The client should receive the first
successful response returned by one of the upstream servers.
* All POST requests should return a successful response (HTTP status code 201). If one
of the upstream servers fails to return such a response, keep retrying until
successful, using an exponential backoff interval.

## Intro
The load balancer image itself located under the load-balancer directory.
The "servers" image that should emulate the upstream server group located under the servers directory.
Currently, there is 3 servers in the upstream group.
To simulate the POST request requirement, an environment variable USERNAME was added with unique name for each server (passing one of the usernames to the load balancer will trigger response from the server that has this username as environment variable).

## Add servers
1. Add servers to load-balancer/app/servers.txt file:
```
http://server1:8000
http://server2:8000
http://server3:8000
.
.
.
http://server<N>:8000
```

2. Add servers to the docker-compose.yml file:
```
  server<N>:
    image: lb-app:latest
    container_name: server<N>
    environment:
      - USERNAME=<Unique Name>
```

Note: the server hostname in servers.txt and the service name in docker-compose.yml MUST BE THE SAME.

## Run the project
```
cd ./python-load-balancer
cd load-balancer && docker build -t lb-main:latest .
cd ../servers && docker build -t lb-app:latest .
cd ../
docker-compose up
```

## APIs
[GET] http://localhost:8000/

[GET] http://localhost:8000/login

[POST] http://localhost:8000/register?username=jack/tom/rob

[POST] http://localhost:8000/changePassword?username=jack/tom/rob

Note: The "username" parameter passed relies on the USERNAME environment variable you can find in docker-compose.yml.

## Metrics of load balancer machine
[GET] http://localhost:8000/metrics

## License
[MIT](https://choosealicense.com/licenses/mit/)
