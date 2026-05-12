import os
import requests
import xml.etree.ElementTree as ET
from src.config.settings import settings

def parse_junit(path: str) -> list[dict]:
    tree = ET.parse(path)
    root = tree.getroot()
    results = []
    for testcase in root.findall(".//testcase"):
        status = "passed"
        if testcase.find("failure") is not None: status = "failed"
        if testcase.find("skipped") is not None: status = "skipped"
        results.append({"name": testcase.attrib["name"], "status": status})
    return results

def sync_to_tms(results: list[dict]):
    payload = {"test_results": results}
    headers = {"Authorization": f"Bearer {os.getenv('TMS_TOKEN')}", "Content-Type": "application/json"}
    resp = requests.post(f"{os.getenv('TMS_API_URL')}/api/v1/results", json=payload, headers=headers)
    resp.raise_for_status()
    print(f"TMS sync completed: {resp.status_code}")

if __name__ == "__main__":
    junit_path = "test-results.xml"
    if os.path.exists(junit_path):
        sync_to_tms(parse_junit(junit_path))