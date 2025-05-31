"""
Streamlit Web Interface for LangChain Agent with Memory Demo

Run with: streamlit run streamlit_demo.py

Updated for LangChain 0.3.x compatibility with OpenRouter support
Advanced Agent Configuration with MCP Support and Streaming
"""

import streamlit as st
import os
import datetime
import json
import yaml
import asyncio
import time
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, AsyncIterator, Iterator
import requests
import urllib.parse
import pathlib
import re

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor, create_react_agent, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.agents.agent_types import AgentType
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Advanced LangChain Agent with Memory Demo",
    page_icon="🧠",
    layout="wide"
)

class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming agent thoughts and tool calls"""
    
    def __init__(self, container):
        self.container = container
        self.step_counter = 0
        self.current_text = ""
        self.sections = {}  # Track different sections
        self.current_thinking_placeholder = None
        self.current_tool_placeholder = None
        
    def _safe_streamlit_call(self, func):
        """Safely call Streamlit functions with error handling"""
        try:
            return func()
        except Exception as e:
            # If Streamlit is not available or there's an API error, silently continue
            print(f"Streamlit callback error: {e}")
            return None
    
    def _get_next_step(self):
        """Get next step number"""
        self.step_counter += 1
        return self.step_counter
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Called when LLM starts generating"""
        step_num = self._get_next_step()
        
        def create_thinking_section():
            with self.container:
                # Create a unique container for this thinking step
                thinking_container = st.container()
                with thinking_container:
                    st.markdown(f"#### 🤔 Step {step_num}: Agent Thinking")
                    self.current_thinking_placeholder = st.empty()
                    with self.current_thinking_placeholder:
                        st.info("🧠 Analyzing the request...")
        
        self._safe_streamlit_call(create_thinking_section)
    
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Called when a new token is generated"""
        self.current_text += token
        
        def update_thinking():
            if self.current_thinking_placeholder:
                with self.current_thinking_placeholder:
                    # Show abbreviated thinking with typing indicator
                    display_text = self.current_text.strip()
                    if len(display_text) > 150:
                        display_text = display_text[:150] + "..."
                    
                    if display_text:
                        st.markdown(f"💭 **Thinking:** {display_text}▌")
                    else:
                        st.info("🧠 Processing...")
        
        self._safe_streamlit_call(update_thinking)
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM finishes generating"""
        def finalize_thinking():
            if self.current_thinking_placeholder and self.current_text.strip():
                with self.current_thinking_placeholder:
                    # Show final thinking result
                    final_text = self.current_text.strip()
                    if len(final_text) > 150:
                        st.markdown(f"💭 **Thinking:** {final_text[:150]}...")
                        with st.expander("📝 View Full Reasoning", expanded=False):
                            st.text(final_text)
                    else:
                        st.markdown(f"💭 **Thinking:** {final_text}")
            elif self.current_thinking_placeholder:
                with self.current_thinking_placeholder:
                    st.success("✅ Thinking completed")
        
        self._safe_streamlit_call(finalize_thinking)
        self.current_text = ""
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Called when a tool starts executing"""
        tool_name = serialized.get("name", "Unknown Tool")
        step_num = self._get_next_step()
        
        def create_tool_section():
            with self.container:
                # Create a unique container for this tool step
                tool_container = st.container()
                with tool_container:
                    st.markdown(f"#### 🔧 Step {step_num}: Using Tool")
                    
                    # Tool info in columns
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"**Tool:** `{tool_name}`")
                    with col2:
                        st.markdown(f"**Input:** `{input_str}`")
                    
                    # Tool execution status
                    self.current_tool_placeholder = st.empty()
                    with self.current_tool_placeholder:
                        st.info("🔄 Executing tool...")
        
        self._safe_streamlit_call(create_tool_section)
    
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when a tool finishes executing"""
        def update_tool_result():
            if self.current_tool_placeholder:
                with self.current_tool_placeholder:
                    st.success("✅ Tool execution completed")
                    
                    # Show output in expandable section
                    if len(output) > 100:
                        with st.expander("📋 View Tool Output", expanded=False):
                            st.code(output, language="text")
                    else:
                        st.code(output, language="text")
        
        self._safe_streamlit_call(update_tool_result)
    
    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when a tool encounters an error"""
        def show_tool_error():
            if self.current_tool_placeholder:
                with self.current_tool_placeholder:
                    st.error(f"❌ Tool error: {str(error)}")
        
        self._safe_streamlit_call(show_tool_error)
    
    def on_agent_finish(self, finish, **kwargs: Any) -> None:
        """Called when agent finishes"""
        def show_completion():
            with self.container:
                st.markdown("---")
                st.success("🎉 **Agent task completed successfully!**")
        
        self._safe_streamlit_call(show_completion)

class AdvancedStreamlitMemoryAgent:
    def __init__(self, 
                 api_key: str, 
                 api_base: Optional[str] = None, 
                 model: str = "openai/gpt-3.5-turbo", 
                 enabled_tools: Optional[List[str]] = None,
                 agent_type: str = "tool_calling",
                 custom_prompt: Optional[str] = None,
                 enable_user_approval: bool = False,
                 mcp_servers: Optional[List[Dict]] = None,
                 enable_streaming: bool = True,
                 show_reasoning: bool = True):
        """Initialize the advanced agent with comprehensive configuration"""
        
        self.api_key = api_key
        self.api_base = api_base or "https://openrouter.ai/api/v1"
        self.model = model
        self.enabled_tools = enabled_tools or []
        self.agent_type = agent_type
        self.custom_prompt = custom_prompt
        self.enable_user_approval = enable_user_approval
        self.mcp_servers = mcp_servers or []
        self.enable_streaming = enable_streaming
        self.show_reasoning = show_reasoning
        self.pending_actions = []
        
        if not self.api_key:
            self.api_available = False
            return
        
        self.api_available = True
        
        # Initialize the LLM with OpenRouter configuration
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=0.7,
            api_key=self.api_key,
            base_url=self.api_base,
            streaming=self.enable_streaming,
            default_headers={
                "HTTP-Referer": "https://github.com/langchain-ai/langchain",
                "X-Title": "Advanced LangChain Streamlit Demo"
            }
        )
        
        # Setup tools (including MCP tools)
        self.tools = self._create_tools()
        
        # Setup agent based on type
        self._setup_agent()
        
        # Setup memory store
        self.store = {}
        
        # Configure RunnableWithMessageHistory based on agent type
        if self.agent_type == "react" and self.tools:
            # Only react agents need custom history handling for PromptTemplate
            def agent_with_history_wrapper(inputs, config=None):
                session_id = config.get("configurable", {}).get("session_id", "default") if config else "default"
                session_history = self._get_session_history(session_id)
                
                # Convert message history to string format for PromptTemplate agents
                chat_history_str = ""
                for message in session_history.messages:
                    if hasattr(message, 'type'):
                        if message.type == "human":
                            chat_history_str += f"Human: {message.content}\n"
                        elif message.type == "ai":
                            chat_history_str += f"Assistant: {message.content}\n"
                
                # Prepare inputs for the agent
                agent_inputs = {
                    "input": inputs["input"],
                    "chat_history": chat_history_str.strip()
                }
                
                # Execute the agent
                result = self.agent_executor.invoke(agent_inputs)
                
                # Add the conversation to history
                from langchain_core.messages import HumanMessage, AIMessage
                session_history.add_message(HumanMessage(content=inputs["input"]))
                session_history.add_message(AIMessage(content=result["output"]))
                
                return result
            
            from langchain_core.runnables import RunnableLambda
            self.agent_with_chat_history = RunnableLambda(agent_with_history_wrapper)
        else:
            # For tool_calling and structured_chat agents and simple chat, use standard message history
            self.agent_with_chat_history = RunnableWithMessageHistory(
                self.agent_executor,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
    
    def _create_tools(self):
        """Create tools for the agent based on enabled tools and MCP servers"""
        all_tools = {}
        
        # Standard tools
        @tool
        def calculator(expression: str) -> str:
            """Calculate mathematical expressions. Input should be a valid mathematical expression."""
            if self.enable_user_approval:
                return self._request_approval(f"Calculate: {expression}", lambda: self._safe_calculate(expression))
            return self._safe_calculate(expression)
        
        @tool
        def get_current_time() -> str:
            """Get the current date and time with timezone information."""
            now = datetime.datetime.now()
            return f"""Current time information:
