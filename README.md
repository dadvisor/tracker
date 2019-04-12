# tracker
A tracker server for discovering other peers. Those peers are used for the dAdvisor.

## How to run?
First install the requirements with:

	pip install -r requirements.txt

Then start with:

	python server.py

## Run using docker
Or use the following docker command:

	docker run --name tracker -d -p 6969:6969/udp dadvisor/tracker:latest
