"""
Advanced Tools Module

Provides advanced functionality tools for LangChain agents:
- Web Search: Real web searching using DuckDuckGo
- File Operations: Safe file system operations
- Weather Information: Real weather data using wttr.in
- Random Facts: Interesting facts from online APIs
- AI News Search: AI-specific news and information
"""

import os
import requests
import json
import time
from typing import Dict, List
from pathlib import Path
from langchain_core.tools import tool

from .registry import BaseToolModule, ToolConfig, ToolCategory


class AdvancedToolsModule(BaseToolModule):
    """Module containing advanced functionality tools"""
    
    def __init__(self, memory_manager=None, enable_user_approval=False):
        super().__init__(memory_manager, enable_user_approval)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_tools(self) -> List:
        """Get all advanced tools"""
        return [
            self._create_web_search_tool(),
            self._create_file_operations_tool(),
            self._create_weather_tool(),
            self._create_random_fact_tool(),
            self._create_ai_news_search_tool()
        ]
    
    def get_tool_configs(self) -> Dict[str, ToolConfig]:
        """Get tool configurations for advanced tools"""
        return {
            "web_search": ToolConfig(
                name="web_search",
                category=ToolCategory.COMMUNICATION,
                description="Search the web for information using DuckDuckGo",
                requires_approval=True,
                risk_level="medium",
                example_usage="Search for: latest AI news",
                parameters={"query": "Search query string"},
                tags=["web", "search", "internet", "information"]
            ),
            "file_operations": ToolConfig(
                name="file_operations",
                category=ToolCategory.SYSTEM,
                description="Perform safe file operations (read, write, list)",
                requires_approval=True,
                risk_level="high",
                example_usage="Read file: data.txt",
                parameters={
                    "operation": "Type of operation (read, write, append, list, delete)",
                    "path": "File or directory path",
                    "content": "Content to write (for write/append operations)"
                },
                tags=["files", "filesystem", "io", "storage"]
            ),
            "weather_info": ToolConfig(
                name="weather_info",
                category=ToolCategory.INFORMATION,
                description="Get real weather information using wttr.in service",
                requires_approval=False,
                risk_level="low",
                example_usage="What's the weather in Tokyo?",
                parameters={"location": "City or location name"},
                tags=["weather", "forecast", "temperature", "climate"]
            ),
            "random_fact": ToolConfig(
                name="random_fact",
                category=ToolCategory.ENTERTAINMENT,
                description="Get interesting random facts from online APIs",
                requires_approval=False,
                risk_level="low",
                example_usage="Tell me a random fact",
                parameters={},
                tags=["facts", "trivia", "entertainment", "knowledge"]
            ),
            "ai_news_search": ToolConfig(
                name="ai_news_search",
                category=ToolCategory.INFORMATION,
                description="Search for AI-related news and developments",
                requires_approval=False,
                risk_level="low",
                example_usage="What's new in AI today?",
                parameters={"topic": "AI topic to search for"},
                tags=["ai", "news", "technology", "research"]
            )
        }
    
    def _create_web_search_tool(self):
        """Create web search tool using DuckDuckGo"""
        @tool
        def web_search(query: str) -> str:
            """Search the web for information using DuckDuckGo. Returns relevant search results."""
            def _perform_search():
                try:
                    if not query or not query.strip():
                        return "Error: Please provide a search query"
                    
                    # Use DuckDuckGo Instant Answer API
                    url = "https://api.duckduckgo.com/"
                    params = {
                        'q': query.strip(),
                        'format': 'json',
                        'no_html': '1',
                        'skip_disambig': '1'
                    }
                    
                    response = self.session.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    result = f"🔍 Web Search Results for: '{query}'\n\n"
                    
                    # Instant Answer
                    if data.get('AbstractText'):
                        result += f"📄 Summary:\n{data['AbstractText']}\n\n"
                        if data.get('AbstractURL'):
                            result += f"🔗 Source: {data['AbstractURL']}\n\n"
                    
                    # Answer (if available)
                    if data.get('Answer'):
                        result += f"💡 Quick Answer: {data['Answer']}\n\n"
                    
                    # Related topics
                    if data.get('RelatedTopics'):
                        result += "📚 Related Topics:\n"
                        for i, topic in enumerate(data['RelatedTopics'][:3], 1):
                            if isinstance(topic, dict) and topic.get('Text'):
                                text = topic['Text'][:150] + "..." if len(topic.get('Text', '')) > 150 else topic['Text']
                                result += f"{i}. {text}\n"
                                if topic.get('FirstURL'):
                                    result += f"   🔗 {topic['FirstURL']}\n"
                        result += "\n"
                    
                    # Definition (if available)
                    if data.get('Definition'):
                        result += f"📖 Definition: {data['Definition']}\n"
                        if data.get('DefinitionURL'):
                            result += f"🔗 Source: {data['DefinitionURL']}\n\n"
                    
                    # Infobox (if available)
                    if data.get('Infobox') and data['Infobox'].get('content'):
                        result += "ℹ️ Additional Information:\n"
                        for item in data['Infobox']['content'][:3]:
                            if item.get('label') and item.get('value'):
                                result += f"• {item['label']}: {item['value']}\n"
                        result += "\n"
                    
                    if len(result.strip()) == len(f"🔍 Web Search Results for: '{query}'"):
                        # No useful results found
                        result += "❌ No detailed information found for this query.\n"
                        result += "💡 Try rephrasing your search or being more specific.\n"
                        result += f"🌐 You can manually search at: https://duckduckgo.com/?q={query.replace(' ', '+')}"
                    
                    return result
                    
                except requests.RequestException as e:
                    return f"❌ Network error during search: {str(e)}\n💡 Please check your internet connection and try again."
                except json.JSONDecodeError:
                    return f"❌ Error parsing search results\n💡 The search service might be temporarily unavailable."
                except Exception as e:
                    return f"❌ Search error: {str(e)}\n💡 Please try again with a different query."
            
            return self.request_approval(f"Web search: {query}", _perform_search)
        
        return web_search
    
    def _create_file_operations_tool(self):
        """Create safe file operations tool"""
        @tool
        def file_operations(operation: str, path: str, content: str = "") -> str:
            """Perform safe file operations. Operations: read, write, append, list, delete. Limited to current directory and subdirectories."""
            def _perform_operation():
                try:
                    # Security: Only allow operations in current directory and subdirectories
                    base_path = Path.cwd()
                    target_path = Path(path).resolve()
                    
                    # Check if target path is within allowed directory
                    try:
                        target_path.relative_to(base_path)
                    except ValueError:
                        return f"❌ Security Error: Access denied to path outside current directory: {path}"
                    
                    operation = operation.lower().strip()
                    
                    if operation == "read":
                        if not target_path.exists():
                            return f"❌ File not found: {path}"
                        
                        if not target_path.is_file():
                            return f"❌ Path is not a file: {path}"
                        
                        # Size limit: 1MB
                        if target_path.stat().st_size > 1024 * 1024:
                            return f"❌ File too large (max 1MB): {path}"
                        
                        try:
                            with open(target_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            return f"📄 File content of '{path}':\n\n{file_content}"
                        except UnicodeDecodeError:
                            return f"❌ Unable to read file as text (binary file?): {path}"
                    
                    elif operation == "write":
                        if not content:
                            return "❌ No content provided for write operation"
                        
                        # Size limit: 10KB for writes
                        if len(content) > 10 * 1024:
                            return "❌ Content too large (max 10KB for write operations)"
                        
                        # Create parent directories if they don't exist
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(target_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        return f"✅ Successfully wrote {len(content)} characters to '{path}'"
                    
                    elif operation == "append":
                        if not content:
                            return "❌ No content provided for append operation"
                        
                        # Size limit: 10KB for appends
                        if len(content) > 10 * 1024:
                            return "❌ Content too large (max 10KB for append operations)"
                        
                        # Create parent directories if they don't exist
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(target_path, 'a', encoding='utf-8') as f:
                            f.write(content)
                        return f"✅ Successfully appended {len(content)} characters to '{path}'"
                    
                    elif operation == "list":
                        if not target_path.exists():
                            return f"❌ Path not found: {path}"
                        
                        if target_path.is_file():
                            stat = target_path.stat()
                            return f"📄 File info for '{path}':\n• Size: {stat.st_size} bytes\n• Modified: {time.ctime(stat.st_mtime)}"
                        
                        if target_path.is_dir():
                            items = list(target_path.iterdir())
                            if not items:
                                return f"📁 Directory '{path}' is empty"
                            
                            result = f"📁 Contents of directory '{path}' ({len(items)} items):\n\n"
                            
                            # Separate files and directories
                            dirs = [item for item in items if item.is_dir()]
                            files = [item for item in items if item.is_file()]
                            
                            if dirs:
                                result += "📁 Directories:\n"
                                for d in sorted(dirs)[:20]:  # Limit to 20 items
                                    result += f"  • {d.name}/\n"
                                if len(dirs) > 20:
                                    result += f"  ... and {len(dirs) - 20} more directories\n"
                                result += "\n"
                            
                            if files:
                                result += "📄 Files:\n"
                                for f in sorted(files)[:20]:  # Limit to 20 items
                                    size = f.stat().st_size
                                    size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                                    result += f"  • {f.name} ({size_str})\n"
                                if len(files) > 20:
                                    result += f"  ... and {len(files) - 20} more files\n"
                            
                            return result
                    
                    elif operation == "delete":
                        if not target_path.exists():
                            return f"❌ Path not found: {path}"
                        
                        if target_path.is_file():
                            target_path.unlink()
                            return f"✅ Successfully deleted file: {path}"
                        else:
                            return f"❌ Can only delete files, not directories: {path}"
                    
                    else:
                        return f"❌ Unknown operation: {operation}. Supported operations: read, write, append, list, delete"
                
                except PermissionError:
                    return f"❌ Permission denied: {path}"
                except FileNotFoundError:
                    return f"❌ File or directory not found: {path}"
                except Exception as e:
                    return f"❌ File operation error: {str(e)}"
            
            return self.request_approval(f"File {operation}: {path}", _perform_operation)
        
        return file_operations
    
    def _create_weather_tool(self):
        """Create weather information tool"""
        @tool
        def weather_info(location: str) -> str:
            """Get real weather information for a specified location using wttr.in service."""
            try:
                if not location or not location.strip():
                    return "❌ Please provide a location name"
                
                # Use wttr.in API for weather data
                url = f"https://wttr.in/{location.strip()}?format=j1"
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract current weather
                current = data.get('current_condition', [{}])[0]
                nearest_area = data.get('nearest_area', [{}])[0]
                
                if not current:
                    return f"❌ Weather data not available for: {location}"
                
                # Location info
                location_name = nearest_area.get('areaName', [{}])[0].get('value', location)
                country = nearest_area.get('country', [{}])[0].get('value', '')
                region = nearest_area.get('region', [{}])[0].get('value', '')
                
                # Current conditions
                temp_c = current.get('temp_C', 'N/A')
                temp_f = current.get('temp_F', 'N/A')
                feels_like_c = current.get('FeelsLikeC', 'N/A')
                feels_like_f = current.get('FeelsLikeF', 'N/A')
                humidity = current.get('humidity', 'N/A')
                visibility = current.get('visibility', 'N/A')
                pressure = current.get('pressure', 'N/A')
                wind_speed = current.get('windspeedKmph', 'N/A')
                wind_dir = current.get('winddir16Point', 'N/A')
                weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
                
                result = f"🌤️ Weather for {location_name}"
                if region and region != location_name:
                    result += f", {region}"
                if country:
                    result += f", {country}"
                result += f"\n\n"
                
                result += f"🌡️ Current Conditions:\n"
                result += f"• Temperature: {temp_c}°C ({temp_f}°F)\n"
                result += f"• Feels like: {feels_like_c}°C ({feels_like_f}°F)\n"
                result += f"• Condition: {weather_desc}\n"
                result += f"• Humidity: {humidity}%\n"
                result += f"• Wind: {wind_speed} km/h {wind_dir}\n"
                result += f"• Visibility: {visibility} km\n"
                result += f"• Pressure: {pressure} mb\n\n"
                
                # 3-day forecast
                weather_data = data.get('weather', [])
                if weather_data:
                    result += "📅 3-Day Forecast:\n"
                    for day_data in weather_data[:3]:
                        date = day_data.get('date', '')
                        max_temp_c = day_data.get('maxtempC', 'N/A')
                        min_temp_c = day_data.get('mintempC', 'N/A')
                        max_temp_f = day_data.get('maxtempF', 'N/A')
                        min_temp_f = day_data.get('mintempF', 'N/A')
                        
                        # Get hourly data for better description
                        hourly = day_data.get('hourly', [])
                        if hourly:
                            desc = hourly[len(hourly)//2].get('weatherDesc', [{}])[0].get('value', 'N/A')
                        else:
                            desc = 'N/A'
                        
                        result += f"• {date}: {min_temp_c}°C - {max_temp_c}°C ({min_temp_f}°F - {max_temp_f}°F) - {desc}\n"
                
                return result
                
            except requests.RequestException as e:
                return f"❌ Network error getting weather data: {str(e)}\n💡 Please check your internet connection."
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                return f"❌ Error parsing weather data for '{location}'\n💡 Please check the location name and try again."
            except Exception as e:
                return f"❌ Weather service error: {str(e)}"
        
        return weather_info
    
    def _create_random_fact_tool(self):
        """Create random fact tool"""
        @tool
        def random_fact() -> str:
            """Get an interesting random fact from online APIs."""
            try:
                # Primary API: uselessfacts.jsph.pl
                url = "https://uselessfacts.jsph.pl/random.json?language=en"
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                fact = data.get('text', '').strip()
                
                if fact:
                    return f"🎲 Random Fact:\n\n{fact}\n\n💡 Source: uselessfacts.jsph.pl"
                else:
                    # Fallback to local facts
                    return self._get_fallback_fact()
                    
            except Exception:
                # Fallback to local facts if API fails
                return self._get_fallback_fact()
    
        return random_fact
    
    def _get_fallback_fact(self):
        """Get a fallback fact from local storage"""
        import random
        
        facts = [
            "Honey never spoils. Archaeologists have found edible honey in ancient Egyptian tombs.",
            "Octopuses have three hearts and blue blood.",
            "A group of flamingos is called a 'flamboyance'.",
            "Bananas are berries, but strawberries aren't.",
            "The shortest war in history lasted only 38-45 minutes (Anglo-Zanzibar War, 1896).",
            "Sharks have been around longer than trees.",
            "A day on Venus is longer than its year.",
            "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
            "There are more possible games of chess than atoms in the observable universe.",
            "Wombat feces is cube-shaped."
        ]
        
        fact = random.choice(facts)
        return f"🎲 Random Fact:\n\n{fact}\n\n💡 Source: Local fact database"
    
    def _create_ai_news_search_tool(self):
        """Create AI news search tool"""
        @tool
        def ai_news_search(topic: str = "artificial intelligence") -> str:
            """Search for AI-related news and developments. Provide a specific AI topic or leave empty for general AI news."""
            def _search_ai_news():
                try:
                    # Enhance the query with AI-related terms
                    ai_query = f"artificial intelligence {topic}" if topic and topic.lower() not in ["ai", "artificial intelligence"] else "artificial intelligence news"
                    
                    # Use the web search functionality but focus on AI content
                    # Create a more specific query
                    search_terms = [
                        f"{ai_query} latest news",
                        f"{ai_query} research breakthrough",
                        f"{ai_query} technology development",
                        f"{ai_query} machine learning"
                    ]
                    
                    # Try the first search term
                    url = "https://api.duckduckgo.com/"
                    params = {
                        'q': search_terms[0],
                        'format': 'json',
                        'no_html': '1',
                        'skip_disambig': '1'
                    }
                    
                    response = self.session.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    result = f"🤖 AI News Search Results for: '{topic}'\n\n"
                    
                    # Check for relevant content
                    if data.get('AbstractText'):
                        result += f"📰 Latest Information:\n{data['AbstractText']}\n\n"
                    
                    if data.get('RelatedTopics'):
                        result += "🔬 Related AI Topics:\n"
                        for i, topic_item in enumerate(data['RelatedTopics'][:5], 1):
                            if isinstance(topic_item, dict) and topic_item.get('Text'):
                                text = topic_item['Text']
                                if any(keyword in text.lower() for keyword in ['ai', 'artificial intelligence', 'machine learning', 'neural', 'algorithm']):
                                    result += f"{i}. {text[:200]}{'...' if len(text) > 200 else ''}\n"
                                    if topic_item.get('FirstURL'):
                                        result += f"   🔗 {topic_item['FirstURL']}\n"
                        result += "\n"
                    
                    # Add some AI-specific suggestions
                    suggestions = [
                        "🧠 Machine Learning and Neural Networks",
                        "🤖 Robotics and Automation",
                        "💬 Natural Language Processing",
                        "👁️ Computer Vision and Image Recognition",
                        "🔬 AI Research and Ethics",
                        "🏢 AI in Business and Industry",
                        "🎮 AI in Gaming and Entertainment"
                    ]
                    
                    result += f"💡 Suggested AI Topics to Explore:\n"
                    for suggestion in suggestions:
                        result += f"• {suggestion}\n"
                    
                    return result
                    
                except Exception as e:
                    return f"❌ AI news search encountered an error: {str(e)}\n\n💡 Suggest using the general web search tool for queries."
            
            return _search_ai_news()
        
        return ai_news_search 