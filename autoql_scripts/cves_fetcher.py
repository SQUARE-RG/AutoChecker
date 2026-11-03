#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import NVD_CACHE, CVES_PATH, get_chroma_client 
def get_cve_directories(base_path: str) -> List[str]:
    cve_dirs = []
    for item in os.listdir(base_path):
        if item.startswith("CVE-") and os.path.isdir(os.path.join(base_path, item)):
            cve_dirs.append(item)
    return sorted(cve_dirs)

def fetch_cve_from_nvd(cve_id: str, api_key: Optional[str] = None) -> Optional[Dict]:
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    headers = {}

    # Add API key if provided (helps with rate limiting)
    if api_key:
        headers['apiKey'] = api_key

    params = {'cveId': cve_id}

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get('vulnerabilities') and len(data['vulnerabilities']) > 0:
            return data['vulnerabilities'][0]['cve']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {cve_id}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {cve_id}: {e}")
        return None

def parse_cvss_metrics(metrics: Dict) -> Dict:
    result = {
        "cvss_v31_score": "",
        "cvss_v31_severity": "",
        "cvss_v31_vector": "",
        "cvss_v2_score": "",
        "cvss_v2_severity": "",
        "cvss_v2_vector": "",
    }

    if not metrics:
        return result

    if 'cvssMetricV31' in metrics and metrics['cvssMetricV31']:
        v31 = metrics['cvssMetricV31'][0]
        if 'cvssData' in v31:
            cvss_data = v31['cvssData']
            result['cvss_v31_score'] = str(cvss_data.get('baseScore', ''))
            result['cvss_v31_severity'] = cvss_data.get('baseSeverity', '')
            result['cvss_v31_vector'] = cvss_data.get('vectorString', '')

    if 'cvssMetricV2' in metrics and metrics['cvssMetricV2']:
        v2 = metrics['cvssMetricV2'][0]
        if 'cvssData' in v2:
            cvss_data = v2['cvssData']
            result['cvss_v2_score'] = str(cvss_data.get('baseScore', ''))
            result['cvss_v2_severity'] = v2.get('baseSeverity', '')
            result['cvss_v2_vector'] = cvss_data.get('vectorString', '')

    return result

def parse_cwe_data(weaknesses: List) -> Dict:
    cwe_ids = []
    cwe_descriptions = []

    if weaknesses:
        for weakness in weaknesses:
            if 'description' in weakness:
                for desc in weakness['description']:
                    if desc.get('lang') == 'en':
                        cwe_id = desc.get('value', '')
                        if cwe_id.startswith('CWE-'):
                            cwe_ids.append(cwe_id)
                            cwe_descriptions.append(cwe_id)

    return {
        "cwe_ids": ", ".join(cwe_ids),
        "cwe_descriptions": ", ".join(cwe_descriptions)
    }

def parse_references(references: List) -> str:
    ref_list = []
    if references:
        for ref in references:
            url = ref.get('url', '')
            if url:
                ref_list.append({
                    'url': url,
                    'source': ref.get('source', ''),
                    'tags': ref.get('tags', [])
                })
    return json.dumps(ref_list)

def parse_affected_software(configurations: List) -> str:
    affected = []
    if configurations:
        for config in configurations:
            if 'nodes' in config:
                for node in config['nodes']:
                    if 'cpeMatch' in node:
                        for cpe in node['cpeMatch']:
                            if cpe.get('vulnerable'):
                                affected.append({
                                    'cpe': cpe.get('criteria', ''),
                                    'versionEndExcluding': cpe.get('versionEndExcluding', ''),
                                    'versionEndIncluding': cpe.get('versionEndIncluding', ''),
                                    'versionStartExcluding': cpe.get('versionStartExcluding', ''),
                                    'versionStartIncluding': cpe.get('versionStartIncluding', '')
                                })
    return json.dumps(affected)

def create_cve_metadata(cve_id: str, cve_data: Optional[Dict] = None) -> Dict:
    base_metadata = {
        "cve_id": cve_id,
        "nist_url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
        "fetched_at": str(time.time())
    }

    if not cve_data:
        base_metadata.update({
            "description": f"CVE {cve_id} - Data not available",
            "published_date": "",
            "modified_date": "",
            "cvss_v31_score": "",
            "cvss_v31_severity": "",
            "cvss_v31_vector": "",
            "cvss_v2_score": "",
            "cvss_v2_severity": "",
            "cvss_v2_vector": "",
            "cwe_ids": "",
            "cwe_descriptions": "",
            "references_json": "[]",
            "affected_software_json": "[]",
        })
        return base_metadata

    description = ""
    if 'descriptions' in cve_data:
        for desc in cve_data['descriptions']:
            if desc.get('lang') == 'en':
                description = desc.get('value', '')
                break

    published_date = ""
    modified_date = ""
    if 'published' in cve_data:
        published_date = cve_data['published']
    if 'lastModified' in cve_data:
        modified_date = cve_data['lastModified']

    metrics = cve_data.get('metrics', {})
    cvss_data = parse_cvss_metrics(metrics)

    weaknesses = cve_data.get('weaknesses', [])
    cwe_data = parse_cwe_data(weaknesses)

    references = cve_data.get('references', [])
    references_json = parse_references(references)

    configurations = cve_data.get('configurations', [])
    affected_json = parse_affected_software(configurations)

    base_metadata.update({
        "description": description,
        "published_date": published_date,
        "modified_date": modified_date,
        **cvss_data,
        **cwe_data,
        "references_json": references_json,
        "affected_software_json": affected_json,
    })

    return base_metadata

