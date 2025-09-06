import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def pre_health_check(domain_url):
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

        # Sitemap discovery (from robots.txt or common locations)
        if results["robots_txt_exists"]:
            for line in robots_resp.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    results["sitemap_urls"].append(line.split(":", 1)[1].strip())
        if not results["sitemap_urls"]:
            # fallback check
            sitemap_url = urljoin(domain_url, "/sitemap.xml")
            sitemap_resp = requests.get(sitemap_url, timeout=5)
            if sitemap_resp.status_code == 200:
                results["sitemap_urls"].append(sitemap_url)

        # Basic mobile-friendly check (viewport tag)
        soup = BeautifulSoup(resp.text, "html.parser")
        viewport = soup.find("meta", attrs={"name": "viewport"})
        results["mobile_friendly"] = viewport is not None

        # Simple CMS detection
        generator = soup.find("meta", attrs={"name": "generator"})
        if generator:
            results["platform_detected"] = generator.get("content")
        elif "wp-content" in resp.text:
            results["platform_detected"] = "WordPress"
        elif "shopify" in resp.text.lower():
            results["platform_detected"] = "Shopify"
        elif "webflow" in resp.text.lower():
            results["platform_detected"] = "Webflow"

    except Exception as e:
        results["error"] = str(e)

    return results


# Example usage
if __name__ == "__main__":
    url = "https://purduethink.com"
    print(pre_health_check(url))
