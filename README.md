# suricata-kafka.py
Python code that allows suricata to write to a unix socket and then stream it to a kafka broker  

## Installing

Clone the repository and move the service and socket files to the approperiate locations.  

`git clone https://github.com/spartan782/suricata-kafka.git`  

the location for the service and socket files are `/etc/systemd/system/`  

`cd suricata-kafka`  
`sudo mv suricata-kafka.service /etc/systemd/system`  
`sudo mv suricata-kafka.socket /etc/systemd/system`  

Then move the the python script to a suitable location.
`sudo mv suricata-kafka.py /etc/suricata/`  

We also need to change suricata to output to the socket created by systemd. Here is a snippet of the config file
`sudo vi /etc/suricata/suricata.yaml`  
```
...
  # Extensible Event Format (nicknamed EVE) event log in JSON format
  - eve-log:
      enabled: yes
      filetype: unix_stream  #unix_dgram #regular|syslog|unix_dgram|unix_stream|redis
      filename: /var/lib/suricata/eve.sock
      #prefix: "@cee: " # prefix to prepend to each log entry
...
```

After getting everything in place we need to start the services, and its off to the races  
`sudo systemctl start suricata-kafka`  
`sudo systemctl start suricata`  


