"""
Basic Tools Module

Provides fundamental utility tools for LangChain agents:
- Calculator: Mathematical calculations with safety checks
- Time Tools: Current time and date information
- Text Analyzer: Text statistics and analysis
- Note Taking: Simple note management
"""

import datetime
import re
from typing import Dict, List
from langchain_core.tools import tool

from .registry import BaseToolModule, ToolConfig, ToolCategory


class BasicToolsModule(BaseToolModule):
    """Module containing basic utility tools"""
    
    def __init__(self, memory_manager=None, enable_user_approval=False):
        super().__init__(memory_manager, enable_user_approval)
        self._note_storage = []  # Simple in-memory note storage
    
    def get_tools(self) -> List:
        """Get all basic tools"""
        return [
            self._create_calculator_tool(),
            self._create_time_tool(),
            self._create_text_analyzer_tool(),
            self._create_note_taker_tool(),
            self._create_get_notes_tool()
        ]
    
    def get_tool_configs(self) -> Dict[str, ToolConfig]:
        """Get tool configurations for basic tools"""
        return {
            "calculator": ToolConfig(
                name="calculator",
                category=ToolCategory.UTILITY,
                description="Perform mathematical calculations",
                requires_approval=True,
                risk_level="medium",
                example_usage="Calculate 15 * 23",
                parameters={"expression": "Mathematical expression to evaluate"},
                tags=["math", "calculation", "arithmetic"]
            ),
            "get_current_time": ToolConfig(
                name="get_current_time",
                category=ToolCategory.INFORMATION,
                description="Get current date and time with timezone information",
                requires_approval=False,
                risk_level="low",
                example_usage="What time is it?",
                parameters={},
                tags=["time", "date", "timezone", "clock"]
            ),
            "text_analyzer": ToolConfig(
                name="text_analyzer",
                category=ToolCategory.UTILITY,
                description="Analyze text statistics including word count, readability, etc.",
                requires_approval=False,
                risk_level="low",
                example_usage="Analyze this text: Hello world",
                parameters={"text": "Text to analyze"},
                tags=["text", "analysis", "statistics", "readability"]
            ),
            "note_taker": ToolConfig(
                name="note_taker",
                category=ToolCategory.PRODUCTIVITY,
                description="Save notes with automatic timestamps",
                requires_approval=False,
                risk_level="low",
                example_usage="Take a note: Buy groceries",
                parameters={"note": "Content of the note to save"},
                tags=["notes", "productivity", "memory", "storage"]
            ),
            "get_notes": ToolConfig(
                name="get_notes",
                category=ToolCategory.PRODUCTIVITY,
                description="Retrieve all saved notes with timestamps and IDs",
                requires_approval=False,
                risk_level="low",
                example_usage="Show me my notes",
                parameters={},
                tags=["notes", "productivity", "retrieval", "list"]
            )
        }
    
    def _create_calculator_tool(self):
        """Create calculator tool with safety checks"""
        @tool
        def calculator(expression: str) -> str:
            """Calculate mathematical expressions. Input should be a valid mathematical expression."""
            def _safe_calculate():
                try:
                    # Basic safety check - only allow mathematical operations
                    allowed_chars = set('0123456789+-*/.() ')
                    if not all(c in allowed_chars for c in expression):
                        return "Error: Only basic mathematical operations are allowed (numbers, +, -, *, /, parentheses)"
                    
                    # Additional safety - check for dangerous patterns
                    dangerous_patterns = ['__', 'import', 'exec', 'eval', 'open', 'file']
                    expression_lower = expression.lower()
                    for pattern in dangerous_patterns:
                        if pattern in expression_lower:
                            return f"Error: Unsafe pattern detected: {pattern}"
                    
                    # Evaluate the expression
                    result = eval(expression)
                    return f"Calculation result: {result}"
                    
                except ZeroDivisionError:
                    return "Error: Division by zero"
                except SyntaxError:
                    return "Error: Invalid mathematical expression syntax"
                except Exception as e:
                    return f"Calculation error: {str(e)}"
            
            return self.request_approval(f"Calculate: {expression}", _safe_calculate)
        
        return calculator
    
    def _create_time_tool(self):
        """Create time information tool"""
        @tool
        def get_current_time() -> str:
            """Get the current date and time with timezone information."""
            try:
                now = datetime.datetime.now()
                return f"""Current time information:
• Local time: {now.strftime('%Y-%m-%d %H:%M:%S')}
• Day of week: {now.strftime('%A')}
• Month: {now.strftime('%B')}
• ISO format: {now.isoformat()}
• Unix timestamp: {int(now.timestamp())}
• Week number: {now.isocalendar()[1]}
• Day of year: {now.timetuple().tm_yday}"""
            except Exception as e:
                return f"Error getting time: {str(e)}"
        
        return get_current_time
    
    def _create_text_analyzer_tool(self):
        """Create text analysis tool"""
        @tool
        def text_analyzer(text: str) -> str:
            """Analyze text statistics including word count, character count, readability, and more."""
            try:
                if not text or not text.strip():
                    return "Error: Please provide text to analyze"
                
                # Basic statistics
                char_count = len(text)
                char_count_no_spaces = len(text.replace(' ', ''))
                word_count = len(text.split())
                
                # Sentence and paragraph counting
                sentences = re.split(r'[.!?]+', text)
                sentence_count = len([s for s in sentences if s.strip()])
                
                paragraphs = text.split('\n\n')
                paragraph_count = len([p for p in paragraphs if p.strip()])
                
                # Character composition analysis
                uppercase_count = sum(1 for c in text if c.isupper())
                lowercase_count = sum(1 for c in text if c.islower())
                digit_count = sum(1 for c in text if c.isdigit())
                punctuation_count = sum(1 for c in text if c in '.,!?;:')
                
                # Word frequency analysis (top 5 words)
                words = text.lower().split()
                word_freq = {}
                for word in words:
                    # Clean word of punctuation
                    clean_word = re.sub(r'[^\w]', '', word)
                    if clean_word and len(clean_word) > 2:  # Skip short words
                        word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
                
                top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
                
                # Averages
                avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
                avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
                
                # Simple readability score (Flesch Reading Ease approximation)
                if sentence_count > 0 and word_count > 0:
                    avg_sentence_len = word_count / sentence_count
                    avg_syllables = avg_word_length * 0.5  # Rough approximation
                    flesch_score = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables)
                    flesch_score = max(0, min(100, flesch_score))  # Clamp to 0-100
                    
                    if flesch_score >= 90:
                        readability = "Very Easy"
                    elif flesch_score >= 80:
                        readability = "Easy"
                    elif flesch_score >= 70:
                        readability = "Fairly Easy"
                    elif flesch_score >= 60:
                        readability = "Standard"
                    elif flesch_score >= 50:
                        readability = "Fairly Difficult"
                    elif flesch_score >= 30:
                        readability = "Difficult"
                    else:
                        readability = "Very Difficult"
                else:
                    flesch_score = 0
                    readability = "Unknown"
                
                # Format results
                result = f"""📊 Text Analysis Results:

📈 Basic Statistics:
• Characters: {char_count:,} (excluding spaces: {char_count_no_spaces:,})
• Words: {word_count:,}
• Sentences: {sentence_count:,}
• Paragraphs: {paragraph_count:,}

🔤 Character Composition:
• Uppercase letters: {uppercase_count:,}
• Lowercase letters: {lowercase_count:,}
• Digits: {digit_count:,}
• Punctuation marks: {punctuation_count:,}

📏 Averages:
• Average word length: {avg_word_length:.1f} characters
• Average sentence length: {avg_sentence_length:.1f} words

📖 Readability:
• Flesch Reading Ease: {flesch_score:.1f}
• Readability level: {readability}"""
                
                if top_words:
                    result += f"\n\n🏆 Most Frequent Words:\n"
                    for i, (word, count) in enumerate(top_words, 1):
                        result += f"• {i}. '{word}' ({count} times)\n"
                
                return result
                
            except Exception as e:
                return f"Error analyzing text: {str(e)}"
        
        return text_analyzer
    
    def _create_note_taker_tool(self):
        """Create note taking tool"""
        @tool
        def note_taker(note: str) -> str:
            """Save a note with automatic timestamp and ID for later reference."""
            try:
                if not note or not note.strip():
                    return "Error: Please provide note content to save"
                
                # Create note with metadata
                timestamp = datetime.datetime.now()
                note_entry = {
                    'id': len(self._note_storage) + 1,
                    'content': note.strip(),
                    'timestamp': timestamp,
                    'created': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                self._note_storage.append(note_entry)
                
                return f"✅ Note #{note_entry['id']} saved at {note_entry['created']}\n📝 Content: {note[:100]}{'...' if len(note) > 100 else ''}"
                
            except Exception as e:
                return f"Error saving note: {str(e)}"
        
        return note_taker
    
    def _create_get_notes_tool(self):
        """Create note retrieval tool"""
        @tool
        def get_notes() -> str:
            """Retrieve all saved notes with timestamps and IDs."""
            try:
                if not self._note_storage:
                    return "📝 No notes saved yet. Use the note_taker tool to save some notes!"
                
                result = f"📋 Your Saved Notes ({len(self._note_storage)} total):\n\n"
                
                # Show notes in reverse chronological order (newest first)
                for note in reversed(self._note_storage):
                    result += f"#{note['id']} [{note['created']}]\n"
                    result += f"📝 {note['content']}\n\n"
                
                return result
                
            except Exception as e:
                return f"Error retrieving notes: {str(e)}"
        
        return get_notes 