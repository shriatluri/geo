import re
import requests
import json
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def extract_domain_from_md(filepath):
    """Extract the first domain URL from a .md intake file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"https?://[^\s`]+", content)
    return match.group(0) if match else None

def detect_platform(resp, soup):
    """Detect CMS/platform from HTML and headers."""
    text = resp.text.lower()

    # 1. Check meta generator tag
    generator = soup.find("meta", attrs={"name": "generator"})
    if generator:
        return generator.get("content")

    # 2. WordPress fingerprint
    if "wp-content" in text:
        return "WordPress"

    # 3. Shopify fingerprint
    if "shopify" in text or "cdn.shopify.com" in text:
        return "Shopify"

    # 4. Webflow fingerprint
    if "webflow" in text:
        return "Webflow"

    # 5. Squarespace fingerprint
    if "squarespace" in text or "static.squarespace.com" in text:
        return "Squarespace"
    if any("squarespace" in h.lower() for h in resp.headers):
        return "Squarespace"

    return None

def pre_health_check(domain_url):
    """Run a pre-health check on a given domain URL."""
    results = {
        "domain": domain_url,
        "ssl_valid": False,
        "response_time_ms": None,
        "mobile_friendly": False,
        "robots_txt_exists": False,
        "sitemap_urls": [],
        "platform_detected": None
    }

    try:
        # Response time & SSL
        resp = requests.get(domain_url, timeout=10)
        results["response_time_ms"] = int(resp.elapsed.total_seconds() * 1000)
        results["ssl_valid"] = domain_url.startswith("https")

        # Robots.txt check
        robots_url = urljoin(domain_url, "/robots.txt")
        robots_resp = requests.get(robots_url, timeout=5)
        results["robots_txt_exists"] = robots_resp.status_code == 200

        if results["robots_txt_exists"]:
            for line in robots_resp.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    results["sitemap_urls"].append(line.split(":", 1)[1].strip())

        if not results["sitemap_urls"]:
            sitemap_url = urljoin(domain_url, "/sitemap.xml")
            sitemap_resp = requests.get(sitemap_url, timeout=5)
            if sitemap_resp.status_code == 200:
                results["sitemap_urls"].append(sitemap_url)

        # Mobile-friendly check
        soup = BeautifulSoup(resp.text, "html.parser")
        viewport = soup.find("meta", attrs={"name": "viewport"})
        results["mobile_friendly"] = viewport is not None

        # CMS detection
        results["platform_detected"] = detect_platform(resp, soup)

    except Exception as e:
        results["error"] = str(e)

    return results

def save_results(results, outdir="../client docs/health_checks"):
    """Save health check results to a JSON file."""
    os.makedirs(outdir, exist_ok=True)  # creates folder if not exists
    domain_slug = results["domain"].replace("https://", "").replace("http://", "").replace("/", "_")
    filepath = os.path.join(outdir, f"{domain_slug}_health.json")
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved pre-health check results to {filepath}")

if __name__ == "__main__":
    filepath = "../client docs/context.md"  # path to your intake .md file
    domain = extract_domain_from_md(filepath)
    if domain:
        print(f"Running pre-health check for: {domain}\n")
        results = pre_health_check(domain)
        print(results)
        save_results(results)  # automatically saves to JSON
    else:
        print("No domain found in the .md file.")
