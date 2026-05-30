#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

from config import REPOS, DAYS_LOOKBACK, GITLAB_BASE_URL

load_dotenv()


def fetch_merged_mrs(token, project_id, since_date):
    headers = {"PRIVATE-TOKEN": token}
    url = f"{GITLAB_BASE_URL}/api/v4/projects/{project_id}/merge_requests"
    params = {
        "state": "merged",
        "updated_after": since_date.isoformat(),
        "per_page": 100,
        "order_by": "updated_at",
        "sort": "desc",
    }

    mrs = []
    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        page = resp.json()
        for mr in page:
            merged_at = mr.get("merged_at")
            if not merged_at:
                continue
            merged_dt = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
            if merged_dt < since_date:
                continue
            mrs.append({
                "title": mr.get("title", ""),
                "description": (mr.get("description") or "")[:400],
                "source_branch": mr.get("source_branch", ""),
                "merged_at": merged_at,
                "url": mr.get("web_url", ""),
            })
        next_page = resp.links.get("next", {}).get("url")
        url = next_page
        params = {}

    return mrs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", help="Fecha ISO desde la que buscar (YYYY-MM-DD)")
    args = parser.parse_args()

    token = os.environ.get("GITLAB_TOKEN")
    if not token:
        print("ERROR: GITLAB_TOKEN no está configurado en .env", file=sys.stderr)
        sys.exit(1)

    if args.since:
        since_date = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
    else:
        since_date = datetime.now(timezone.utc) - timedelta(days=DAYS_LOOKBACK)

    result = []
    for repo in REPOS:
        try:
            mrs = fetch_merged_mrs(token, repo["id"], since_date)
            for mr in mrs:
                mr["repo"] = repo["name"]
            result.extend(mrs)
        except requests.HTTPError as e:
            print(f"WARNING: Error al obtener MRs de {repo['name']}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"WARNING: Error inesperado en {repo['name']}: {e}", file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