def fetch_descriptions_to_json(descriptions_file: str, api_key: Optional[str] = None,
                               rate_limit_delay: float = 0.6, test_limit: Optional[int] = None) -> None:
    """
    Fetch CVE descriptions from NVD and append them to a JSON file.

    The JSON file maps CVE IDs to their English description strings, suitable
    for populating task.cve_description in no-tools ablation mode.

    Args:
        descriptions_file: Path to JSON file to write/append descriptions to
        api_key: Optional NVD API key (helps with rate limiting)
        rate_limit_delay: Delay in seconds between NVD API requests
        test_limit: If set, only process the first N CVE directories
    """
    # Load existing descriptions so we only fetch new ones
    existing: Dict[str, str] = {}
    if os.path.exists(descriptions_file):
        with open(descriptions_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        print(f"Loaded {len(existing)} existing descriptions from {descriptions_file}")

    cve_dirs = get_cve_directories(CVES_PATH)
    if test_limit:
        cve_dirs = cve_dirs[:test_limit]
        print(f"TEST MODE: Limited to first {test_limit} CVEs")
    print(f"Found {len(cve_dirs)} CVE directories")

    if not api_key:
        rate_limit_delay = max(rate_limit_delay, 12.5)
        print("No API key provided - rate limit: 5 requests per 60 seconds window")
    else:
        print("Using API key - rate limit: 30 requests per 60 seconds window")

    new_count = 0
    failed_cves = []

    for i, cve_id in enumerate(cve_dirs):
        if cve_id in existing:
            print(f"  {cve_id}: already cached, skipping")
            continue

        print(f"Fetching {cve_id}...", end=" ")
        cve_data = fetch_cve_from_nvd(cve_id, api_key)
        metadata = create_cve_metadata(cve_id, cve_data)
        description = metadata.get('description', '')

        if cve_data and description and description != f"CVE {cve_id} - Data not available":
            print("✓")
            existing[cve_id] = description
            new_count += 1
        else:
            print("✗")
            failed_cves.append(cve_id)

        if i < len(cve_dirs) - 1:
            time.sleep(rate_limit_delay)

    os.makedirs(os.path.dirname(os.path.abspath(descriptions_file)), exist_ok=True)
    with open(descriptions_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2)

    print("\n" + "=" * 60)
    print(f"Descriptions complete!")
    print(f"New descriptions fetched: {new_count}")
    print(f"Failed to fetch: {len(failed_cves)}")
    print(f"Total in file: {len(existing)}")
    print(f"Saved to: {descriptions_file}")
    if failed_cves:
        print(f"\nFailed CVEs:")
        for cve in failed_cves[:10]:
            print(f"  - {cve}")
        if len(failed_cves) > 10:
            print(f"  ... and {len(failed_cves) - 10} more")


def populate_chroma_collection(api_key: Optional[str] = None, batch_size: int = 50,
                               rate_limit_delay: float = 0.6, test_limit: Optional[int] = None): 

    client = get_chroma_client() 

    try:
        collection = client.get_collection(NVD_CACHE)
        print(f"Using existing collection {NVD_CACHE}")
        existing_ids = collection.get()['ids']
        if existing_ids:
            print(f"Clearing {len(existing_ids)} existing entries...")
            collection.delete(ids=existing_ids)
    except:
        collection = client.create_collection(NVD_CACHE)
        print(f"Created new collection {NVD_CACHE}")

    # Base path for CVE directories
    base_path = CVES_PATH 

    # Get all CVE directories
    cve_dirs = get_cve_directories(base_path)

    # Apply test limit if specified
    if test_limit:
        cve_dirs = cve_dirs[:test_limit]
        print(f"TEST MODE: Limited to first {test_limit} CVEs")
    print(f"Found {len(cve_dirs)} CVE directories")

    # API rate limiting info
    if api_key:
        print("Using API key - rate limit: 30 requests per 60 seconds window")
    else:
        print("No API key provided - rate limit: 5 requests per 60 seconds window")
        rate_limit_delay = max(rate_limit_delay, 12.5)  # Ensure at least 12.5s delay without key

    # Process CVEs in batches
    total_processed = 0
    total_fetched = 0
    failed_cves = []

    for i in range(0, len(cve_dirs), batch_size):
        batch_cves = cve_dirs[i:i + batch_size]
        batch_ids = []
        batch_documents = []
        batch_metadatas = []

        print(f"\nProcessing batch {i//batch_size + 1}/{(len(cve_dirs) + batch_size - 1)//batch_size}")

        for cve_id in batch_cves:
            print(f"Fetching {cve_id}...", end=" ")

            # Fetch CVE data from NVD
            cve_data = fetch_cve_from_nvd(cve_id, api_key)

            if cve_data:
                print("✓")
                total_fetched += 1
                # Create enriched metadata from fetched data
                metadata = create_cve_metadata(cve_id, cve_data)
                # Use description as document text, fallback to CVE ID
                document_text = metadata.get('description', cve_id)
                if not document_text or document_text == f"CVE {cve_id} - Data not available":
                    document_text = cve_id
            else:
                failed_cves.append(cve_id)
                # Create minimal metadata if fetch failed
                metadata = create_cve_metadata(cve_id, None)
                document_text = cve_id

            batch_ids.append(cve_id)
            batch_documents.append(document_text)
            batch_metadatas.append(metadata)

            # Rate limiting between requests
            if cve_id != batch_cves[-1]:  # Don't delay after last item in batch
                time.sleep(rate_limit_delay)

        # Add batch to collection
        if batch_ids:
            print(f"Adding {len(batch_ids)} CVEs to Chroma collection...")
            collection.add(
                ids=batch_ids,
                documents=batch_documents,
                metadatas=batch_metadatas
            )
            total_processed += len(batch_ids)
            print(f"Batch complete. Total processed: {total_processed}/{len(cve_dirs)}")

    # Final summary
    print("\n" + "="*60)
    print(f"Population complete!")
    print(f"Total CVEs processed: {total_processed}")
    print(f"Successfully fetched from NVD: {total_fetched}")
    print(f"Failed to fetch: {len(failed_cves)}")

    if failed_cves:
        print(f"\nFailed CVEs (stored with minimal metadata):")
        for cve in failed_cves[:10]:  # Show first 10 failures
            print(f"  - {cve}")
        if len(failed_cves) > 10:
            print(f"  ... and {len(failed_cves) - 10} more")

    # Verify final collection count
    count = collection.count()
    print(f"\nCollection now contains {count} documents")

    return collection

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Populate Chroma database with CVE data from NVD')
    parser.add_argument('--api-key', type=str, help='NVD API key (optional, helps with rate limiting)')
    parser.add_argument('--batch-size', type=int, default=50, help='Number of CVEs per batch (default: 50)')
    parser.add_argument('--test', action='store_true', help='Test with only first 3 CVEs')
    parser.add_argument('--delay', type=float, default=0.6,
                       help='Delay between API requests in seconds (default: 0.6 for API key, 12.5 without)')
    parser.add_argument('--descriptions-file', type=str, default=None,
                       help='Fetch CVE descriptions and save to this JSON file (for no-tools ablation mode). '
                            'Skips Chroma population. Appends to existing entries.')

    args = parser.parse_args()

    if args.descriptions_file:
        fetch_descriptions_to_json(
            descriptions_file=args.descriptions_file,
            api_key=args.api_key,
            rate_limit_delay=args.delay,
            test_limit=3 if args.test else None,
        )
        sys.exit(0)

    collection = populate_chroma_collection(
        api_key=args.api_key,
        batch_size=args.batch_size if not args.test else 3,
        rate_limit_delay=args.delay,
        test_limit=3 if args.test else None
    )

    # Test query to verify data
    print("\n--- Testing query for stored CVEs ---")
    result = collection.get(limit=3)

    if result['ids']:
        for i in range(min(3, len(result['ids']))):
            print(f"\n{'='*60}")
            print(f"CVE ID: {result['ids'][i]}")
            metadata = result['metadatas'][i]
            print(f"Description: {metadata.get('description', 'N/A')[:200]}...")
            print(f"Published: {metadata.get('published_date', 'N/A')}")
            print(f"CVSS v3.1: {metadata.get('cvss_v31_score', 'N/A')} ({metadata.get('cvss_v31_severity', 'N/A')})")
            print(f"NVD URL: {metadata.get('nist_url', 'N/A')}")

            # Show CWEs if present
            cwe_ids = metadata.get('cwe_ids', '')
            if cwe_ids:
                print(f"CWEs: {cwe_ids}")

            # Show reference count
            refs = metadata.get('references_json', '[]')
            try:
                ref_count = len(json.loads(refs))
                print(f"References: {ref_count} links")
            except:
                pass

        # Test search functionality
        print(f"\n{'='*60}")
        print("Testing search functionality...")
        search_results = collection.query(
            query_texts=["remote code execution vulnerability"],
            n_results=3
        )

        if search_results['ids'] and search_results['ids'][0]:
            print(f"Found {len(search_results['ids'][0])} results for 'remote code execution vulnerability'")
            for idx, cve_id in enumerate(search_results['ids'][0]):
                print(f"  {idx+1}. {cve_id} (distance: {search_results['distances'][0][idx]:.4f})")
    else:
        print("No documents found in collection")