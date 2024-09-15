# app-catalog

This project provides a FastAPI-based service to fetch ArgoCD application data using Kubernetes API and ArgoCD's Custom Resource Definitions (CRDs).

## Installation and Setup

```
git clone https://github.com/GlueOps/app-catalog

cd app-catalog

pip install -r requirements.txt

python3 app/main.py
```


| Environment Variable | Description                                        | Example Value             |
|----------------------|----------------------------------------------------|---------------------------|
| `CAPTAIN_DOMAIN`     | The domain for generating ArgoCD app URLs          | `captain.example.com`     |
| `LOG_LEVEL`          | (Optional) The logging level for the application   | `INFO`, `DEBUG`, `WARNING`|
