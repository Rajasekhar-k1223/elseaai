#!/usr/bin/env python3
"""Simple end-to-end test script for ElseaAI backend.

Usage: set environment variable API_URL or edit the default below, then run:
    python scripts/e2e_test.py

This script will:
 - register a test user (if not present)
 - obtain a token
 - upload `scripts/sample_doc.txt`
 - list pending-review documents
 - request fine-tune dataset generation for the uploaded doc
 - print responses
"""
import os
import time
import requests

API_URL = os.environ.get("API_URL") or "http://localhost:8000"

TEST_EMAIL = "e2e_test_user@example.com"
TEST_PASSWORD = "TestPass123!"


def register_user():
    url = f"{API_URL}/api/v1/auth/register"
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "E2E Test User"
    }
    resp = requests.post(url, json=payload)
    if resp.status_code in (200, 201):
        print("[register] user created")
    else:
        print(f"[register] status: {resp.status_code}, detail: {resp.text}")


def get_token():
    url = f"{API_URL}/api/v1/auth/token"
    data = {"username": TEST_EMAIL, "password": TEST_PASSWORD}
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]


def upload_file(token: str, path: str):
    url = f"{API_URL}/api/v1/documents/upload"
    with open(path, "rb") as f:
        files = {"file": (os.path.basename(path), f)}
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(url, files=files, headers=headers)
    resp.raise_for_status()
    return resp.json()


def list_pending(token: str):
    url = f"{API_URL}/api/v1/documents/pending-review"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def generate_dataset(token: str, document_id: str):
    url = f"{API_URL}/api/v1/documents/{document_id}/generate-finetune"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, json={"include_sections": True}, headers=headers)
    resp.raise_for_status()
    return resp.json()


def main():
    print("Starting E2E test against", API_URL)
    register_user()
    token = get_token()
    print("Got token (truncated):", token[:24])

    sample = os.path.join(os.path.dirname(__file__), "sample_doc.txt")
    if not os.path.exists(sample):
        print("Sample document not found:", sample)
        return

    print("Uploading sample document...")
    upload_res = upload_file(token, sample)
    print("Upload response:", upload_res)

    # wait briefly for background processing queue to accept task
    time.sleep(2)

    pending = list_pending(token)
    print("Pending documents:", pending)

    # find our uploaded document
    doc_id = None
    for d in pending:
        if d.get("filename") == os.path.basename(sample):
            doc_id = d.get("document_id")
            break

    if not doc_id and pending:
        doc_id = pending[0].get("document_id")

    if not doc_id:
        print("Uploaded document not found in pending list. Exiting.")
        return

    print("Generating fine-tune dataset for:", doc_id)
    gen = generate_dataset(token, doc_id)
    print("Generate response:", gen)


if __name__ == "__main__":
    main()
