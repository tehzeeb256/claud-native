import socket
import time
from fastapi import FastAPI, status
app = FastAPI(
    title="cloud-native platform",
    version="1.0.0",
    description="production ready cloud-native devops API"

)
START_TIME = time.time()

# welcome endpoint 1
@app.get("/", tags=["general"])
def read_root():
    return{
        "message": "welcome to cloud-native platform",
        "versiom": "1.0.0",
        "status":"opreational"
    }

# devops leveness (docker/kubernetes) 2
@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["devops probes"])
def liveness_probe():
    """
    kubernetes ko batay ga k app abhi tak zinda ha 
    agar ya fail ho jay to orchestrator container ko restart kar da ga .
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

# devops load balancer 3
@app.get("/readyz", status_code=status.HTTP_200_OK, tags=["devops probes"])
def readiness_probe():
    """
    hamay batay ga k user request la rha ha 
    """
    return {
        "status": "ready",

    }

#info endpoint 4 
@app.get("/api/v1/info",  tags=["devops probes"])
def system_info():
    uptime = round(time.time() - START_TIME, 2)
    return {
        "hostname": socket.gethostname(),
        "app_name": "cloud-native platform",
        "uptime_seconds": uptime
    }