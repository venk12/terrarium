![alt text](https://i.ibb.co/Fn94zNS/2.png)
![alt text](https://i.ibb.co/9qYxHPF/3.png)

To clone the latest version from git repo:
>> git clone https://github.com/venk12/terra-monorepo.git

You can now open the entire terra-monorepo folder on vscode.
To push the changes to git repo you can either use the vscode source control or navigate to the project root directory:
>> git add .
>> git commit -m 'commit description'
>> git push origin main

UI:
To run locally/local development:
>> cd ui
>> npm start
# The app will launch in port 3000

Server:

If you are setting up server from scratch, follow these steps (only 1st time):
1. Download and install Anaconda. This should install python by default in your computer (check if python version 3+ is installed)
2. >> cd server
3. >> conda env create -f environment.yaml
4. >> conda activate avenv

To run locally/local development:
>> cd server
>> conda activate avenv 
>> pip install -r requirements.txt
>> python main.py
# The program will launch in port 3389



