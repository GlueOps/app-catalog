from kubernetes import client, config
from kubernetes.client.rest import ApiException
from fastapi import FastAPI, Response
import glueops.setup_logging
import re
import json
import uvicorn
import os

ARGOCD_API_GROUP = 'argoproj.io'
ARGOCD_API_VERSION = 'v1alpha1'
ARGOCD_PLURAL = 'applications'

# Initialize FastAPI app and logger
app = FastAPI()
logger = glueops.setup_logging.configure(level=os.environ.get('LOG_LEVEL', 'WARNING'))

def load_kube_config():
    """Loads Kubernetes configuration."""
    try:
        config.load_kube_config()
    except Exception as e:
        logger.error(f"Error loading kubeconfig: {e}")
        raise

def fetch_argocd_apps():
    """Fetches all ArgoCD applications using the Kubernetes API."""
    custom_api = client.CustomObjectsApi()
    try:
        return custom_api.list_cluster_custom_object(
            ARGOCD_API_GROUP, ARGOCD_API_VERSION, ARGOCD_PLURAL
        )
    except ApiException as e:
        logger.error(f"Error fetching ArgoCD applications: {e}")
        raise

def parse_images(image_list):
    """Parses image list and extracts image information."""
    images = []
    for image in image_list:
        match = re.match(r"([^:]+):([^@]+)(?:@sha256:([a-f0-9]+))?", image)
        if match:
            images.append({
                "image": match.group(1),
                "tag": match.group(2),
                "sha": match.group(3) if match.group(3) else "No SHA provided"
            })
    return images

def parse_app_data(app):
    """Parses individual ArgoCD app data into a structured format."""
    app_name = app["metadata"]["name"]
    namespace = app["metadata"]["namespace"]
    captain_domain = os.getenv("CAPTAIN_DOMAIN")
    res_app = {
        "app_name": app_name,
        "argocd_status": app["status"]["health"]["status"],
        "last_updated_at": app["status"]["operationState"]["finishedAt"],
        "app_link": "argocd.{captain_domain}/applications/{namespace}/{app_name}".format(captain_domain=captain_domain, namespace=namespace, app_name=app_name),
    }

    if "externalURLs" in app["status"]["summary"]:
        res_app["external_urls"] = app["status"]["summary"]["externalURLs"]

    if "images" in app["status"]["summary"]:
        res_app["images"] = parse_images(app["status"]["summary"]["images"])

    return res_app

@app.get("/apps")
def get_apps():
    """API endpoint to fetch and return ArgoCD apps."""
    load_kube_config()
    
    try:
        apps_data = fetch_argocd_apps()
        parsed_apps = [parse_app_data(app) for app in apps_data.get('items', [])]
        response_data = {"apps": parsed_apps}
        return Response(content=json.dumps(response_data), media_type="application/json")
    except ApiException as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
