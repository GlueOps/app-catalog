from kubernetes import client, config
from kubernetes.client.rest import ApiException
from fastapi import FastAPI, Response
from fastapi import Request
from contextlib import contextmanager
import glueops.setup_logging
import re
import json
import uvicorn
import os

ARGOCD_API_GROUP = 'argoproj.io'
ARGOCD_API_VERSION = 'v1alpha1'
ARGOCD_PLURAL = 'applications'
PAGINATION_LIMIT = 100

# Initialize FastAPI app and logger
app = FastAPI()
logger = glueops.setup_logging.configure(level=os.environ.get('LOG_LEVEL', 'WARNING'))

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")

@contextmanager
def load_kube_config():
    """Loads Kubernetes configuration."""
    try:
        config.load_incluster_config()
        logger.info("Loaded in-cluster kubeconfig")
    except config.ConfigException:
        try:
            config.load_kube_config()
            logger.info("Loaded local kubeconfig")
        except Exception as e:
            logger.error(f"Error loading kubeconfig: {e}")
            raise

def fetch_argocd_apps():
    """Fetch all ArgoCD applications using pagination."""
    custom_api = client.CustomObjectsApi()
    continue_token = None
    all_apps = []

    try:
        while True:
            response = custom_api.list_cluster_custom_object(
                ARGOCD_API_GROUP, ARGOCD_API_VERSION, ARGOCD_PLURAL,
                limit=PAGINATION_LIMIT,  
                _continue=continue_token 
            )
            all_apps.extend(response.get('items', []))
            continue_token = response.get('metadata', {}).get('continue')
            if not continue_token:
                break
    except ApiException as e:
        logger.error(f"Error fetching ArgoCD applications: {e}")
        raise

    return all_apps

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
        else:
            logger.warning(f"Unexpected image format: {image}")
    return images

def parse_app_data(app):
    """Parses individual ArgoCD app data into a structured format."""
    required_keys = ["metadata", "status"]
    if not all(key in app for key in required_keys):
        logger.error(f"Missing required keys in app data: {app}")
        return None
    
    try:
        app_name = app["metadata"]["name"]
        namespace = app["metadata"]["namespace"]
        captain_domain = os.getenv("CAPTAIN_DOMAIN")
        res_app = {
            "app_name": app_name,
            "argocd_status": app["status"]["health"]["status"],
            "last_updated_at": app["status"]["operationState"]["finishedAt"],
            "app_link": f"argocd.{captain_domain}/applications/{namespace}/{app_name}",
        }
        if "externalURLs" in app["status"].get("summary", {}):
            res_app["external_urls"] = app["status"]["summary"]["externalURLs"]
            
        if "images" in app["status"].get("summary", {}):
            res_app["images"] = parse_images(app["status"]["summary"]["images"])
 
        return res_app
    except KeyError as e:
        logger.error(f"KeyError while parsing app data: {e}")
        return None

@app.get("/apps")
def get_apps():
    """API endpoint to fetch and return ArgoCD apps."""
    try:
        apps_data = fetch_argocd_apps()
        parsed_apps = [parse_app_data(app) for app in apps_data]
        response_data = {"apps": parsed_apps}
        return Response(content=json.dumps(response_data), media_type="application/json")
    except ApiException as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=500)

if __name__ == "__main__":
    load_kube_config()
    uvicorn.run(app, host="0.0.0.0")
    
