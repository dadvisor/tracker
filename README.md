# tracker
A tracker server for discovering other peers. Those peers are used for the dAdvisor.

## How to run?
First install the requirements with:

	pip install -r requirements.txt

Then start with:

	python main.py

## Run using docker
Or use the following docker command:

	docker run --name tracker -d -p 14100:14100 dadvisor/tracker:latest


## Endpoints
This tracker contains the following endpoints. Note that `{hash}` can be replaced with any string.
Additionally, `{peer}` is structured as `ip:port`:

- `/dashboard/{hash}`: for redirecting to the dashboard.
- `/add/{hash}/{peer}`: for adding a peer.
- `/remove/{hash}/{peer}`: for removing a peer.
- `/peers/{hash}`: for retrieving a list of peers.
- `/node_info/{hash}/{peer}`: for info about a node in the tree.