"""
Internet Search Module for SEEU AI
Uses Tavily API for real-time internet searches
Handles: Weather, News, Sports, Current Events, General Information
"""

import os
from dotenv import load_dotenv
from typing import Optional, Dict, List
from datetime import datetime

# Load environment variables
load_dotenv()

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ Tavily not installed. Run: pip install tavily-python")


class InternetSearchEngine:
    """
    Advanced Internet Search Engine using Tavily API
    Provides real-time information for weather, news, sports, and general queries
    """

    def __init__(self):
        """Initialize the Internet Search Engine"""
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

        if not self.tavily_api_key:
            print("⚠️ TAVILY_API_KEY not found in .env file")
            self.client = None
        elif not TAVILY_AVAILABLE:
            print("⚠️ Tavily library not available")
            self.client = None
        else:
            try:
                self.client = TavilyClient(api_key=self.tavily_api_key)
                print("✅ Internet Search Engine initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Tavily client: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Check if internet search is available"""
        return self.client is not None

    def search(self, query: str, search_depth: str = "basic", max_results: int = 5) -> Dict:
        """
        Perform internet search using Tavily API

        Args:
            query: Search query
            search_depth: "basic" or "advanced" (advanced uses more credits)
            max_results: Maximum number of results to return

        Returns:
            Dict containing search results and formatted response
        """
        if not self.is_available():
            return {
                'success': False,
                'response': "Internet search is not available. Please configure TAVILY_API_KEY in your .env file.",
                'results': []
            }

        try:
            print(f"🔍 Searching the internet for: {query}")

            # Perform search
            search_result = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_answer=True,
                include_raw_content=False
            )

            # Extract answer and results
            answer = search_result.get('answer', '')
            results = search_result.get('results', [])

            # Format response
            formatted_response = self._format_search_response(query, answer, results)

            print(f"✅ Found {len(results)} results")

            return {
                'success': True,
                'response': formatted_response,
                'answer': answer,
                'results': results,
                'query': query
            }

        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'response': f"I encountered an error while searching: {str(e)}",
                'results': []
            }

    def _format_search_response(self, query: str, answer: str, results: List[Dict]) -> str:
        """
        Format search results into a conversational response

        Args:
            query: Original search query
            answer: AI-generated answer from Tavily
            results: List of search results

        Returns:
            Formatted response string
        """
        response = ""

        # Add the main answer if available
        if answer:
            response = answer
        else:
            # If no direct answer, summarize top results
            if results:
                top_result = results[0]
                response = f"Based on my search, {top_result.get('content', 'No content available')}"

        # Add source information for credibility
        if results:
            sources = []
            for result in results[:3]:  # Top 3 sources
                title = result.get('title', '')
                url = result.get('url', '')
                if title:
                    sources.append(title)

            if sources:
                response += f"\n\nSources: {', '.join(sources)}"

        return response

    def search_weather(self, location: str) -> Dict:
        """
        Search for weather information

        Args:
            location: City name or location

        Returns:
            Dict containing weather information
        """
        query = f"current weather in {location} today temperature forecast"
        return self.search(query, search_depth="basic", max_results=3)

    def search_news(self, topic: str = "latest news") -> Dict:
        """
        Search for latest news

        Args:
            topic: News topic (default: latest news)

        Returns:
            Dict containing news information
        """
        query = f"{topic} latest news today {datetime.now().strftime('%Y-%m-%d')}"
        return self.search(query, search_depth="basic", max_results=5)

    def search_sports(self, query: str) -> Dict:
        """
        Search for sports information

        Args:
            query: Sports-related query

        Returns:
            Dict containing sports information
        """
        sports_query = f"{query} latest result score today {datetime.now().strftime('%Y-%m-%d')}"
        return self.search(sports_query, search_depth="basic", max_results=3)

    def search_general(self, query: str) -> Dict:
        """
        General internet search

        Args:
            query: Any search query

        Returns:
            Dict containing search results
        """
        return self.search(query, search_depth="basic", max_results=5)

    def quick_answer(self, query: str) -> str:
        """
        Get a quick answer from internet search

        Args:
            query: Search query

        Returns:
            Quick answer string
        """
        result = self.search(query, search_depth="basic", max_results=3)
        return result.get('response', "I couldn't find information about that.")


# Global instance
_search_engine = None

def get_search_engine() -> InternetSearchEngine:
    """Get or create global search engine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = InternetSearchEngine()
    return _search_engine


def search_internet(query: str) -> str:
    """
    Quick function to search the internet

    Args:
        query: Search query

    Returns:
        Search result as string
    """
    engine = get_search_engine()
    result = engine.search_general(query)
    return result.get('response', "I couldn't find information about that.")


def search_weather(location: str) -> str:
    """
    Quick function to get weather information

    Args:
        location: City or location name

    Returns:
        Weather information as string
    """
    engine = get_search_engine()
    result = engine.search_weather(location)
    return result.get('response', f"I couldn't find weather information for {location}.")


def search_news(topic: str = "latest news") -> str:
    """
    Quick function to get latest news

    Args:
        topic: News topic

    Returns:
        News information as string
    """
    engine = get_search_engine()
    result = engine.search_news(topic)
    return result.get('response', "I couldn't find the latest news.")


def search_sports(query: str) -> str:
    """
    Quick function to get sports information

    Args:
        query: Sports query

    Returns:
        Sports information as string
    """
    engine = get_search_engine()
    result = engine.search_sports(query)
    return result.get('response', f"I couldn't find information about {query}.")


# Test function
if __name__ == "__main__":
    print("\n🌐 SEEU Internet Search Engine - Test Mode")
    print("=" * 60)

    engine = InternetSearchEngine()

    if not engine.is_available():
        print("❌ Internet search is not available. Please configure TAVILY_API_KEY.")
        print("Add this to your .env file:")
        print("TAVILY_API_KEY=your_tavily_api_key_here")
        exit(1)

    # Test queries
    test_queries = [
        ("Weather in Mumbai", lambda: engine.search_weather("Mumbai")),
        ("Latest technology news", lambda: engine.search_news("technology")),
        ("Who won the IPL match today", lambda: engine.search_sports("IPL match today")),
        ("What is the temperature in Pune", lambda: engine.search_weather("Pune")),
        ("Latest AI developments", lambda: engine.search_general("latest AI developments 2026")),
    ]

    for description, query_func in test_queries:
        print(f"\n{'=' * 60}")
        print(f"🔍 Test: {description}")
        print('=' * 60)
        result = query_func()
        print(f"\n✅ Result:")
        print(result.get('response', 'No response'))
        print(f"\n📊 Success: {result.get('success', False)}")
        print('=' * 60)

        # Wait for user input to continue
        input("\nPress Enter to continue to next test...")

    print("\n✅ All tests completed!")
    print("=" * 60)