# orsi-video-platform

## Commands:
Step 9: Update the Frontend (If Needed)
Rebuild the Docker image if you make changes:
```docker build -t orsi-frontend .```
Re-import it into k3s:
```docker save orsi-frontend | sudo k3s ctr images import -```
Restart the Kubernetes deployment:
```kubectl rollout restart deployment frontend-deployment```


hostname -I