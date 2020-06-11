# mad_dash
A suite for displaying and managing histograms stored at Madison's Data Warehouse

There are three independent applications that read/write to a common MongoDB database server: a database interface REST server, a web application, and a client script for production.


## Database REST Server
A REST server that interfaces a local MongoDB server

### Getting Started
    python3 -m virtualenv -p python3 mad_dash_db_server
    pip install -r db_server/requirements.txt
 
#### *Optional:* First Kill All Active MongoDBs Daemons
`sudo killall mongod`
  
#### Launch Local MongoDB Server via Docker
    ./db_server/resources/mongo_test_server.sh

#### Launch Local Token Service via Docker
    ./db_server/resources/token_test_server.sh
    
### Running the Server   
    python -m db_server


## Production Client
A script to add histograms and file-lists to the MongoDB DMBS

### Getting Started
1. Get I3 histogram pickle file(s)
1. Have an http connection (not required for debugging)

### POSTing and Updating from Pickle Files
#### Ingesting from a single file...
    python3 production_client/depickler.py FILEPATH
#### Ingesting from multiple files...
    python3 production_client/depickler.py FILEPATH1 FILEPATH2 ...
#### Ingesting recursively from directories...
    python3 production_client/depickler.py -r DIRPATH1 ...
#### More Options
    python3 production_client/depickler.py -h


## Web App
A dashboard for viewing and comparing histograms

### Getting Started
    python3 -m virtualenv -p python3 mad_dash_web_app
    pip install -r web_app/requirements.txt

### Running the Server
    python -m web_app
    
### Viewing Webpage
Go to http://localhost:8050/


## Testing

### Manual Testing
1. Set up and start servers (see above)
1. `pytest`

### Automated Testing
_TBD_