• Local time: {now.strftime('%Y-%m-%d %H:%M:%S')}
• Day of week: {now.strftime('%A')}
• ISO format: {now.isoformat()}
• Unix timestamp: {int(now.timestamp())}"""
        
        @tool
        def note_taker(note: str) -> str:
            """Save a note with timestamp for later reference."""
            if 'notes' not in st.session_state:
                st.session_state.notes = []
            
            # 添加时间戳
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            note_with_timestamp = {
                'content': note,
                'timestamp': timestamp,
                'id': len(st.session_state.notes) + 1
            }
            
            st.session_state.notes.append(note_with_timestamp)
            return f"✅ Note #{note_with_timestamp['id']} saved at {timestamp}: {note}"
        
        @tool
        def get_notes() -> str:
            """Retrieve all saved notes with timestamps and IDs."""
            if 'notes' not in st.session_state or not st.session_state.notes:
                return "📝 No notes saved yet."
            
            # 处理旧格式的笔记（字符串）和新格式的笔记（字典）
            formatted_notes = []
            for i, note in enumerate(st.session_state.notes):
                if isinstance(note, dict):
                    formatted_notes.append(f"#{note['id']} [{note['timestamp']}]: {note['content']}")
                else:
                    # 兼容旧格式
                    formatted_notes.append(f"#{i+1}: {note}")
            
            return f"📝 Your saved notes ({len(st.session_state.notes)} total):\n\n" + "\n\n".join(formatted_notes)
        
        @tool
        def weather_info(location: str = "Beijing") -> str:
            """Get real weather information for a location using wttr.in service."""
            try:
                # 使用wttr.in免费天气服务
                url = f"https://wttr.in/{urllib.parse.quote(location)}?format=3"
                headers = {'User-Agent': 'curl/7.64.1'}
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    weather_data = response.text.strip()
                    return f"Current weather: {weather_data}"
                else:
                    return f"Unable to get weather for {location}. Service returned status: {response.status_code}"
                    
            except requests.exceptions.RequestException as e:
                return f"Weather service temporarily unavailable: {str(e)}"
            except Exception as e:
                return f"Error getting weather data: {str(e)}"
        
        @tool
        def random_fact() -> str:
            """Get a random interesting fact from online API."""
            try:
                # 尝试从免费的事实API获取随机事实
                response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    fact = data.get('text', '').strip()
                    if fact:
                        return f"Random fact: {fact}"
                
                # 如果API失败，使用备用事实库
                backup_facts = [
                    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
                    "A group of flamingos is called a 'flamboyance'.",
                    "Octopuses have three hearts and blue blood.",
                    "The shortest war in history lasted only 38-45 minutes between Britain and Zanzibar in 1896.",
                    "Bananas are berries, but strawberries aren't.",
                    "The human brain contains approximately 86 billion neurons.",
                    "A day on Venus is longer than its year.",
                    "Sharks have been around longer than trees.",
                    "There are more possible games of chess than atoms in the observable universe.",
                    "A single cloud can weigh more than a million pounds."
                ]
                import random
                return f"Random fact (backup): {random.choice(backup_facts)}"
                
            except Exception as e:
                # 失败时返回一个简单的事实
                return f"Random fact: Did you know that the word 'set' has the most different meanings in the English language? (Error accessing fact API: {str(e)})"
        
        @tool
        def text_analyzer(text: str) -> str:
            """Analyze text and provide comprehensive statistics and insights."""
            if not text.strip():
                return "No text provided for analysis."
            
            try:
                # 基础统计
                words = text.split()
                lines = text.split('\n')
                paragraphs = [p for p in text.split('\n\n') if p.strip()]
                
                chars_total = len(text)
                chars_no_spaces = len(text.replace(' ', ''))
                chars_no_whitespace = len(re.sub(r'\s', '', text))
                
                # 句子分析
                sentence_endings = re.findall(r'[.!?]+', text)
                sentences = len(sentence_endings)
                
                # 词汇分析
                word_lengths = [len(word.strip('.,!?;:"()[]{}')) for word in words if word.strip('.,!?;:"()[]{}')]
                avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
                
                # 词频分析（去除标点符号）
                clean_words = [re.sub(r'[^\w]', '', word.lower()) for word in words if re.sub(r'[^\w]', '', word.lower())]
                word_freq = {}
                for word in clean_words:
                    if len(word) > 2:  # 只统计长度大于2的词
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                # 获取最常见的词
                top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
                
                # 语言特征分析
                uppercase_chars = sum(1 for c in text if c.isupper())
                lowercase_chars = sum(1 for c in text if c.islower())
                digits = sum(1 for c in text if c.isdigit())
                punctuation = sum(1 for c in text if c in '.,!?;:"()[]{}')
                
                # 可读性评估（简化版Flesch Reading Ease）
                if sentences > 0 and len(words) > 0:
                    avg_sentence_length = len(words) / sentences
                    readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
                    if readability_score >= 90:
                        readability = "Very Easy"
                    elif readability_score >= 80:
                        readability = "Easy"
                    elif readability_score >= 70:
                        readability = "Fairly Easy"
                    elif readability_score >= 60:
                        readability = "Standard"
                    elif readability_score >= 50:
                        readability = "Fairly Difficult"
                    elif readability_score >= 30:
                        readability = "Difficult"
                    else:
                        readability = "Very Difficult"
                else:
                    readability = "Cannot determine"
                    avg_sentence_length = 0
                
                # 构建分析结果
                analysis = f"""📊 **Comprehensive Text Analysis**
                
**📈 Basic Statistics:**
• Total characters: {chars_total:,}
• Characters (no spaces): {chars_no_spaces:,}
• Characters (no whitespace): {chars_no_whitespace:,}
• Words: {len(words):,}
• Lines: {len(lines):,}
• Paragraphs: {len(paragraphs):,}
• Sentences: {sentences:,}

**📏 Length Analysis:**
• Average word length: {avg_word_length:.1f} characters
• Average sentence length: {avg_sentence_length:.1f} words
• Words per paragraph: {len(words)/len(paragraphs) if paragraphs else 0:.1f} (avg)

**🔤 Character Composition:**
• Uppercase letters: {uppercase_chars:,} ({uppercase_chars/chars_total*100:.1f}%)
• Lowercase letters: {lowercase_chars:,} ({lowercase_chars/chars_total*100:.1f}%)
• Digits: {digits:,} ({digits/chars_total*100:.1f}%)
• Punctuation: {punctuation:,} ({punctuation/chars_total*100:.1f}%)

**📚 Readability:**
• Reading difficulty: {readability}

