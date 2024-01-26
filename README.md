# DataCommsTeamAssignment2

## Description
> This application simulates a weather condition and motion collision detection program where the user is provided with UI components viewing the difference data (stored in a broker) fetched from 2 microservices updated every couple of seconds

## Contributors
> Adriano D'Alonzo 2035770

> Yu Hua Yang 2133677

## Instructions to setup publish/subscribe paradigm:

1. Clone the repo on your computer
2. run `pip install -r requirements.txt` to install requirements for app
3. `cd broker`
4. `sudo vim mosquitto/config/mosquitto.conf` and uncomment `allow_anonymous true` and comment `allow_anonymous false` and `password_file mosquitto/config/mosquitto.conf`
5. Save changes
6. Kill container if its running (`sudo docker kill mosquitto_broker`) and remove it (`sudo docker rm mosquitto_broker`)
7. Run the container `sudo docker compose up -d` and enter the container with `sudo docker exec -it mosquitto_broker sh`. **NOTE** if the terminal tells you that the port 1883 is already in use, run `sudo netstat -tulpn | grep LISTEN`, find the process using the port and `sudo kill <id>`.
8. Once inside execute `mosquitto_passwd -c /mosquitto/config/passwd user1` and when prompted for password, enter `pass1`. Repeat same step for `user2` using the password `pass2` and `user3` with password `pass3` (**WITHOUT THE -c OPTION**)
9. Run `exit`
10. `sudo vim mosquitto/config/mosquitto.conf` and comment `allow_anonymous true` and uncomment `allow_anonymous false` and `password_file mosquitto/config/mosquitto.conf`
11. Save changes
12. If `private_key.pem` and `public_key.pem` files are not located in the `keys` directory, proceed to step **13**. Otherwise go to step **14**.
13. Go to root of repository and `cd ./keys` and run `python asymetric_keys.py` to generate public/private pair keys.
14. Proceed to next steps to run the dashboard.

## Instructions to run Dashboard:

1. `cd web_api` and run `sudo docker compose up -d` to start the microservices in respective containers (if they're not running already).
2. From `/web_api`, `cd ../` and run `python subscriber_dashboard.py` to subscribe to the broker.
3. From another terminal, head to the root of the repository and run `python publisher.py` to run the publisher and publish the topics to the broker
4. In the terminal running the subscriber/dashboard, once it says `Public Key Recieved. You may access at http://0.0.0.0:8050/`, you may access app at `localhost:8050`, `0.0.0.0:8050` or `<RPi IP>:8050` (**NOTE: A few seconds may be needed for the view to work properly. Wait ~ 5 seconds before viewing**)
5. Enjoy the view!

## Disclaimer
> There is an ongoing bug (occuring on occasion/chance) where no data retrieved gets displayed and just shows the filler text. To resolve this, restarting the publisher and subscriber scripts are required.
