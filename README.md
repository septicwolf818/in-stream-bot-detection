# In-Stream Processing
## Project description
Bot detection algorithm: more than 20 requests per 10 seconds for single IP. IP should be whitelisted in 10 minutes if bot detection condition is not matched. It means IP should be deleted from Redis once host stops suspicious activity. System should handle up to 200 000 events per minute and collect user click rate and transitions for the last 10 minutes.
## Project prerequisites
To run the project, you need to install [Python 3](https://www.python.org/), [Scala 2.12](https://www.scala-lang.org/), [SBT](https://www.scala-sbt.org/), [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
## How to run the project
First enter into project files directory.
```sh
cd stream_project
```
Start Docker containers and wait until all of the containers are up and running.
After all containers are started you can run bot detector on them.
### Starting Docker containers
To start Docker containers use
```sh
./init.sh
``` 
### Starting services
To start services on Docker containers use
```sh
./start_structured.sh
```
or
```sh
./start_dstream.sh
```
## Testing

Create and activate virtual environment
```sh
virtualenv your_environment_name
source your_environment_name/bin/activate
```
Install requirements using `pip3`
```sh
pip3 install -r tests/requirements.txt
```
### Testing event generator
```
python3 -m unittest -v stream_project/generatortest.py
```
### Testing project
Enter into `tests` directory
```sh
cd tests
```
Make sure Docker Engine is up and running and then start tests
```sh
pytest -v test_structured.py test_dstream.py
```
## Check results
After you have started Docker containers and services you should be able to see detected bot in Redis.
Connect to Redis container and run `redis-cli`
```sh
docker exec -it redis redis-cli
```
and then list keys for bots
```
keys bots:*
```
There should be one detected bot

```
1) "bots:172.8.0.1"
```