**🔥 Most Frequent Words:**"""

                for i, (word, freq) in enumerate(top_words, 1):
                    analysis += f"\n{i}. '{word}' appears {freq} times"
                
                if not top_words:
                    analysis += "\nNo significant word patterns found"
                
                return analysis
                
            except Exception as e:
                return f"Error analyzing text: {str(e)}"
        
        @tool
        def file_operations(operation: str, filename: str, content: str = "") -> str:
            """Perform file operations (read, write, list). Use with caution."""
            if self.enable_user_approval:
                return self._request_approval(
                    f"File operation: {operation} on {filename}", 
                    lambda: self._safe_file_operation(operation, filename, content)
                )
            return self._safe_file_operation(operation, filename, content)
        
        @tool
        def web_search(query: str) -> str:
            """Search the web for real information using multiple strategies."""
            def _perform_search():
                results = []
                
                try:
                    # 策略1: DuckDuckGo即时答案API
                    search_url = "https://api.duckduckgo.com/"
                    params = {
                        'q': query,
                        'format': 'json',
                        'no_html': '1',
                        'skip_disambig': '1'
                    }
                    
                    response = requests.get(search_url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # 收集所有可用信息
                        if data.get('AbstractText'):
                            results.append(f"📝 **摘要信息:**\n{data['AbstractText']}")
                            if data.get('AbstractURL'):
                                results.append(f"🔗 **来源:** {data['AbstractURL']}")
                        
                        if data.get('Answer'):
                            results.append(f"💡 **即时答案:**\n{data['Answer']}")
                        
                        if data.get('Definition'):
                            results.append(f"📖 **定义:**\n{data['Definition']}")
                        
                        # 处理相关主题
                        if data.get('RelatedTopics'):
                            topic_results = []
                            for topic in data['RelatedTopics'][:5]:  # 增加到5个
                                if isinstance(topic, dict):
                                    if 'Text' in topic:
                                        topic_results.append(f"• {topic['Text']}")
                                    elif 'Topics' in topic:  # 处理嵌套主题
                                        for subtopic in topic['Topics'][:3]:
                                            if 'Text' in subtopic:
                                                topic_results.append(f"• {subtopic['Text']}")
                            
                            if topic_results:
                                results.append(f"🔍 **相关信息:**\n" + "\n".join(topic_results))
                        
                        # 处理结果
                        if data.get('Results'):
                            search_results = []
                            for result in data['Results'][:3]:
                                if 'Text' in result and 'FirstURL' in result:
                                    search_results.append(f"• {result['Text']}\n  🔗 {result['FirstURL']}")
                            
                            if search_results:
                                results.append(f"🌐 **搜索结果:**\n" + "\n\n".join(search_results))
                
                except Exception as e:
                    results.append(f"⚠️ DuckDuckGo搜索遇到问题: {str(e)}")
                
                # 策略2: 如果没有找到足够信息，尝试HTTP搜索请求
                if len(results) == 0:
                    try:
                        # 使用HTML搜索作为备用方案
                        search_url = f"https://html.duckduckgo.com/html/"
                        params = {'q': query}
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        }
                        
                        response = requests.get(search_url, params=params, headers=headers, timeout=10)
                        
                        if response.status_code == 200:
                            # 简单的HTML解析来提取搜索结果标题
                            import re
                            titles = re.findall(r'<a[^>]*class="result__a"[^>]*>([^<]+)</a>', response.text)
                            
                            if titles:
                                results.append(f"🔍 **找到的相关主题:**\n" + "\n".join([f"• {title.strip()}" for title in titles[:5]]))
                            else:
                                results.append(f"🔍 搜索完成，但没有找到直接相关的结果。建议尝试更具体的搜索词。")
                        
                    except Exception as e:
                        results.append(f"⚠️ 备用搜索方法也遇到问题: {str(e)}")
                
                # 如果仍然没有结果，提供搜索建议
                if len(results) == 0:
                    # 分析查询并提供搜索建议
                    suggestions = []
                    if 'latest' in query.lower() or '最新' in query.lower():
                        suggestions.append("• 尝试搜索具体的公司名称或产品名称")
                        suggestions.append("• 使用更具体的时间范围，如 '2024' 或 'recent'")
                    
                    if 'ai' in query.lower() or 'artificial intelligence' in query.lower():
                        suggestions.append("• 尝试搜索 'OpenAI', 'Google AI', 'Microsoft AI' 等")
                        suggestions.append("• 搜索具体的AI技术，如 'GPT', 'ChatGPT', 'Claude' 等")
                    
                    if 'news' in query.lower() or '新闻' in query.lower():
                        suggestions.append("• 尝试搜索具体的事件或公告")
                        suggestions.append("• 使用关键词而不是'新闻'或'news'")
                    
                    result_text = f"🔍 **搜索完成:** '{query}'\n\n"
                    result_text += "ℹ️ **没有找到直接匹配的信息。建议优化搜索策略:**\n"
                    result_text += "\n".join(suggestions) if suggestions else "• 尝试使用更具体的关键词\n• 使用英文关键词可能获得更好的结果"
                    
                    return result_text
                
                # 组装最终结果
                final_result = f"🔍 **搜索结果:** '{query}'\n\n" + "\n\n".join(results)
                
                # 如果结果太长，截断并提供摘要
                if len(final_result) > 2000:
                    final_result = final_result[:1800] + "\n\n... (结果已截断，以上是最相关的信息)"
                
                return final_result
                
            if self.enable_user_approval:
                return self._request_approval(f"Web search: {query}", _perform_search)
            else:
                return _perform_search()
        
        @tool
        def ai_news_search(topic: str = "AI agent") -> str:
            """Search for recent AI and technology news and developments."""
            def _search_ai_news():
                try:
                    # 构建专门的AI新闻搜索查询
                    search_queries = [
                        f"{topic} 2024",
                        f"{topic} recent developments",
                        f"{topic} breakthrough",
                        f"{topic} OpenAI Google Microsoft"
                    ]
                    
                    all_results = []
                    
                    for query in search_queries[:2]:  # 只执行前两个查询避免过多请求
                        try:
                            search_url = "https://api.duckduckgo.com/"
                            params = {
                                'q': query,
                                'format': 'json',
                                'no_html': '1',
                                'skip_disambig': '1'
                            }
                            
                            response = requests.get(search_url, params=params, timeout=8)
                            
                            if response.status_code == 200:
                                data = response.json()
                                
                                if data.get('RelatedTopics'):
                                    for topic_item in data['RelatedTopics'][:3]:
                                        if isinstance(topic_item, dict) and 'Text' in topic_item:
                                            all_results.append(topic_item['Text'])
                                        elif isinstance(topic_item, dict) and 'Topics' in topic_item:
                                            for subtopic in topic_item['Topics'][:2]:
                                                if 'Text' in subtopic:
                                                    all_results.append(subtopic['Text'])
                                
                                if data.get('AbstractText'):
                                    all_results.append(data['AbstractText'])
                                    
                        except Exception:
                            continue  # 如果一个查询失败，继续下一个
                    
                    # 整理结果
                    if all_results:
                        # 去重并过滤
                        unique_results = []
                        seen = set()
                        for result in all_results:
                            if result not in seen and len(result) > 50:  # 过滤太短的结果
                                unique_results.append(result)
                                seen.add(result)
                        
                        if unique_results:
                            result_text = f"🤖 **AI技术动态搜索:** '{topic}'\n\n"
                            result_text += "📊 **找到的相关信息:**\n\n"
                            
                            for i, result in enumerate(unique_results[:5], 1):
                                result_text += f"**{i}.** {result}\n\n"
                            
                            return result_text
                    
                    # 如果没有找到结果，提供AI相关的搜索建议
                    suggestions = [
                        "🔍 **建议的AI搜索主题:**",
                        "• OpenAI GPT-4 developments",
                        "• Google Bard AI updates", 
                        "• Microsoft Copilot features",
                        "• Claude AI capabilities",
                        "• AI agent frameworks",
                        "• Autonomous AI systems",
                        "• Large language models",
                        "• AI safety research",
                        "",
                        "💡 **搜索技巧:**",
                        "• 使用具体的产品名称或公司名称",
                        "• 添加年份(2024)获取最新信息",
                        "• 使用英文关键词通常获得更好的结果"
                    ]
                    
                    return f"🤖 **AI新闻搜索:** '{topic}'\n\n" + "\n".join(suggestions)
                    
                except Exception as e:
                    return f"❌ AI新闻搜索遇到错误: {str(e)}\n\n建议使用通用搜索工具进行查询。"
            
            if self.enable_user_approval:
                return self._request_approval(f"AI news search: {topic}", _search_ai_news)
            else:
                return _search_ai_news()
        
        # Store all available tools
        all_tools = {
            "calculator": calculator,
            "get_current_time": get_current_time,
            "note_taker": note_taker,
            "get_notes": get_notes,
            "weather_info": weather_info,
            "random_fact": random_fact,
            "text_analyzer": text_analyzer,
            "file_operations": file_operations,
            "web_search": web_search,
            "ai_news_search": ai_news_search
        }
        
        # Add MCP tools
        mcp_tools = self._create_mcp_tools()
        all_tools.update(mcp_tools)
        
        # Return only enabled tools
        return [all_tools[tool_name] for tool_name in self.enabled_tools if tool_name in all_tools]
    
    def _create_mcp_tools(self):
        """Create tools from MCP server configurations"""
        mcp_tools = {}
        
        for mcp_config in self.mcp_servers:
            if not mcp_config.get('enabled', False):
                continue
                
            server_name = mcp_config.get('name', 'unknown')
            tools_config = mcp_config.get('tools', [])
            
            for tool_config in tools_config:
                tool_name = f"mcp_{server_name}_{tool_config['name']}"
                
                def create_mcp_tool(config, server):
                    @tool
                    def mcp_tool(input_data: str) -> str:
                        """MCP Tool: {config['name']} from {server}. {config.get('description', '')}"""
                        time.sleep(1.0)  # Simulate MCP call
                        if self.enable_user_approval:
                            return self._request_approval(
                                f"MCP Tool {config['name']}: {input_data}",
                                lambda: f"MCP {config['name']} executed with: {input_data} [Simulated MCP response]"
                            )
                        return f"MCP {config['name']} executed with: {input_data} [Simulated MCP response]"
                    
                    mcp_tool.__name__ = tool_name
                    return mcp_tool
                
                mcp_tools[tool_name] = create_mcp_tool(tool_config, server_name)
        
        return mcp_tools
    
    def _setup_agent(self):
        """Setup agent based on the selected type"""
        if not self.tools:
            # No tools - simple chat
            self._setup_simple_chat()
            return
        
        # Create system prompt
        system_message = self._create_system_prompt()
        
        if self.agent_type == "tool_calling":
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
            
        elif self.agent_type == "react":
            self.prompt = PromptTemplate.from_template(f"""
            {system_message}
            
            You have access to the following tools:
            {{tools}}
            
            Use the following format:
            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{{tool_names}}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question
            
            Previous conversation:
            {{chat_history}}
            
            Question: {{input}}
            Thought: {{agent_scratchpad}}
            """)
            self.agent = create_react_agent(self.llm, self.tools, self.prompt)
            
        elif self.agent_type == "structured_chat":
            # Use the same approach as tool_calling for better compatibility
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", system_message + "\n\nYou can use tools when needed or respond directly for simple conversations."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            # Use tool_calling agent instead of structured_chat for better reliability
            self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=True
        )
    
    def _setup_simple_chat(self):
        """Setup simple chat without tools"""
        system_message = self._create_system_prompt()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        
        from langchain_core.runnables import RunnableLambda
        
        def simple_chat(inputs):
            formatted_prompt = self.prompt.format_messages(
                chat_history=inputs.get("chat_history", []),
                input=inputs["input"]
            )
            response = self.llm.invoke(formatted_prompt)
            return {"output": response.content}
        
        self.agent_executor = RunnableLambda(simple_chat)
    
    def _create_system_prompt(self):
        """Create system prompt based on configuration"""
        if self.custom_prompt:
            return self.custom_prompt
        
        if not self.tools:
            return """You are a helpful AI assistant with memory. 
            You can remember our conversation and provide helpful responses based on our chat history.
            
            Note: You currently don't have access to any external tools, but you can still:
            - Remember our conversation history
            - Answer questions based on your knowledge
            - Provide helpful information and assistance
            
            Always be helpful and use your memory of our conversation when relevant."""
        
        # Create tool descriptions
        tool_descriptions = []
        for tool_func in self.tools:
            tool_descriptions.append(f"- {tool_func.name}: {tool_func.description}")
        
        tools_text = "\n".join(tool_descriptions)
        
        approval_note = ""
        if self.enable_user_approval:
            approval_note = """

IMPORTANT: When you use certain tools (calculator, file_operations, web_search), they require user approval.
When you call these tools, you will receive a message starting with "APPROVAL_REQUIRED:".
This means:
1. The action has been submitted for approval
2. You should inform the user that the action is waiting for their approval
3. DO NOT retry the same tool call again - it's already pending
4. Simply acknowledge the pending approval and tell the user to check the approval section

Example: If you receive "APPROVAL_REQUIRED: Calculate: 15 * 23 has been submitted for approval (ID: 1)..."
You should respond: "I've submitted the calculation 15 * 23 for your approval. Please check the approval section above to approve or deny this action."

