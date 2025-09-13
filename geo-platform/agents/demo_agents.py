#!/usr/bin/env python3
"""
Demonstration script for GEO Agents using PurdueTHINK crawler data.

This script demonstrates how the AEO, GEO, and GEO+ agents work with
real crawler output from the PurdueTHINK consulting website.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.shared.crawler_adapter import CrawlerDataAdapter
from src.shared.models import WebsiteData
from src.shared.llm_client import LLMClient
from src.aeo_agent.agent import AEOAgent
from src.geo_agent.agent import GEOAgent
from src.geo_plus_agent.agent import GEOPlusAgent


async def demo_purdue_think_analysis():
    """Demonstrate agent analysis using PurdueTHINK crawler data."""
    
    print("🚀 GEO Agents Demo - PurdueTHINK Analysis")
    print("=" * 50)
    
    # Initialize LLM client (mock for demo)
    llm_client = LLMClient()
    
    # Initialize agents
    aeo_agent = AEOAgent(llm_client)
    geo_agent = GEOAgent(llm_client)
    geo_plus_agent = GEOPlusAgent(llm_client)
    
    print("\n📊 Initializing agents:")
    print(f"✅ {aeo_agent.name} (Visibility Optimization)")
    print(f"✅ {geo_agent.name} (Data Accuracy)")
    print(f"✅ {geo_plus_agent.name} (Actionability)")
    
    # Load crawler data for PurdueTHINK
    try:
        adapter = CrawlerDataAdapter.from_client_docs("purduethink.com")
        website_data = adapter.convert_to_website_data(
            "https://purduethink.com",
            # Mock HTML content based on what we know about the site
            """
            <html>
            <head>
                <title>PurdueTHINK Consulting - Student Consulting at Purdue</title>
                <meta name="description" content="Student-run consulting organization at Purdue University helping companies with strategic projects.">
            </head>
            <body>
                <header>
                    <h1>PurdueTHINK Consulting</h1>
                    <nav>
                        <a href="/apply">Apply</a>
                        <a href="/projects">Projects</a>
                        <a href="/people">Our Team</a>
                        <a href="/client-interest">Partner With Us</a>
                    </nav>
                </header>
                <main>
                    <section>
                        <h2>About Us</h2>
                        <p>We are a student-run consulting organization at Purdue University that helps companies solve strategic challenges while providing students with real-world experience.</p>
                    </section>
                    <section>
                        <h2>Our Services</h2>
                        <ul>
                            <li>Market Research</li>
                            <li>Strategic Planning</li>
                            <li>Process Improvement</li>
                            <li>Financial Analysis</li>
                        </ul>
                    </section>
                    <section>
                        <h2>Get Involved</h2>
                        <p>Join our team of talented Purdue students making an impact.</p>
                        <form action="/apply" method="post">
                            <label for="name">Full Name:</label>
                            <input type="text" id="name" name="full_name" required>
                            
                            <label for="email">Email:</label>
                            <input type="email" id="email" name="email" required>
                            
                            <label for="year">Class Year:</label>
                            <select id="year" name="class_year">
                                <option value="freshman">Freshman</option>
                                <option value="sophomore">Sophomore</option>
                                <option value="junior">Junior</option>
                                <option value="senior">Senior</option>
                            </select>
                            
                            <label for="experience">Why do you want to join PurdueTHINK?</label>
                            <textarea id="experience" name="motivation" rows="4"></textarea>
                            
                            <button type="submit">Submit Application</button>
                        </form>
                    </section>
                </main>
                <footer>
                    <p>Contact us: <a href="mailto:contact@purduethink.com">contact@purduethink.com</a></p>
                    <p>Follow us: 
                        <a href="https://linkedin.com/company/purduethink">LinkedIn</a> |
                        <a href="https://instagram.com/purduethink">Instagram</a>
                    </p>
                </footer>
            </body>
            </html>
            """
        )
        
        # Extract business context
        business_info = adapter.extract_business_info_from_context("client docs/context.md")
        
        print(f"\n📈 Loaded website data for: {website_data.url}")
        print(f"📋 Business: {business_info.name or 'PurdueTHINK Consulting'}")
        print(f"🏢 CMS: {website_data.metadata.get('cms', 'Unknown')}")
        print(f"📄 Pages crawled: {website_data.metadata.get('pages_crawled', 0)}")
        
    except Exception as e:
        print(f"❌ Error loading crawler data: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🔍 AGENT ANALYSIS RESULTS")
    print("=" * 50)
    
    # Run AEO Agent Analysis
    print("\n🎯 AEO AGENT - Visibility Optimization")
    print("-" * 40)
    try:
        aeo_response = await aeo_agent.analyze(website_data)
        print(f"✅ Analysis completed in {aeo_response.processing_time:.2f}s")
        print(f"📊 Confidence: {aeo_response.confidence:.2f}")
        print(f"🔍 Found {len(aeo_response.results)} recommendations:")
        
        for i, result in enumerate(aeo_response.results[:3], 1):  # Show top 3
            print(f"\n  {i}. {result.title}")
            print(f"     Priority: {result.priority.value.upper()}")
            print(f"     Impact: {result.impact.value.upper()}")
            print(f"     {result.description}")
            if result.code_examples:
                print("     📝 Code example available")
    
    except Exception as e:
        print(f"❌ AEO Agent error: {e}")
    
    # Run GEO Agent Analysis
    print("\n📊 GEO AGENT - Data Accuracy")
    print("-" * 40)
    try:
        geo_response = await geo_agent.analyze(website_data)
        print(f"✅ Analysis completed in {geo_response.processing_time:.2f}s")
        print(f"📊 Confidence: {geo_response.confidence:.2f}")
        print(f"🔍 Found {len(geo_response.results)} recommendations:")
        
        for i, result in enumerate(geo_response.results[:3], 1):  # Show top 3
            print(f"\n  {i}. {result.title}")
            print(f"     Priority: {result.priority.value.upper()}")
            print(f"     Impact: {result.impact.value.upper()}")
            print(f"     {result.description}")
    
    except Exception as e:
        print(f"❌ GEO Agent error: {e}")
    
    # Run GEO+ Agent Analysis
    print("\n🤖 GEO+ AGENT - Actionability")
    print("-" * 40)
    try:
        geo_plus_response = await geo_plus_agent.analyze(website_data)
        print(f"✅ Analysis completed in {geo_plus_response.processing_time:.2f}s")
        print(f"📊 Confidence: {geo_plus_response.confidence:.2f}")
        print(f"🔍 Found {len(geo_plus_response.results)} recommendations:")
        
        automation_readiness = geo_plus_response.metadata.get("automation_readiness", 0.0)
        print(f"🎯 Automation Readiness Score: {automation_readiness:.2f}/1.0")
        
        for i, result in enumerate(geo_plus_response.results[:3], 1):  # Show top 3
            print(f"\n  {i}. {result.title}")
            print(f"     Priority: {result.priority.value.upper()}")
            print(f"     Impact: {result.impact.value.upper()}")
            print(f"     {result.description}")
    
    except Exception as e:
        print(f"❌ GEO+ Agent error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 ANALYSIS SUMMARY")
    print("=" * 50)
    
    try:
        total_recommendations = (
            len(aeo_response.results) + 
            len(geo_response.results) + 
            len(geo_plus_response.results)
        )
        
        avg_confidence = (
            aeo_response.confidence + 
            geo_response.confidence + 
            geo_plus_response.confidence
        ) / 3
        
        print(f"🎯 Total Recommendations: {total_recommendations}")
        print(f"📊 Average Confidence: {avg_confidence:.2f}")
        print(f"⏱️  Total Analysis Time: {aeo_response.processing_time + geo_response.processing_time + geo_plus_response.processing_time:.2f}s")
        
        # Categorize by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for response in [aeo_response, geo_response, geo_plus_response]:
            for result in response.results:
                if result.priority.value == "high":
                    high_priority.append(result)
                elif result.priority.value == "medium":
                    medium_priority.append(result)
                else:
                    low_priority.append(result)
        
        print(f"\n🚨 High Priority: {len(high_priority)} items")
        print(f"⚠️  Medium Priority: {len(medium_priority)} items")
        print(f"ℹ️  Low Priority: {len(low_priority)} items")
        
        if high_priority:
            print(f"\n🚨 Top High Priority Recommendations:")
            for i, item in enumerate(high_priority[:2], 1):
                print(f"  {i}. {item.title} ({item.type})")
        
    except Exception as e:
        print(f"❌ Summary error: {e}")
    
    print("\n✨ Analysis complete! Use these insights to optimize PurdueTHINK's website for AI discoverability.")


def print_sample_output():
    """Print sample output format for documentation."""
    print("""
📋 SAMPLE AGENT OUTPUT STRUCTURE:

AEO Agent (Visibility):
- Schema markup gaps
- Structured data recommendations  
- AI response optimization
- Content structure analysis
- Meta information optimization

GEO Agent (Accuracy):
- Business information consistency
- Contact information validation
- Data quality assessment
- External validation opportunities
- Canonical data recommendations

GEO+ Agent (Actionability):
- API endpoint analysis
- Form automation compatibility
- Interaction pattern detection
- Conversion opportunity analysis
- Automation readiness scoring

Each recommendation includes:
- Priority level (High/Medium/Low)
- Impact assessment (High/Medium/Low)
- Effort required (High/Medium/Low)
- Implementation steps
- Code examples (where applicable)
- Confidence score (0.0-1.0)
""")


if __name__ == "__main__":
    print("🎯 GEO Agents - PurdueTHINK Demo")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        print_sample_output()
    else:
        # Check if we're in the right directory
        if not os.path.exists("client docs"):
            print("❌ Error: 'client docs' directory not found.")
            print("   Please run this script from the project root directory.")
            sys.exit(1)
        
        asyncio.run(demo_purdue_think_analysis())