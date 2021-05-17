## Droplet Directions

 These directions are for setting up escalation on a [DigitalOcean](https://www.digitalocean.com/) droplet.

- Log in to your droplet (e.g. via ssh)

- clone the escalation repository.
  - `git clone https://github.com/twosixlabs/Escalation.git`

- Install docker 
  - Follow https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository (if using ubuntu)
  - Afterwards, I recommend https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user 
   so you do not have to run sudo before docker commands


- Install docker-compose 
  - https://docs.docker.com/compose/install/#install-compose (Linux directions)

- Move into the root directory (e.g. `cd Escalation`)
- Run `docker-compose build`

- Run `./escalation/scripts/wizard_launcher.sh`
- With a browser (on any computer) go to <span>http://</span><your public ip address/domain name>:8000/

- Build your app ([creating your first config files with the UI wizard](documentation/wizard_guide/creating_first_graphic_with_wizard.md))
- stop running debugger (ctrl-c in terminal where debugger is running)

- run `docker-compose up --build -d`

- The app will be running at <span>http://</span><your public ip address/domain name>:8000/ 

- At this point you can log out of the ssh session and the app will continue to run

- If you would like to stop the app, run `docker-compose down` in the ssh terminal to your droplet
# Pointing a domain to Escalation (Nginx)
One method to point a domain or subdomain to a port:
- Follow  [the directions for setting up a server block](https://www.digitalocean.com/community/tutorials/how-to-set-up-nginx-server-blocks-virtual-hosts-on-ubuntu-16-04)
- In the directions, replace the file /etc/nginx/sites-available/example.com with


```
server {
        listen 80;
        listen [::]:80;
                
        server_name your_domain.com;

        location / {
                proxy_pass http://127.0.0.1:8000;
        }
}
```


todo: set Flask SECRET_KEY on server, not in code, set postgres db password, set password for admin actions