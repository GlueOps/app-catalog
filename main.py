from kubernetes import client, config
from kubernetes.client.rest import ApiException
from fastapi import FastAPI, Response
import re
import json
import uvicorn

app = FastAPI()

@app.get("/apps")
def get_apps():
    # Load kubeconfig from default location ~/.kube/config
    try:
        config.load_kube_config()
    except Exception as e:
        print(f"Error loading kubeconfig: {e}")
        return
    
    # Or load in-cluster config if running inside Kubernetes
    # config.load_incluster_config()

    # Create API client
    v1 = client.CoreV1Api()

    # List all the apps 
    
    # Initialize the CustomObjectsApi to interact with custom resources
    custom_api = client.CustomObjectsApi()

    # ArgoCD applications are usually in the 'argoproj.io' API group and 'v1alpha1' version
    group = 'argoproj.io'
    version = 'v1alpha1'
    plural = 'applications'

    try:
        # List all ArgoCD Application resources across all namespaces
        all_apps = dict()
        res_apps = []
        apps = custom_api.list_cluster_custom_object(group, version, plural)

        app_count = 0
        for app in apps.get('items', []):
            app_count = app_count + 1
            res_app = dict()
            res_app["app_name"] = app["metadata"]["name"]
            res_app["argocd_status"] = app["status"]["health"]["status"]
            res_app["last_updated_at"] = app["status"]["operationState"]["finishedAt"]
            
            if "externalURLs" in app["status"]["summary"]:
                res_app["external_urls"] = app["status"]["summary"]["externalURLs"] 
             
            if "images" in app["status"]["summary"]:    
                images = []
                for image in app["status"]["summary"]["images"]:
                    match = re.match(r"([^:]+):([^@]+)(?:@sha256:([a-f0-9]+))?", image)
                    image_dict = dict()
                    if match:
                        full_image_location = match.group(1)
                        tag = match.group(2)
                        sha = match.group(3)
                       
                        image_dict["image"] = full_image_location
                        image_dict["tag"] = tag
                        image_dict["sha"] = sha
                        
                        images.append(image_dict)
                        
                res_app["images"] = images
                    
            res_apps.append(res_app) 
            if(app_count == 5):
                break
        all_apps["apps"] = res_apps
        response = json.dumps(all_apps)
        return Response(content = response)
    except ApiException as e:
        print(f"Exception when calling CustomObjectsApi->list_cluster_custom_object: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
