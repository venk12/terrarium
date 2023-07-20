To pull the latest version from git repo:
git clone https://github.com/venk12/terra-monorepo.git

To push the changes to git repo:
>> git add .
>> git commit -m 'commit description'
>> git push origin main

UI
To run locally/local development:
>> cd ui
>> npm start
# The app will launch in port 3000

Server:

If you are setting up server from scratch, follow these steps (only 1st time):
1. Download and install Anaconda. This should install python by default in your computer
2. >> cd server
3. >> conda env create -f environment.yaml
4. >> conda activate avenv

To run locally/local development:
>> cd server
>> conda activate avenv 
>> pip install -r requirements.txt




