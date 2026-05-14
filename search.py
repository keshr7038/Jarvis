from duckduckgo_search import DDGS
import time

def web_search(query, max_results=5):
    """
    Advanced web search with multiple results
    and automatic retry on failure.
    """
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    'title': r['title'],
                    'body':  r['body'],
                    'url':   r['href']
                })
        return results

    except Exception:
        # Retry once after short delay
        try:
            time.sleep(1)
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': r['title'],
                        'body':  r['body'],
                        'url':   r['href']
                    })
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []


def news_search(query, max_results=3):
    """Search specifically for news articles"""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                results.append({
                    'title': r['title'],
                    'body':  r['body'],
                    'url':   r['url'],
                    'date':  r.get('date', 'Recent')
                })
        return results
    except Exception as e:
        print(f"News search error: {e}")
        return []


def image_search(query, max_results=3):
    """Search for images"""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.images(query, max_results=max_results):
                results.append({
                    'title': r['title'],
                    'url':   r['url'],
                    'image': r['image']
                })
        return results
    except Exception as e:
        print(f"Image search error: {e}")
        return []


def format_results(results, is_news=False):
    """Format results into clean readable text"""
    if not results:
        return "No results found."

    formatted = ""
    for i, r in enumerate(results, 1):
        formatted += f"Result {i}:\n"
        formatted += f"Title: {r['title']}\n"
        formatted += f"Summary: {r['body']}\n"
        if is_news and 'date' in r:
            formatted += f"Date: {r['date']}\n"
        formatted += f"Source: {r['url']}\n\n"

    return formatted.strip()


def should_search(user_input):
    """Decide if web search is needed"""
    search_triggers = [
        'search', 'look up', 'find', 'what is', 'what are',
        'who is', 'who are', 'where is', 'when is', 'when did',
        'how much', 'how many', 'latest', 'recent', 'news',
        'today', 'current', 'price', 'score', 'tell me about',
        'information on', 'details about', 'explain', 'define',
        'meaning of', 'how to', 'why is', 'why are', 'which is',
        'best', 'top', 'review', 'compare', 'difference between',
        'vs', 'versus', 'upcoming', 'release date', 'launch'
    ]
    user_lower = user_input.lower()
    return any(trigger in user_lower for trigger in search_triggers)


def is_news_query(user_input):
    """Check if user wants news specifically"""
    news_triggers = [
        'news', 'latest news', 'breaking', 'headlines',
        'what happened', 'recent events', 'update on'
    ]
    user_lower = user_input.lower()
    return any(trigger in user_lower for trigger in news_triggers)