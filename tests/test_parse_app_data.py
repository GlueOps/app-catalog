import unittest
import os
import glueops.setup_logging
import app.main as app 

logger = glueops.setup_logging.configure(level='ERROR')


class TestParseAppData(unittest.TestCase):
    
    def setUp(self):
        # Set up any environment variables required by parse_app_data
        os.environ['CAPTAIN_DOMAIN'] = 'captain.example.com'

    def test_parse_app_data(self):
        test_cases = [
            # Test case 1: Valid app data
            {
                "name": "Valid app data",
                "input": {
                    "metadata": {
                        "name": "test-app",
                        "namespace": "test-namespace"
                    },
                    "status": {
                        "health": {
                            "status": "Healthy"
                        },
                        "operationState": {
                            "finishedAt": "2023-09-01T12:00:00Z"
                        },
                        "summary": {
                            "externalURLs": ["http://example.com"],
                            "images": ["nginx:1.21@sha256:abcd1234"]
                        }
                    }
                },
                "expected": {
                    "app_name": "test-app",
                    "argocd_status": "Healthy",
                    "last_updated_at": "2023-09-01T12:00:00Z",
                    "app_link": "argocd.captain.example.com/applications/test-namespace/test-app",
                    "external_urls": ["http://example.com"],
                    "images": [{
                        "image": "nginx",
                        "tag": "1.21",
                        "sha": "abcd1234"
                    }]
                }
            },
            # Test case 2: Missing metadata
            {
                "name": "Missing metadata",
                "input": {
                    "status": {
                        "health": {
                            "status": "Healthy"
                        },
                        "operationState": {
                            "finishedAt": "2023-09-01T12:00:00Z"
                        }
                    }
                },
                "expected": None
            },
            # Test case 3: Missing status
            {
                "name": "Missing status",
                "input": {
                    "metadata": {
                        "name": "test-app",
                        "namespace": "test-namespace"
                    }
                },
                "expected": None
            },
            # Test case 4: No images or externalURLs
            {
                "name": "No images or externalURLs",
                "input": {
                    "metadata": {
                        "name": "test-app",
                        "namespace": "test-namespace"
                    },
                    "status": {
                        "health": {
                            "status": "Healthy"
                        },
                        "operationState": {
                            "finishedAt": "2023-09-01T12:00:00Z"
                        }
                    }
                },
                "expected": {
                    "app_name": "test-app",
                    "argocd_status": "Healthy",
                    "last_updated_at": "2023-09-01T12:00:00Z",
                    "app_link": "argocd.captain.example.com/applications/test-namespace/test-app"
                }
            }
        ]

        for case in test_cases:
            with self.subTest(case["name"]):
                result = app.parse_app_data(case["input"])
                self.assertEqual(result, case["expected"])

if __name__ == "__main__":
    unittest.main()
