# tracker
A tracker server for discovering other peers. Those peers are used for the dAdvisor.

## How to run?
First install the requirements with:

	pip install -r requirements.txt

Then start with:

	python main.py

## Endpoints
This tracker contains the following endpoints. Note that `{hash}` can be replaced with any string.

- `/add/{hash}`: POST-request for adding a peer.
- `/remove/{hash}`: POST-request for removing a peer.
- `/distribution/{hash}`: GET-request for retrieving a list of peers.

## Testing
run the following file for testing purposes
`python -m unittest tracker.TestService`