NEVER call the same tool multiple times when you see APPROVAL_REQUIRED.
"""
        
        reasoning_note = ""
        if self.show_reasoning and self.agent_type == "react":
            reasoning_note = "\n\nPlease think step by step and show your reasoning process clearly."
        
        return f"""You are a helpful AI assistant with memory and access to tools. 
        You can remember our conversation and use tools to help answer questions.
        
        Available tools:
        {tools_text}
        
        Agent Type: {self.agent_type}
        {approval_note}
        {reasoning_note}
        
        Always be helpful and use your memory of our conversation when relevant. 
        When appropriate, use the available tools to provide better assistance."""
    
    def _safe_calculate(self, expression: str) -> str:
        """Safely calculate mathematical expressions"""
        try:
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return f"Calculation result: {result}"
            else:
                return "Error: Only basic mathematical operations are allowed"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def _safe_file_operation(self, operation: str, filename: str, content: str = "") -> str:
        """Safely perform real file operations with security restrictions"""
        try:
            # 安全限制：只允许在当前工作目录及其子目录中操作
            current_dir = pathlib.Path.cwd()
            file_path = pathlib.Path(filename).resolve()
            
            # 检查文件路径是否在安全范围内
            try:
                file_path.relative_to(current_dir)
            except ValueError:
                return f"Security error: File access outside current directory is not allowed: {filename}"
            
            if operation.lower() == "read":
                if not file_path.exists():
                    return f"File not found: {filename}"
                if not file_path.is_file():
                    return f"Path is not a file: {filename}"
                    
                # 读取文件（限制大小）
                file_size = file_path.stat().st_size
                if file_size > 1024 * 1024:  # 限制1MB
                    return f"File too large to read: {filename} ({file_size} bytes)"
                    
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                    
                return f"File content of {filename} ({len(file_content)} characters):\n\n{file_content}"
                
            elif operation.lower() == "write":
                # 写入文件
                if len(content) > 10 * 1024:  # 限制10KB
                    return f"Content too large to write: {len(content)} characters (limit: 10KB)"
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                return f"Successfully wrote {len(content)} characters to {filename}"
                
            elif operation.lower() == "list":
                # 列出目录内容
                if filename == "." or filename == "":
                    list_path = current_dir
                else:
                    list_path = file_path
                    
                if not list_path.exists():
                    return f"Directory not found: {filename}"
                if not list_path.is_dir():
                    return f"Path is not a directory: {filename}"
                
                items = []
                for item in list_path.iterdir():
                    if item.is_file():
                        size = item.stat().st_size
                        items.append(f"📄 {item.name} ({size} bytes)")
                    elif item.is_dir():
                        items.append(f"📁 {item.name}/")
                
                if not items:
                    return f"Directory is empty: {list_path}"
                    
                return f"Contents of {list_path}:\n" + "\n".join(sorted(items))
                
            elif operation.lower() == "append":
                # 追加到文件
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(content)
                return f"Successfully appended {len(content)} characters to {filename}"
                
            elif operation.lower() == "delete":
                # 删除文件
                if not file_path.exists():
                    return f"File not found: {filename}"
                file_path.unlink()
                return f"Successfully deleted: {filename}"
                
            else:
                return f"Unknown file operation: {operation}. Supported: read, write, list, append, delete"
                
        except PermissionError:
            return f"Permission denied: Cannot access {filename}"
        except FileNotFoundError:
            return f"File not found: {filename}"
        except UnicodeDecodeError:
            return f"Cannot read file: {filename} (encoding error - file may be binary)"
        except Exception as e:
            return f"File operation error: {str(e)}"
    
    def _request_approval(self, action_description: str, action_func):
        """请求用户审批敏感操作"""
        import time
        
        if 'pending_approvals' not in st.session_state:
            st.session_state.pending_approvals = []
        
        # 使用时间戳确保唯一ID
        approval_id = len(st.session_state.pending_approvals)
        timestamp = int(time.time() * 1000)  # 毫秒级时间戳
        
        approval = {
            'id': approval_id,
            'timestamp': timestamp,
            'description': action_description,
            'action': action_func,
            'status': 'pending'  # 确保初始状态为pending
        }
        st.session_state.pending_approvals.append(approval)
        
        # 详细调试信息：追踪审批请求创建过程
        print(f"🔍 DEBUG: 创建了新的审批请求 - ID: {approval_id}, 状态: {approval['status']}, 描述: {action_description}")
        print(f"🔍 DEBUG: 当前总审批数量: {len(st.session_state.pending_approvals)}")
        print(f"🔍 DEBUG: 创建前 has_new_approval 状态: {st.session_state.get('has_new_approval', False)}")
        print(f"🔍 DEBUG: 创建前 approval_ui_shown 状态: {st.session_state.get('approval_ui_shown', False)}")
        
        # 强制设置标志，确保UI能检测到
        st.session_state.has_new_approval = True
        st.session_state.force_approval_check = True  # 添加额外的强制检查标志
        
        print(f"🔍 DEBUG: 创建后设置 has_new_approval = True")
        print(f"🔍 DEBUG: 创建后设置 force_approval_check = True")
        
        # 这里不要调用st.rerun()，因为它会干扰当前的执行流程
        # 相反，返回一个提示信息，让用户知道有待审批操作
        
        return f"我已经提交了{action_description}以供批准。请检查上面的批准部分以批准或拒绝此操作。"
    
    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create session history"""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
    
    def chat_stream(self, message: str, session_id: str = "default", reasoning_container=None):
        """Send a message to the agent and get a streaming response"""
        if not self.api_available:
            yield "API not available. Please check your configuration."
            return
        
        try:
            # Setup callback handler for streaming
            callback_handler = None
            if reasoning_container and self.show_reasoning:
                callback_handler = StreamingCallbackHandler(reasoning_container)
            
            # Configure callbacks
            config = {"configurable": {"session_id": session_id}}
            if callback_handler:
                config["callbacks"] = [callback_handler]
            
            # For react agents, we need to handle streaming differently
            if self.agent_type == "react" and self.tools:
                # Use the custom wrapper that handles history conversion
                response = self.agent_with_chat_history.invoke(
                    {"input": message},
                    config=config,
                )
                
                # Simulate streaming by yielding character by character
                full_response = response["output"]
                for i, char in enumerate(full_response):
                    yield char
                    if i % 5 == 0:  # Add small delay every 5 characters
                        time.sleep(0.02)
            else:
                # For tool_calling and structured_chat agents, use standard approach
                # Always use the agent_with_chat_history to ensure proper history handling
                response = self.agent_with_chat_history.invoke(
                    {"input": message},
                    config=config,
                )
                
                # Simulate streaming by yielding character by character
                full_response = response["output"]
                for i, char in enumerate(full_response):
                    yield char
                    if i % 5 == 0:  # Add small delay every 5 characters
                        time.sleep(0.02)
                        
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def chat(self, message: str, session_id: str = "default") -> str:
        """Send a message to the agent and get a response (non-streaming)"""
        if not self.api_available:
            return "API not available. Please check your configuration."
        
        try:
            response = self.agent_with_chat_history.invoke(
                {"input": message},
                config={"configurable": {"session_id": session_id}},
            )
            return response["output"]
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_memory(self, session_id: str = "default"):
        """Clear conversation memory"""
        if session_id in self.store:
            self.store[session_id] = ChatMessageHistory()
    
    def get_memory_info(self, session_id: str = "default") -> dict:
        """Get memory information"""
        session_history = self._get_session_history(session_id)
        return {
            "message_count": len(session_history.messages),
            "messages": [msg.content for msg in session_history.messages[-10:]]
        }

def get_tool_info():
    """Get information about all available tools"""
    return {
        "calculator": {
            "name": "🧮 Calculator",
            "description": "Perform mathematical calculations",
            "example": "Calculate 15 * 23",
            "category": "Utility",
            "requires_approval": True
        },
        "get_current_time": {
            "name": "🕐 Current Time",
            "description": "Get current date and time",
            "example": "What time is it?",
            "category": "Information",
            "requires_approval": False
        },
        "note_taker": {
            "name": "📝 Note Taker",
            "description": "Save notes for later reference",
            "example": "Take a note: Buy groceries",
            "category": "Productivity",
            "requires_approval": False
        },
        "get_notes": {
            "name": "📋 Get Notes",
            "description": "Retrieve all saved notes",
            "example": "Show me my notes",
            "category": "Productivity",
            "requires_approval": False
        },
        "weather_info": {
            "name": "🌤️ Weather Info",
            "description": "Get real weather information using wttr.in",
            "example": "What's the weather in Tokyo?",
            "category": "Information",
            "requires_approval": False
        },
        "random_fact": {
            "name": "🎲 Random Fact",
            "description": "Get interesting random facts from online API",
            "example": "Tell me a random fact",
            "category": "Entertainment",
            "requires_approval": False
        },
        "text_analyzer": {
            "name": "📊 Text Analyzer",
            "description": "Analyze text statistics",
            "example": "Analyze this text: Hello world",
            "category": "Utility",
            "requires_approval": False
        },
        "file_operations": {
            "name": "📁 File Operations",
            "description": "Read, write, and list files",
            "example": "Read file: data.txt",
            "category": "System",
            "requires_approval": True
        },
        "web_search": {
            "name": "🔍 Web Search",
            "description": "Real web search using DuckDuckGo API",
            "example": "Search for: latest AI news",
            "category": "Information",
            "requires_approval": True
        },
        "ai_news_search": {
            "name": "🤖 AI News Search",
            "description": "Specialized search for AI and technology developments",
            "example": "Search for AI agent news",
            "category": "Information",
            "requires_approval": True
        }
    }

def get_agent_types():
    """Get available agent types"""
    return {
        "tool_calling": {
            "name": "🔧 Tool Calling Agent",
            "description": "Modern agent that can call tools directly",
            "best_for": "Most use cases, reliable tool usage",
            "supports_streaming": True
        },
        "react": {
            "name": "🤔 ReAct Agent",
            "description": "Reasoning and Acting agent with step-by-step thinking",
            "best_for": "Complex reasoning tasks, debugging",
            "supports_streaming": True
        },
        "structured_chat": {
            "name": "💬 Structured Chat Agent",
            "description": "Structured conversation agent with tool integration",
            "best_for": "Conversational interfaces, chat applications",
            "supports_streaming": True
        }
    }

def load_agent_presets():
    """Load predefined agent presets"""
    return {
        "general_assistant": {
            "name": "🤖 General Assistant",
            "description": "A helpful general-purpose assistant",
            "tools": ["calculator", "get_current_time", "note_taker", "get_notes", "text_analyzer"],
            "agent_type": "tool_calling",
            "prompt": None,
            "user_approval": False,
            "streaming": True,
            "show_reasoning": False
        },
        "research_agent": {
            "name": "🔬 Research Agent",
            "description": "Specialized for research and analysis",
            "tools": ["web_search", "text_analyzer", "note_taker", "get_notes"],
            "agent_type": "react",
            "prompt": "You are a research assistant specialized in gathering and analyzing information. Always think step by step and provide detailed analysis.",
            "user_approval": True,
            "streaming": True,
            "show_reasoning": True
        },
        "safe_assistant": {
            "name": "🛡️ Safe Assistant",
            "description": "Assistant with user approval for all actions",
            "tools": ["calculator", "get_current_time", "note_taker", "get_notes"],
            "agent_type": "tool_calling",
            "prompt": None,
            "user_approval": True,
            "streaming": True,
            "show_reasoning": False
        },
        "system_admin": {
            "name": "⚙️ System Admin",
            "description": "System administration assistant",
            "tools": ["file_operations", "calculator", "text_analyzer"],
            "agent_type": "structured_chat",
            "prompt": "You are a system administrator assistant. Always be cautious with file operations and explain what you're doing.",
            "user_approval": True,
            "streaming": True,
            "show_reasoning": True
        },
        "debug_agent": {
            "name": "🐛 Debug Agent",
            "description": "Agent with full reasoning visibility",
            "tools": ["calculator", "text_analyzer", "get_current_time"],
            "agent_type": "react",
            "prompt": "You are a debugging assistant. Show all your reasoning steps clearly.",
            "user_approval": False,
            "streaming": True,
            "show_reasoning": True
        }
    }

