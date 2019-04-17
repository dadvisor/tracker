# tracker
A tracker server for discovering other peers. Those peers are used for the dAdvisor.

## How to run?
First install the requirements with:

	pip install -r requirements.txt

Then start with:

	python main.py

## Run using docker
Or use the following docker command:

	docker run --name tracker -d -p 8080:8080 dadvisor/tracker:latest
