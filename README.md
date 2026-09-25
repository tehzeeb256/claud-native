# cloud-native devops plateform 

Hi users!
Actually This is my hands-on first project to learn **Devops from bignner to advance**.

NOW 
I am building a real web application with **python fastAPI** and implementing every devops practice step-by-step or commit-by-commit. 

# what is this project?
At its start, this is a web api designed to behave like a modren cloud services.
The goal is not to just write the code, but to take this app through the **entire production life cycle**  
* packiging it with **docker**
* Automating tests and build with **Github action**
* orchestrating containers with **kubernetes**
* Managing infrastructure using **Terraform**
* Tracking live health and matrice with **Prometheus & Grafana**


# Tech stack
* **Backend:** python 3.12, fastAPI, uvicorn
* **Devops & Cloud:** Docker, github actions, Kubernetes, Teraform
* **Monitoring:** Prometheus, Grafana

# How to run locally 
If you want to run this in your computer or laptops 

# 1: Clone this repo
---bash 
git clone https://github.com/tehzeeb256/claud-native.git
cd claud-native


# setup packeges and environments 

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


# run the development server 
.venv/bin/python3 -m uvicorn app.main:app --reload

# check the endpoint of your browser 
Welcome page: http://127.0.0.1:8000
Kubernetes Health Probe: http://127.0.0.1:8000/healthz
Interactive API Docs: http://127.0.0.1:8000/docs


AUTHOR
. Tehzeeb -- learning in public and mastring in devops 