def main():
    st.title("🧠 Advanced LangChain Agent with Memory Demo")
    
    # 添加自定义CSS样式
    st.markdown("""
    <style>
    /* 审批按钮样式增强 */
    .stButton > button {
        transition: all 0.3s ease;
        border-radius: 8px;
        font-weight: 600;
        border: 2px solid transparent;
    }
    
    /* 同意按钮样式 */
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #4caf50, #45a049);
        border: 2px solid #4caf50;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #45a049, #4caf50);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
    }
    
    /* 拒绝按钮样式 */
    .stButton > button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #f44336, #e53935);
        color: white !important;
        border: 2px solid #f44336;
    }
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #e53935, #f44336);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(244, 67, 54, 0.4);
    }
    
    /* 审批卡片动画 */
    .approval-card {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .approval-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* 统计指标样式 */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
    }
    
    /* 脉冲动画 */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    /* 成功/警告消息样式增强 */
    .stSuccess {
        border-radius: 10px;
        border-left: 5px solid #4caf50;
    }
    
    .stWarning {
        border-radius: 10px;
        border-left: 5px solid #ff9800;
    }
    
    .stError {
        border-radius: 10px;
        border-left: 5px solid #f44336;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 Powered by OpenRouter - Advanced Agent Configuration with Streaming")
    st.markdown("---")
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Chat", 
        "🔧 Tools Configuration", 
        "🤖 Agent Configuration",
        "🔌 MCP Servers",
        "⚙️ Model Settings"
    ])
    
    with tab5:
        st.header("⚙️ Model & API Configuration")
        
        # Load from environment if available
        default_api_key = os.getenv("OPENAI_API_KEY", "")
        default_api_base = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # API Key input
            api_key = st.text_input(
                "OpenRouter API Key", 
                value=default_api_key,
                type="password",
                help="Get your API key from openrouter.ai",
                placeholder="sk-or-v1-..."
            )
            
            # API Base URL input (pre-filled with OpenRouter)
            api_base = st.text_input(
                "API Base URL",
                value=default_api_base,
                help="OpenRouter API endpoint"
            )
        
        with col2:
            # Model selection
            model_options = [
                "openai/gpt-3.5-turbo",
                "openai/gpt-4",
                "openai/gpt-4-turbo",
                "anthropic/claude-3-haiku",
                "anthropic/claude-3-sonnet",
                "google/gemini-pro",
                "meta-llama/llama-2-70b-chat",
                "mistralai/mistral-7b-instruct"
            ]
            
            selected_model = st.selectbox(
                "Select AI Model",
                model_options,
                index=0,
                help="Choose from various AI models available through OpenRouter"
            )
        
        # Streaming settings
        st.subheader("🌊 Streaming Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'enable_streaming' not in st.session_state:
                st.session_state.enable_streaming = True
            
            enable_streaming = st.checkbox(
                "Enable Streaming Response",
                value=st.session_state.enable_streaming,
                help="Stream responses in real-time for better user experience"
            )
            st.session_state.enable_streaming = enable_streaming
        
        with col2:
            if 'show_reasoning' not in st.session_state:
                st.session_state.show_reasoning = True
            
            show_reasoning = st.checkbox(
                "Show Agent Reasoning",
                value=st.session_state.show_reasoning,
                help="Display agent's thinking process and tool usage steps"
            )
            st.session_state.show_reasoning = show_reasoning
        
        # Instructions
        st.markdown("### 💡 Quick Setup")
        st.markdown("""
        **Get Started:**
        1. 🔑 Get API key from [openrouter.ai](https://openrouter.ai)
        2. 💰 Add credits to your account
        3. 🤖 Choose your preferred AI model
        4. 🌊 Configure streaming and reasoning display
        5. 🔧 Configure agent type and tools
        6. 🔌 Setup MCP servers (optional)
        7. 💬 Start chatting!
        """)
        
        # OpenRouter info
        with st.expander("ℹ️ About OpenRouter"):
            st.markdown("""
            **OpenRouter Benefits:**
            - Access to multiple AI models
            - Competitive pricing
            - No vendor lock-in
            - Unified API interface
            - Pay-per-use model
            """)
    
    with tab4:
        st.header("🔌 MCP (Model Context Protocol) Servers")
        st.markdown("Configure external MCP servers for additional capabilities")
        
        # Initialize MCP servers in session state
        if 'mcp_servers' not in st.session_state:
            st.session_state.mcp_servers = []
        
        # Add new MCP server
        with st.expander("➕ Add New MCP Server"):
            col1, col2 = st.columns(2)
            with col1:
                mcp_name = st.text_input("Server Name", placeholder="my-mcp-server")
                mcp_url = st.text_input("Server URL", placeholder="http://localhost:3000")
            with col2:
                mcp_description = st.text_area("Description", placeholder="What does this MCP server do?")
                mcp_enabled = st.checkbox("Enable by default", value=True)
            
            # Tools configuration
            st.markdown("**Tools Configuration:**")
            mcp_tools_json = st.text_area(
                "Tools (JSON format)",
                placeholder='''[
    {"name": "search", "description": "Search for information"},
    {"name": "analyze", "description": "Analyze data"}
]''',
                height=100
            )
            
            if st.button("Add MCP Server"):
                try:
                    tools_config = json.loads(mcp_tools_json) if mcp_tools_json else []
                    new_server = {
                        "name": mcp_name,
                        "url": mcp_url,
                        "description": mcp_description,
                        "enabled": mcp_enabled,
                        "tools": tools_config
                    }
                    st.session_state.mcp_servers.append(new_server)
                    st.success(f"Added MCP server: {mcp_name}")
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("Invalid JSON format for tools configuration")
        
        # Display existing MCP servers
        if st.session_state.mcp_servers:
            st.markdown("### Configured MCP Servers")
            for i, server in enumerate(st.session_state.mcp_servers):
                with st.expander(f"🔌 {server['name']} ({'✅ Enabled' if server['enabled'] else '❌ Disabled'})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**URL:** {server['url']}")
                        st.write(f"**Description:** {server['description']}")
                        st.write(f"**Tools:** {len(server['tools'])}")
                        for tool in server['tools']:
                            st.write(f"  - {tool['name']}: {tool.get('description', 'No description')}")
                    
                    with col2:
                        if st.button(f"{'Disable' if server['enabled'] else 'Enable'}", key=f"toggle_{i}"):
                            st.session_state.mcp_servers[i]['enabled'] = not server['enabled']
                            st.rerun()
                    
                    with col3:
                        if st.button("Remove", key=f"remove_{i}", type="secondary"):
                            st.session_state.mcp_servers.pop(i)
                            st.rerun()
        else:
            st.info("No MCP servers configured. Add one above to extend agent capabilities.")
        
        # MCP Info
        with st.expander("ℹ️ About MCP (Model Context Protocol)"):
            st.markdown("""
            **MCP allows you to:**
            - Connect to external services and APIs
            - Extend agent capabilities dynamically
            - Integrate with custom tools and workflows
            - Access real-time data sources
            
            **Note:** This is a demonstration. In a real implementation, MCP servers would provide actual connectivity to external services.
            """)
    
    with tab3:
        st.header("🤖 Agent Configuration")
        
        # Agent presets
        st.subheader("📋 Agent Presets")
        presets = load_agent_presets()
        
        col1, col2 = st.columns([1, 2])
        with col1:
            selected_preset = st.selectbox(
                "Choose a preset",
                ["custom"] + list(presets.keys()),
                format_func=lambda x: "🎨 Custom Configuration" if x == "custom" else presets[x]["name"]
            )
        
        with col2:
            if selected_preset != "custom":
                st.info(f"**{presets[selected_preset]['name']}**: {presets[selected_preset]['description']}")
                if st.button("Load Preset"):
                    preset = presets[selected_preset]
                    st.session_state.selected_agent_type = preset["agent_type"]
                    st.session_state.enabled_tools = preset["tools"]
                    st.session_state.custom_prompt = preset["prompt"]
                    st.session_state.enable_user_approval = preset["user_approval"]
                    st.session_state.enable_streaming = preset.get("streaming", True)
                    st.session_state.show_reasoning = preset.get("show_reasoning", False)
                    st.success(f"Loaded preset: {preset['name']}")
                    st.rerun()
        
        st.markdown("---")
        
        # Agent type selection
        st.subheader("🤖 Agent Type")
        agent_types = get_agent_types()
        
        if 'selected_agent_type' not in st.session_state:
            st.session_state.selected_agent_type = "tool_calling"
        
        selected_agent_type = st.selectbox(
            "Select Agent Type",
            list(agent_types.keys()),
            index=list(agent_types.keys()).index(st.session_state.selected_agent_type),
            format_func=lambda x: agent_types[x]["name"]
        )
        st.session_state.selected_agent_type = selected_agent_type
        
        st.info(f"**{agent_types[selected_agent_type]['name']}**: {agent_types[selected_agent_type]['description']}")
        st.caption(f"**Best for:** {agent_types[selected_agent_type]['best_for']}")
        
        if agent_types[selected_agent_type].get('supports_streaming', False):
            st.success("✅ This agent type supports streaming and reasoning display")
        
        # User approval settings
        st.subheader("🛡️ Security Settings")
        if 'enable_user_approval' not in st.session_state:
            st.session_state.enable_user_approval = False
        
        enable_user_approval = st.checkbox(
            "Enable User Approval for Sensitive Actions",
            value=st.session_state.enable_user_approval,
            help="Require manual approval before executing potentially sensitive operations"
        )
        st.session_state.enable_user_approval = enable_user_approval
        
        if enable_user_approval:
            st.warning("⚠️ User approval is enabled. Some actions will require manual confirmation.")
        
        # Custom prompt
        st.subheader("📝 Custom System Prompt")
        if 'custom_prompt' not in st.session_state:
            st.session_state.custom_prompt = ""
        
        custom_prompt = st.text_area(
            "Custom System Prompt (optional)",
            value=st.session_state.custom_prompt,
            placeholder="Enter a custom system prompt to override the default behavior...",
            height=150,
            help="Leave empty to use the default prompt based on selected tools and agent type"
        )
        st.session_state.custom_prompt = custom_prompt
        
        # Export/Import configuration
        st.subheader("💾 Configuration Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export Configuration"):
                config = {
                    "agent_type": st.session_state.selected_agent_type,
                    "enabled_tools": st.session_state.get('enabled_tools', []),
                    "custom_prompt": st.session_state.custom_prompt,
                    "enable_user_approval": st.session_state.enable_user_approval,
                    "enable_streaming": st.session_state.get('enable_streaming', True),
                    "show_reasoning": st.session_state.get('show_reasoning', False),
                    "mcp_servers": st.session_state.get('mcp_servers', [])
                }
                st.download_button(
                    "Download Config",
                    data=json.dumps(config, indent=2),
                    file_name="agent_config.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_config = st.file_uploader("📥 Import Configuration", type="json")
            if uploaded_config:
                try:
                    config = json.load(uploaded_config)
                    st.session_state.selected_agent_type = config.get("agent_type", "tool_calling")
                    st.session_state.enabled_tools = config.get("enabled_tools", [])
                    st.session_state.custom_prompt = config.get("custom_prompt", "")
                    st.session_state.enable_user_approval = config.get("enable_user_approval", False)
                    st.session_state.enable_streaming = config.get("enable_streaming", True)
                    st.session_state.show_reasoning = config.get("show_reasoning", False)
                    st.session_state.mcp_servers = config.get("mcp_servers", [])
                    st.success("Configuration imported successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing configuration: {str(e)}")
    
    with tab2:
        st.header("🔧 Tools Configuration")
        st.markdown("Select which tools the AI agent can use:")
        
        # Get tool information
        tool_info = get_tool_info()
        
        # Initialize enabled tools in session state
        if 'enabled_tools' not in st.session_state:
            st.session_state.enabled_tools = []
        
        # Group tools by category
        categories = {}
        for tool_id, info in tool_info.items():
            category = info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((tool_id, info))
        
        # Display tools by category
        for category, tools in categories.items():
            st.subheader(f"📁 {category}")
            
            cols = st.columns(2)
            for i, (tool_id, info) in enumerate(tools):
                with cols[i % 2]:
                    # Tool card
                    with st.container():
                        enabled = st.checkbox(
                            f"{info['name']}",
                            value=tool_id in st.session_state.enabled_tools,
                            key=f"tool_{tool_id}"
                        )
                        
                        if enabled and tool_id not in st.session_state.enabled_tools:
                            st.session_state.enabled_tools.append(tool_id)
                        elif not enabled and tool_id in st.session_state.enabled_tools:
                            st.session_state.enabled_tools.remove(tool_id)
                        
                        st.caption(info["description"])
                        if info.get("requires_approval", False):
                            st.caption("🛡️ Requires user approval when enabled")
                        st.code(info["example"], language=None)
        
        # Add MCP tools to the list
        if st.session_state.get('mcp_servers', []):
            st.subheader("📁 MCP Tools")
            for server in st.session_state.mcp_servers:
                if server['enabled']:
                    for tool in server['tools']:
                        tool_id = f"mcp_{server['name']}_{tool['name']}"
                        enabled = st.checkbox(
                            f"🔌 {tool['name']} (from {server['name']})",
                            value=tool_id in st.session_state.enabled_tools,
                            key=f"tool_{tool_id}"
                        )
                        
                        if enabled and tool_id not in st.session_state.enabled_tools:
                            st.session_state.enabled_tools.append(tool_id)
                        elif not enabled and tool_id in st.session_state.enabled_tools:
                            st.session_state.enabled_tools.remove(tool_id)
                        
                        st.caption(tool.get('description', 'MCP tool'))
        
        # Tool summary
        st.markdown("---")
        total_tools = len(tool_info) + sum(len(server['tools']) for server in st.session_state.get('mcp_servers', []) if server['enabled'])
        st.markdown(f"**Selected Tools:** {len(st.session_state.enabled_tools)} / {total_tools}")
        
        # Quick actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Enable All Tools"):
                all_tools = list(tool_info.keys())
                for server in st.session_state.get('mcp_servers', []):
                    if server['enabled']:
                        for tool in server['tools']:
                            all_tools.append(f"mcp_{server['name']}_{tool['name']}")
                st.session_state.enabled_tools = all_tools
                st.rerun()
        
        with col2:
            if st.button("❌ Disable All Tools"):
                st.session_state.enabled_tools = []
                st.rerun()
        
        with col3:
            if st.button("🔄 Reset to Default"):
                st.session_state.enabled_tools = []
                st.rerun()
    
    with tab1:
        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'agent' not in st.session_state:
            st.session_state.agent = None
        if 'current_model' not in st.session_state:
            st.session_state.current_model = None
        if 'current_tools' not in st.session_state:
            st.session_state.current_tools = None
        if 'current_agent_type' not in st.session_state:
            st.session_state.current_agent_type = None
        if 'current_prompt' not in st.session_state:
            st.session_state.current_prompt = None
        if 'current_approval' not in st.session_state:
            st.session_state.current_approval = None
        if 'current_streaming' not in st.session_state:
            st.session_state.current_streaming = None
        if 'current_reasoning' not in st.session_state:
            st.session_state.current_reasoning = None
        if 'enabled_tools' not in st.session_state:
            st.session_state.enabled_tools = []
        if 'pending_approvals' not in st.session_state:
            st.session_state.pending_approvals = []
        
        # Check if configuration changed
        config_changed = (
            st.session_state.current_tools != st.session_state.enabled_tools or
            st.session_state.current_model != selected_model or
            st.session_state.current_agent_type != st.session_state.selected_agent_type or
            st.session_state.current_prompt != st.session_state.custom_prompt or
            st.session_state.current_approval != st.session_state.enable_user_approval or
            st.session_state.current_streaming != st.session_state.enable_streaming or
            st.session_state.current_reasoning != st.session_state.show_reasoning
        )
        
        # Create agent if API key is provided or configuration changed
        if api_key and (not st.session_state.agent or config_changed):
            with st.spinner(f"🔄 Initializing {st.session_state.selected_agent_type} agent..."):
                try:
                    st.session_state.agent = AdvancedStreamlitMemoryAgent(
                        api_key=api_key,
                        api_base=api_base,
                        model=selected_model,
                        enabled_tools=st.session_state.enabled_tools,
                        agent_type=st.session_state.selected_agent_type,
                        custom_prompt=st.session_state.custom_prompt if st.session_state.custom_prompt else None,
                        enable_user_approval=st.session_state.enable_user_approval,
                        mcp_servers=st.session_state.get('mcp_servers', []),
                        enable_streaming=st.session_state.enable_streaming,
                        show_reasoning=st.session_state.show_reasoning
                    )
                    
                    # Update current state
                    st.session_state.current_model = selected_model
                    st.session_state.current_tools = st.session_state.enabled_tools.copy()
                    st.session_state.current_agent_type = st.session_state.selected_agent_type
                    st.session_state.current_prompt = st.session_state.custom_prompt
                    st.session_state.current_approval = st.session_state.enable_user_approval
                    st.session_state.current_streaming = st.session_state.enable_streaming
                    st.session_state.current_reasoning = st.session_state.show_reasoning
                    
                    if st.session_state.agent.api_available:
                        st.success(f"✅ Agent initialized successfully!")
                    else:
                        st.error("❌ Failed to initialize agent")
                except Exception as e:
                    st.error(f"❌ Error initializing agent: {str(e)}")
        
        # Display current configuration
        if st.session_state.agent and st.session_state.agent.api_available:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"🤖 **Model:** {selected_model}")
            with col2:
                st.info(f"🔧 **Agent:** {st.session_state.selected_agent_type}")
            with col3:
                st.info(f"🛠️ **Tools:** {len(st.session_state.enabled_tools)}")
            with col4:
                features = []
                if st.session_state.enable_streaming:
                    features.append("🌊 Stream")
                if st.session_state.show_reasoning:
                    features.append("🧠 Reason")
                st.info(f"**Features:** {' '.join(features) if features else 'Basic'}")
            
            # Show active tools and settings
            if st.session_state.enabled_tools:
                tool_info = get_tool_info()
                active_tool_names = []
                for tool_id in st.session_state.enabled_tools:
                    if tool_id in tool_info:
                        active_tool_names.append(tool_info[tool_id]["name"])
                    elif tool_id.startswith("mcp_"):
                        active_tool_names.append(f"🔌 {tool_id}")
                st.caption(f"**Active Tools:** {', '.join(active_tool_names)}")
            
            if st.session_state.enable_user_approval:
                st.caption("🛡️ **User approval enabled** for sensitive actions")
                
        # Main Chat Interface
        st.header("💬 Chat with AI Agent")
        
        # 首先检查并显示审批界面 - 放在聊天输入框前面确保用户能立即看到
        # 强制检查待审批操作 - 每次页面渲染都检查
        
        # 确保pending_approvals存在
        if 'pending_approvals' not in st.session_state:
            st.session_state.pending_approvals = []
        
        # 检查是否有新的审批请求 - 如果有，立即显示
        if st.session_state.get('has_new_approval', False):
            st.session_state.has_new_approval = False  # 重置标志
            st.rerun()  # 立即重新运行以显示新的审批请求
        
        # 额外的强制检查机制
        if st.session_state.get('force_approval_check', False):
            print(f"🔍 DEBUG: 检测到 force_approval_check 标志，强制检查审批状态")
            st.session_state.force_approval_check = False  # 重置标志
            if any(approval.get('status') == 'pending' for approval in st.session_state.pending_approvals):
                print(f"🔍 DEBUG: 发现待审批操作，强制刷新UI")
                st.rerun()
        
        # 调试信息 - 显示当前状态
        with st.expander("🔍 调试信息 - 审批状态", expanded=False):
            st.write(f"**用户审批启用状态:** {st.session_state.get('enable_user_approval', False)}")
            st.write(f"**待审批操作数量:** {len(st.session_state.pending_approvals)}")
            st.write(f"**启用的工具:** {st.session_state.get('enabled_tools', [])}")
            st.write(f"**has_new_approval 标志:** {st.session_state.get('has_new_approval', False)}")
            st.write(f"**force_approval_check 标志:** {st.session_state.get('force_approval_check', False)}")
            st.write(f"**approval_ui_shown 标志:** {st.session_state.get('approval_ui_shown', False)}")
            
            if st.session_state.pending_approvals:
                st.write("**待审批列表详情:**")
                pending_count_debug = 0
                for i, approval in enumerate(st.session_state.pending_approvals):
                    status = approval.get('status', 'N/A')
                    desc = approval.get('description', 'N/A')
                    if status == 'pending':
                        pending_count_debug += 1
                    st.write(f"  {i}: {desc} - 状态: {status}")
                st.write(f"**实际 pending 状态的操作数量:** {pending_count_debug}")
                
                # 添加清理按钮用于测试
                if st.button("🧹 清理所有审批记录（测试用）", key="debug_clear_all"):
                    st.session_state.pending_approvals = []
                    st.session_state.approval_ui_shown = False  # 重置UI标志
                    st.session_state.has_new_approval = False
                    st.session_state.force_approval_check = False
                    st.success("已清理所有审批记录")
                    st.rerun()
            else:
                st.write("**没有审批记录**")
                
        # 如果有新创建的审批且没有正在处理，立即强制刷新
        if (len(st.session_state.pending_approvals) > 0 and 
            any(approval.get('status') == 'pending' for approval in st.session_state.pending_approvals) and
            not st.session_state.get('approval_ui_shown', False)):
            st.session_state.approval_ui_shown = True
            st.info("🔄 检测到新的审批请求，正在刷新界面...")
            time.sleep(0.1)  # 短暂延迟
            st.rerun()
        
        # 最终保障检查 - 如果有任何pending状态的审批，确保UI一定显示
        current_pending = sum(1 for approval in st.session_state.pending_approvals if approval.get('status') == 'pending')
        if current_pending > 0 and not st.session_state.get('approval_ui_shown', False):
            print(f"🔍 DEBUG: 最终保障检查 - 发现 {current_pending} 个待审批操作，强制显示UI")
            st.session_state.approval_ui_shown = True
            # 不调用rerun，让当前渲染周期显示审批界面
        
        # 检查是否有待审批的操作 - 总是检查，不依赖其他条件
        pending_count = 0
        if st.session_state.pending_approvals:
            pending_count = sum(1 for approval in st.session_state.pending_approvals if approval.get('status') == 'pending')
            
        # 调试：显示 pending_count 计算结果
        if st.session_state.pending_approvals:
            st.info(f"🔍 调试：计算出的 pending_count = {pending_count}")
        
        # 如果有任何待审批操作，立即显示审批界面
        if pending_count > 0:
            # 美化的审批界面
            # 顶部警告横幅
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, #ff6b6b, #ff8e8e);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                text-align: center;
                font-weight: bold;
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
            ">
                🚨 您有 {pending_count} 个操作需要审批 - 请及时处理
            </div>
            """, unsafe_allow_html=True)
            
            # 简洁的统计信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: rgba(255, 193, 7, 0.1); border-radius: 8px;">
                    <h3 style="margin: 0; color: #ff9800;">⏳ {pending_count}</h3>
                    <small>待审批</small>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                approved_count = sum(1 for approval in st.session_state.pending_approvals if approval['status'] == 'approved')
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: rgba(76, 175, 80, 0.1); border-radius: 8px;">
                    <h3 style="margin: 0; color: #4caf50;">✅ {approved_count}</h3>
                    <small>已同意</small>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                denied_count = sum(1 for approval in st.session_state.pending_approvals if approval['status'] == 'denied')
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: rgba(244, 67, 54, 0.1); border-radius: 8px;">
                    <h3 style="margin: 0; color: #f44336;">❌ {denied_count}</h3>
                    <small>已拒绝</small>
                </div>
                """, unsafe_allow_html=True)
            
            # 快速批量操作
            if pending_count > 1:
                st.markdown("### 🚀 快速操作")
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("✅ 全部同意", type="primary", use_container_width=True, key="approve_all"):
                        for approval in st.session_state.pending_approvals:
                            if approval['status'] == 'pending':
                                try:
                                    result = approval['action']()
                                    approval['status'] = 'approved'
                                    st.session_state.messages.append({
                                        "role": "assistant", 
                                        "content": f"✅ 操作已执行：{result}"
                                    })
                                except Exception as e:
                                    st.error(f"❌ 执行操作时出错：{str(e)}")
                        st.success("✅ 已同意所有待审批操作")
                        st.rerun()
                
                with col2:
                    if st.button("❌ 全部拒绝", use_container_width=True, key="deny_all"):
                        for approval in st.session_state.pending_approvals:
                            if approval['status'] == 'pending':
                                approval['status'] = 'denied'
                                st.session_state.messages.append({
                                    "role": "assistant", 
                                    "content": f"❌ 操作被拒绝：{approval['description']}"
                                })
                        st.warning("⚠️ 已拒绝所有待审批操作")
                        st.rerun()
                
                with col3:
                    if st.button("🧹 清理已处理", help="清理已同意或拒绝的审批记录", key="clear_processed"):
                        st.session_state.pending_approvals = [
                            approval for approval in st.session_state.pending_approvals 
                            if approval['status'] == 'pending'
                        ]
                        st.info("🧹 已清理处理完成的审批记录")
                        st.rerun()
            
            st.markdown("---")
            
            # 显示待审批操作
            pending_approvals = [approval for approval in st.session_state.pending_approvals if approval['status'] == 'pending']
            if pending_approvals:
                st.markdown("### 🔄 待审批操作")
                
                # 添加强制显示的提示
                st.info("💡 请点击下方的 ✅同意 或 ❌拒绝 按钮来处理待审批操作")
                
                for approval in pending_approvals:
                    # Create a card-like container for each approval
                    with st.container():
                        # 使用颜色编码的边框
                        st.markdown("""
                        <div style="
                            border: 2px solid #ffa726; 
                            border-radius: 10px; 
                            padding: 15px; 
                            margin: 10px 0;
                            background-color: rgba(255, 167, 38, 0.1);
                        ">
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**🔍 操作内容：** {approval['description']}")
                            st.caption(f"📋 审批 ID: #{approval['id']} | ⏰ 状态: 等待审批")
                            
                            # 添加风险等级判断
                            description = approval['description'].lower()
                            if 'calculate' in description or '计算' in description:
                                risk_level = "🟢 低风险"
                                risk_color = "#4caf50"
                                risk_desc = "计算操作，通常安全"
                            elif 'file' in description or '文件' in description:
                                risk_level = "🟡 中风险"  
                                risk_color = "#ff9800"
                                risk_desc = "文件操作，请确认路径和内容"
                            elif 'web' in description or 'search' in description or '搜索' in description:
                                risk_level = "🟡 中风险"
                                risk_color = "#ff9800" 
                                risk_desc = "网络搜索，请确认查询内容"
                            elif 'mcp' in description:
                                risk_level = "🟠 高风险"
                                risk_color = "#f44336"
                                risk_desc = "外部服务调用，请谨慎确认"
                            else:
                                risk_level = "⚪ 未知风险"
                                risk_color = "#9e9e9e"
                                risk_desc = "请仔细检查操作内容"
                            
                            st.markdown(f"""
                            <div style="
                                background-color: rgba(128, 128, 128, 0.1);
                                padding: 8px;
                                border-radius: 5px;
                                border-left: 4px solid {risk_color};
                                margin-top: 8px;
                            ">
                            <small><strong>{risk_level}</strong> - {risk_desc}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            # Create two columns for approve/deny buttons
                            btn_col1, btn_col2 = st.columns(2)
                            
                            with btn_col1:
                                # 确保按钮有唯一的key
                                approve_key = f"approve_{approval['id']}_{approval.get('timestamp', approval['id'])}"
                                if st.button(
                                    "✅ 同意", 
                                    key=approve_key, 
                                    type="primary", 
                                    use_container_width=True,
                                    help="点击同意执行此操作"
                                ):
                                    try:
                                        result = approval['action']()
                                        approval['status'] = 'approved'
                                        st.session_state.messages.append({
                                            "role": "assistant", 
                                            "content": f"✅ 操作已执行：{result}"
                                        })
                                        st.success(f"✅ 已同意并执行操作：{approval['description']}")
                                        # 仅在所有待审批操作都处理完成后才重置UI标志
                                        remaining_pending = sum(1 for a in st.session_state.pending_approvals if a.get('status') == 'pending' and a['id'] != approval['id'])
                                        if remaining_pending == 0:
                                            st.session_state.approval_ui_shown = False
                                        print(f"🔍 DEBUG: 审批 {approval['id']} 已同意，剩余待审批: {remaining_pending}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ 执行批准操作时出错：{str(e)}")
                            
                            with btn_col2:
                                # 确保按钮有唯一的key
                                deny_key = f"deny_{approval['id']}_{approval.get('timestamp', approval['id'])}"
                                if st.button(
                                    "❌ 拒绝", 
                                    key=deny_key, 
                                    type="secondary", 
                                    use_container_width=True,
                                    help="点击拒绝此操作"
                                ):
                                    approval['status'] = 'denied'
                                    st.session_state.messages.append({
                                        "role": "assistant", 
                                        "content": f"❌ 操作被拒绝：{approval['description']}"
                                    })
                                    st.warning(f"⚠️ 已拒绝操作：{approval['description']}")
                                    # 仅在所有待审批操作都处理完成后才重置UI标志
                                    remaining_pending = sum(1 for a in st.session_state.pending_approvals if a.get('status') == 'pending' and a['id'] != approval['id'])
                                    if remaining_pending == 0:
                                        st.session_state.approval_ui_shown = False
                                    print(f"🔍 DEBUG: 审批 {approval['id']} 已拒绝，剩余待审批: {remaining_pending}")
                                    st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            
            # 已处理操作 (可折叠显示)
            processed_approvals = [approval for approval in st.session_state.pending_approvals if approval['status'] != 'pending']
            if processed_approvals:
                with st.expander(f"📋 查看已处理操作 ({len(processed_approvals)} 个)", expanded=False):
                    for approval in processed_approvals:
                        # 根据状态设置颜色
                        if approval['status'] == 'approved':
                            border_color = "#4caf50"  # 绿色
                            bg_color = "rgba(76, 175, 80, 0.1)"
                            status_icon = "✅"
                            status_text = "已同意"
                        else:  # denied
                            border_color = "#f44336"  # 红色
                            bg_color = "rgba(244, 67, 54, 0.1)"
                            status_icon = "❌"
                            status_text = "已拒绝"
                        
                        st.markdown(f"""
                        <div style="
                            border: 2px solid {border_color}; 
                            border-radius: 10px; 
                            padding: 10px; 
                            margin: 5px 0;
                            background-color: {bg_color};
                        ">
                        <strong>{status_icon} 操作内容：</strong> {approval['description']}<br>
                        <small>📋 审批 ID: #{approval['id']} | 📊 状态: {status_text}</small>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.info(f"💡 共有 {pending_count} 个操作待审批，请及时处理")
            
        elif st.session_state.pending_approvals:
            # 如果有审批记录但没有待审批的，显示简短状态
            processed_count = len([a for a in st.session_state.pending_approvals if a['status'] != 'pending'])
            if processed_count > 0:
                st.success(f"✅ 所有操作已处理完成 (共处理 {processed_count} 个)")
                if st.button("🧹 清理审批历史", key="clear_all_history"):
                    st.session_state.pending_approvals = []
                    st.rerun()
        
        # 然后显示聊天界面
        st.markdown("### 💬 对话区域")
        
        # 聊天历史管理 - 实现折叠功能
        if st.session_state.messages:
            # 获取用户设置的显示数量，如果没有设置则默认为3
            if 'recent_messages_display' not in st.session_state:
                st.session_state.recent_messages_display = 3
            recent_messages_count = st.session_state.recent_messages_display
            total_messages = len(st.session_state.messages)
            
            # 检查是否临时展开所有对话
            if st.session_state.get('temp_expand_all', False):
                st.session_state.temp_expand_all = False  # 重置标志
                st.info("📖 临时展开显示所有历史对话")
                for i, message in enumerate(st.session_state.messages):
                    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
                        timestamp = f"#{i+1}"
                        st.caption(f"{timestamp} | {message['role'].title()}")
                        st.write(message["content"])
            elif total_messages > recent_messages_count:
                # 显示历史消息统计
                st.markdown(f"""
                <div style="
                    background: linear-gradient(90deg, #e3f2fd, #bbdefb);
                    padding: 10px;
                    border-radius: 8px;
                    margin: 10px 0;
                    text-align: center;
                    color: #1976d2;
                    font-weight: bold;
                ">
                    📚 共有 {total_messages} 条对话记录 | 显示最近 {recent_messages_count} 条
                </div>
                """, unsafe_allow_html=True)
                
                # 历史对话折叠区域
                older_messages = st.session_state.messages[:-recent_messages_count]
                if older_messages:
                    with st.expander(f"📜 查看历史对话 ({len(older_messages)} 条)", expanded=False):
                        for i, message in enumerate(older_messages):
                            with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
                                # 为历史消息添加时间戳或序号
                                timestamp = f"#{i+1}"
                                st.caption(f"{timestamp} | {message['role'].title()}")
                                st.write(message["content"])
                
                # 显示最近的消息
                st.markdown("#### 🕒 最近对话")
                recent_messages = st.session_state.messages[-recent_messages_count:]
                for i, message in enumerate(recent_messages):
                    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
                        st.write(message["content"])
            else:
                # 消息数量较少时，正常显示所有消息
                for i, message in enumerate(st.session_state.messages):
                    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
                        st.write(message["content"])
        
        # 聊天控制选项
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            if st.button("🧹 清理对话", help="清理所有聊天历史", key="clear_chat_history"):
                st.session_state.messages = []
                # 同时清理agent的记忆
                if st.session_state.agent:
                    st.session_state.agent.clear_memory("streamlit_session")
                st.success("✅ 对话历史已清理")
                st.rerun()
        
        with col3:
            # 显示对话统计
            if st.session_state.messages:
                message_count = len(st.session_state.messages)
                user_count = sum(1 for m in st.session_state.messages if m['role'] == 'user')
                assistant_count = sum(1 for m in st.session_state.messages if m['role'] == 'assistant')
                
                with st.popover("📊 对话统计"):
                    st.metric("总消息数", message_count)
                    st.metric("用户消息", user_count)
                    st.metric("AI回复", assistant_count)
                    
                    st.markdown("---")
                    st.markdown("**💬 聊天设置**")
                    
                    # 历史消息显示数量设置
                    if 'recent_messages_display' not in st.session_state:
                        st.session_state.recent_messages_display = 3
                    
                    new_count = st.selectbox(
                        "显示最近消息数量",
                        options=[1, 2, 3, 4, 5, 10],
                        index=[1, 2, 3, 4, 5, 10].index(st.session_state.recent_messages_display),
                        help="设置在主界面显示的最近消息数量"
                    )
                    
                    if new_count != st.session_state.recent_messages_display:
                        st.session_state.recent_messages_display = new_count
                        st.rerun()
                    
                    # 展开所有历史对话按钮
                    if st.button("📖 临时展开所有对话", key="temp_expand_all"):
                        st.session_state.temp_expand_all = True
                        st.rerun()
        
        # 聊天输入区域
        if prompt := st.chat_input("Ask me anything...", key="main_chat_input"):
            if not st.session_state.agent or not st.session_state.agent.api_available:
                st.error("❌ Please configure your OpenRouter API key first in the Model Settings tab.")
                return
                
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user", avatar="👤"):
                st.write(prompt)
            
            # 在执行前记录当前审批数量
            initial_approval_count = len(st.session_state.pending_approvals)
            
            # Display assistant response
            with st.chat_message("assistant", avatar="🤖"):
                response_container = st.empty()
                
                try:
                    if st.session_state.enable_streaming:
                        # Streaming response handling
                        full_response = ""
                        
                        if st.session_state.show_reasoning:
                            # Create reasoning container
                            reasoning_container = st.container()
                            with reasoning_container:
                                st.markdown("### 🧠 Agent Reasoning Process")
                                st.markdown("---")
                        else:
                            reasoning_container = None
                        
                        # Stream the response
                        for chunk in st.session_state.agent.chat_stream(
                            prompt, 
                            session_id="streamlit_session",
                            reasoning_container=reasoning_container
                        ):
                            full_response += chunk
                            # Update display with typing indicator
                            with response_container:
                                st.markdown(full_response + "▌")
                        
                        # Final response without cursor
                        with response_container:
                            st.markdown(full_response)
                        
                        # Add separator after reasoning if shown
                        if st.session_state.show_reasoning and reasoning_container:
                            with reasoning_container:
                                st.markdown("---")
                                st.markdown("### 💬 Final Response")
                        
                        # Add to chat history
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        
                    else:
                        # Non-streaming response
                        with st.spinner("🤔 Thinking..."):
                            response = st.session_state.agent.chat(prompt, session_id="streamlit_session")
                            with response_container:
                                st.markdown(response)
                            # Add to chat history
                            st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # 检查是否有新的审批请求被创建
                    final_approval_count = len(st.session_state.pending_approvals)
                    if final_approval_count > initial_approval_count:
                        # 有新的审批请求，立即设置标志并刷新
                        new_approvals = final_approval_count - initial_approval_count
                        print(f"🔍 DEBUG: 检测到 {new_approvals} 个新的审批请求")
                        print(f"🔍 DEBUG: 审批数量从 {initial_approval_count} 增加到 {final_approval_count}")
                        
                        # 设置多个标志确保检测成功
                        st.session_state.has_new_approval = True
                        st.session_state.force_approval_check = True
                        
                        # 显示提示信息
                        st.info("🔔 检测到新的审批请求！页面将自动刷新以显示审批界面...")
                        print(f"🔍 DEBUG: 已设置审批检测标志，准备刷新")
                        
                        # 立即刷新页面
                        st.rerun()
                        
                except Exception as e:
                    error_msg = f"❌ 处理请求时发生错误：{str(e)}"
                    with response_container:
                        st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🧠 Advanced LangChain Agent with Memory Demo | 
        🌊 Streaming & Reasoning Support |
        🚀 Powered by <a href='https://openrouter.ai' target='_blank'>OpenRouter</a> | 
        <a href='https://python.langchain.com/' target='_blank'>LangChain 0.3.x</a> | 
        Built with ❤️ using Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 