add the enviroment variables to .env file

install and setup docker

`
docker-compose up -d
`

then run the following command to see the logs

`
docker logs slack-bot-backend --follow
`

To create the database 

`
docker-compose exec db createdb -U root slack-bot-test
`

To Run the Tests
`
docker-compose exec backend pytest -p no:warnings -s

MINOR CHANGE
