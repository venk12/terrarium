#!/usr/bin/env python3

import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}\n{err.decode()}")
    else:
        print(f"Successfully executed: {command}\n{out.decode()}")

# Install mosquitto and mosquitto-clients
run_command("sudo apt-get install -y mosquitto mosquitto-clients")

# Enable mosquitto
run_command("sudo systemctl enable mosquitto")

# Install paho-mqtt Python package
run_command("pip install paho-mqtt")

# Install required packages from requirements.txt
run_command("pip3 install -r /server/requirements.txt")

# Add configurations to mosquitto.conf
mosquitto_conf = "/etc/mosquitto/mosquitto.conf"

# BIG SECURITY RISK HERE, ADDRESS WHEN DONE DEVELOPING!
conf_data = "listener 1883\nallow_anonymous true\n"

with open("temp_conf", "w") as temp_file:
    temp_file.write(conf_data)

run_command(f"sudo bash -c 'cat temp_conf >> {mosquitto_conf}'")
run_command("rm temp_conf")

print("Mosquitto setup complete.")
