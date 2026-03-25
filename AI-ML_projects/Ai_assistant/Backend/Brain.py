import os
import sys
import json
import re
import hashlib
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

#-----------------------------Battery Automation-----------------------------
from Backend.BatteryAutomation import BatteryMonitor, BatteryVoiceCommands, BatteryEventResponses
from Backend.TTS import SpeakSeeu

#-----------------------------Internet Search-----------------------------
# Import Internet Search Engine
try:
    from Backend.InternetSearch import InternetSearchEngine
    INTERNET_SEARCH_AVAILABLE = True
except ImportError:
    INTERNET_SEARCH_AVAILABLE = False
    print("⚠️ InternetSearch module not available")

#-----------------------------Personal Information-----------------------------
# Import Personal Info Manager
try:
    from Backend.PersonalInfo import PersonalInfoManager
    PERSONAL_INFO_AVAILABLE = True
except ImportError:
    PERSONAL_INFO_AVAILABLE = False
    print("⚠️ PersonalInfo module not available")

#-----------------------------Task Automation-----------------------------
try:
    from Backend.TaskAutomation import TaskAutomation
    TASK_AUTOMATION_AVAILABLE = True
except ImportError:
    TASK_AUTOMATION_AVAILABLE = False
    print("Warning: TaskAutomation module not available")


#-----------------------------Screen Control-----------------------------
try:
    from Backend.ScreenControl import ScreenCommandProcessor, process_screen_command, is_screen_command
    SCREEN_CONTROL_AVAILABLE = True
except ImportError:
    SCREEN_CONTROL_AVAILABLE = False
    print("⚠️ ScreenControl module not available")


battery_monitor = BatteryMonitor()
battery_commands = BatteryVoiceCommands(battery_monitor)


def setup_battery_alerts():
    battery_monitor.register_callback(
        'on_charger_connected',
        lambda p: SpeakSeeu(f"Charger connected. System is now charging. Battery at {p}%.")
    )
    battery_monitor.register_callback(
        'on_charger_disconnected',
        lambda p: SpeakSeeu(f"Charger disconnected. Running on battery power. Battery at {p}%.")
    )
    battery_monitor.register_callback(
        'on_battery_low',
        lambda p: SpeakSeeu(f"Battery low warning! Battery at {p}%. Please connect the charger soon.")
    )
    battery_monitor.register_callback(
        'on_battery_critical',
        lambda p: SpeakSeeu(f"Critical battery warning! Only {p}% remaining. Connect charger immediately!")
    )
    battery_monitor.register_callback(
        'on_battery_full',
        lambda p: SpeakSeeu(f"Battery fully charged at {p}%. You can disconnect the charger now.")
    )

    # Start monitoring (checks every 5 seconds)
    battery_monitor.start_monitoring(check_interval=5)

# Call this during SEEU initialization
setup_battery_alerts()

# -----------------------------------------------------------------------
# Fix paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
backend_dir = current_dir if os.path.basename(current_dir) == 'Backend' else os.path.join(parent_dir, 'Backend')

for path in [parent_dir, backend_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import
SeeuAI = None
try:
    from Automation import SeeuAI, Coder
    print("✅ Automation imported")
except ImportError as e:
    print(f"❌ Import failed: {e}")

# Load env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
USERNAME = os.getenv("USERNAME", "User")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

class SEEUDatabase:
    """JSON-based database for SEEU"""

    def __init__(self, db_path: str = 'Database/SEEU.json'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        self.data = self._load_database()
        self._init_database()

    def _load_database(self):
        """Load database from JSON file"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading database: {e}. Creating new database.")
                return self._create_empty_database()
        return self._create_empty_database()

    def _create_empty_database(self):
        """Create empty database structure"""
        return {
            'conversations': [],
            'long_term_memory': [],
            'user_preferences': [],
            'sessions': [],
            'response_cache': [],
            'metadata': {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
        }

    def _save_database(self):
        """Save database to JSON file"""
        try:
            self.data['metadata']['last_modified'] = datetime.now().isoformat()

            temp_path = self.db_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)

            if os.path.exists(self.db_path):
                os.replace(temp_path, self.db_path)
            else:
                os.rename(temp_path, self.db_path)
            return True
        except Exception as e:
            print(f"❌ Error saving database: {e}")
            return False

    def _init_database(self):
        """Initialize database structure if needed"""
        required_tables = ['conversations', 'long_term_memory', 'user_preferences', 'sessions', 'response_cache']
        for table in required_tables:
            if table not in self.data:
                self.data[table] = []

        if 'metadata' not in self.data:
            self.data['metadata'] = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }

        self._save_database()

    def _get_next_id(self, table_name: str) -> int:
        """Get next available ID for a table"""
        if not self.data[table_name]:
            return 1
        return max(item.get('id', 0) for item in self.data[table_name]) + 1

    def start_new_session(self):
        """Start a new conversation session"""
        session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:16]
        session = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'message_count': 0
        }
        self.data['sessions'].append(session)
        self._save_database()
        return session_id

    def end_session(self, session_id: str):
        """Mark a session as ended"""
        for session in self.data['sessions']:
            if session['session_id'] == session_id:
                session['end_time'] = datetime.now().isoformat()
                break
        self._save_database()

    def add_conversation_turn(self, user_message: str, assistant_response: str = None,
                             session_id: str = None, category: str = None) -> int:
        """Add a conversation turn to the database"""
        conversation_id = self._get_next_id('conversations')
        conversation = {
            'id': conversation_id,
            'user_message': user_message,
            'assistant_response': assistant_response,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'category': category
        }
        self.data['conversations'].append(conversation)

        # Update session message count
        if session_id:
            for session in self.data['sessions']:
                if session['session_id'] == session_id:
                    session['message_count'] = session.get('message_count', 0) + 1
                    break

        self._save_database()
        return conversation_id

    def update_assistant_response(self, conversation_id: int, assistant_response: str):
        """Update the assistant's response for a conversation"""
        for conv in self.data['conversations']:
            if conv['id'] == conversation_id:
                conv['assistant_response'] = assistant_response
                break
        self._save_database()

    def get_recent_conversation(self, limit: int = 10, session_id: str = None):
        """Get recent conversation with optional session filter"""
        conversations = self.data['conversations']

        if session_id:
            conversations = [c for c in conversations if c.get('session_id') == session_id]

        # Sort by timestamp (most recent last)
        sorted_convs = sorted(
            conversations,
            key=lambda x: x.get('timestamp', ''),
            reverse=False
        )

        # Get last N conversations
        recent = sorted_convs[-limit:] if len(sorted_convs) > limit else sorted_convs

        # Format for AI
        formatted = []
        for conv in recent:
            if conv.get('user_message'):
                formatted.append({
                    "role": "user",
                    "content": conv['user_message']
                })
            if conv.get('assistant_response'):
                formatted.append({
                    "role": "assistant",
                    "content": conv['assistant_response']
                })

        return formatted

    def add_memory(self, memory_type: str, content: str, importance: int = 3,
                   tags: list = None, metadata: dict = None):
        """Add a memory to long-term storage"""
        memory_id = self._get_next_id('long_term_memory')
        memory = {
            'id': memory_id,
            'type': memory_type,
            'content': content,
            'importance': importance,
            'tags': tags or [],
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'access_count': 0
        }
        self.data['long_term_memory'].append(memory)
        self._save_database()
        return memory_id

    def get_relevant_memories(self, query: str, limit: int = 3):
        """Get memories relevant to the query"""
        memories = self.data.get('long_term_memory', [])
        if not memories:
            return []

        # Simple keyword matching
        query_words = set(query.lower().split())
        scored_memories = []

        for memory in memories:
            content = memory.get('content', '').lower()
            tags = [tag.lower() for tag in memory.get('tags', [])]

            # Score based on keyword matches
            content_words = set(content.split())
            tag_words = set(tags)

            content_matches = len(query_words & content_words)
            tag_matches = len(query_words & tag_words)

            score = content_matches * 2 + tag_matches * 3 + memory.get('importance', 0)

            if score > 0:
                scored_memories.append((score, memory))

        # Sort by score and return top N
        scored_memories.sort(reverse=True, key=lambda x: x[0])
        return [mem for score, mem in scored_memories[:limit]]

    def get_important_memories(self, limit: int = 10):
        """Get most important memories"""
        memories = self.data.get('long_term_memory', [])
        sorted_memories = sorted(
            memories,
            key=lambda x: x.get('importance', 0),
            reverse=True
        )
        return sorted_memories[:limit]

    def search_conversations(self, keyword: str):
        """Search conversations by keyword"""
        results = []
        for conv in self.data['conversations']:
            if keyword.lower() in conv.get('user_message', '').lower() or \
               keyword.lower() in conv.get('assistant_response', '').lower():
                results.append(conv)
        return results

    def cleanup_old_data(self, days_to_keep: int = 60):
        """Clean up old conversations and memories"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_iso = cutoff_date.isoformat()

        # Clean old conversations
        self.data['conversations'] = [
            conv for conv in self.data['conversations']
            if conv.get('timestamp', '') > cutoff_iso
        ]

        # Clean low-importance memories
        self.data['long_term_memory'] = [
            mem for mem in self.data['long_term_memory']
            if mem.get('importance', 0) >= 3 or mem.get('created_at', '') > cutoff_iso
        ]

        self._save_database()
        return True


class SEEUAssistant:
    """Enhanced SEEU Assistant with Internet Search, Memory, and Task Execution"""

    def __init__(self):
        self.db = SEEUDatabase()
        self.current_session = self.db.start_new_session()
        self.user_name = "Naru"
        self.battery_monitor = battery_monitor
        self.battery_commands = battery_commands

        # Initialize Internet Search Engine
        if INTERNET_SEARCH_AVAILABLE:
            self.search_engine = InternetSearchEngine()
            print("✅ Internet Search Engine initialized")
        else:
            self.search_engine = None
            print("⚠️ Internet Search Engine not available")

        # Initialize Personal Info Manager
        if PERSONAL_INFO_AVAILABLE:
            self.personal_info = PersonalInfoManager()
            print("✅ Personal Info Manager initialized")
        else:
            self.personal_info = None
            print("⚠️ Personal Info Manager not available")

        if SeeuAI:
            self.automation = SeeuAI()
            print("✅ Automation engine loaded")
        else:
            self.automation = None
            print("⚠️ Automation not available")

        # Initialize Task Automation (timer, files, apps, screenshot, etc.)
        if TASK_AUTOMATION_AVAILABLE:
            self.task_automation = TaskAutomation(speak_fn=SpeakSeeu)
            print("✅ Task Automation initialized")
        else:
            self.task_automation = None
            print("Warning: Task Automation not available")


                # Initialize Screen Controller
        if SCREEN_CONTROL_AVAILABLE:
            self.screen_control = ScreenCommandProcessor()
            print("✅ Screen Control initialized")
        else:
            self.screen_control = None
            print("⚠️ Screen Control not available")


        self.system_instructions = f"""You are SEEU, an advanced AI voice assistant created to help {self.user_name}.

Core capabilities:
1. Natural conversation with memory retention
2. Task execution (opening apps, controlling system)
3. Internet search for real-time information
4. Battery monitoring and system control
5. YouTube control and automation

IMPORTANT RESPONSE RULES:
- Keep responses concise and conversational
- For tasks/commands: Extract a command in format: COMMAND[action_here]
- For internet searches: Use SEARCH[query] format
- For conversations: Just respond naturally
- Always be helpful and friendly

Memory Guidelines:
- Remember user's name, preferences, and important information
- Learn from conversations to provide better assistance
- Reference past interactions when relevant

Examples:
User: "Play music on YouTube"
Response: "Playing music for you now. COMMAND[play music on youtube]"

User: "What's the weather in Mumbai?"
Response: "Let me check the weather for you. SEARCH[weather in Mumbai]"

User: "Who won the match today?"
Response: "Let me find that for you. SEARCH[who won the match today]"

User: "What's the latest news?"
Response: "Checking the latest news for you. SEARCH[latest news today]"

User: "Open calculator"
Response: "Opening calculator now. COMMAND[open calculator]"

User: "My name is Naru"
Response: "Nice to meet you, Naru! I'll remember that. MEMORY[User's name is Naru]"

Current session: {self.current_session}
Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        print(f"\n✅ SEEU Assistant initialized")
        print(f"👤 User: {self.user_name}")
        print(f"📁 Session: {self.current_session}")
        print(f"💾 Database: {self.db.db_path}")

        # Speak startup greeting + battery info (in a thread so it doesn't block init)
        import threading
        def _speak_startup():
            import time
            time.sleep(1)  # Small delay to let TTS engine fully load
            try:
                battery_msg = self.battery_monitor.get_battery_status_message()
                greeting = f"Hello {self.user_name}! I'm SEEU, your AI assistant.I'm At your Service Sir. {battery_msg}"
                print(f"🔊 Startup greeting: {greeting}")
                SpeakSeeu(greeting)
            except Exception as e:
                print(f"⚠️ Startup speech error: {e}")

        threading.Thread(target=_speak_startup, daemon=True).start()

    def _is_internet_search_query(self, user_input: str) -> bool:
        """
        Detect if the query requires internet search

        Returns:
            bool: True if query needs internet search
        """
        search_keywords = [
            # Weather
            'weather', 'temperature', 'forecast', 'climate', 'hot', 'cold', 'rain', 'sunny',
            # News
            'news', 'latest', 'breaking', 'today', 'headlines', 'current events',
            # Sports
            'match', 'game', 'score', 'won', 'lost', 'cricket', 'football', 'basketball',
            'ipl', 'nba', 'fifa', 'tournament', 'championship',
            # General current info
            'who is', 'what is', 'when is', 'where is', 'how is',
            'current', 'now', 'recent', 'update',
            # Stock and finance
            'stock', 'price', 'market', 'bitcoin', 'cryptocurrency',
            # Time-sensitive
            'happening', 'going on', 'trending',
        ]

        query_lower = user_input.lower()

        # Check for search keywords
        for keyword in search_keywords:
            if keyword in query_lower:
                return True

        # Check for question patterns
        question_patterns = [
            'what\'s', 'whats', 'who won', 'what happened',
            'tell me about', 'find out', 'search for',
            'look up', 'check', 'is there'
        ]

        for pattern in question_patterns:
            if pattern in query_lower:
                return True

        return False

    def _perform_internet_search(self, query: str) -> str:
        """
        Perform internet search and return formatted results

        Args:
            query: Search query

        Returns:
            Search results as string
        """
        if not self.search_engine or not self.search_engine.is_available():
            return "Internet search is not available. Please configure TAVILY_API_KEY in your .env file."

        try:
            print(f"🌐 Performing internet search: {query}")

            # Determine search type
            query_lower = query.lower()

            if any(word in query_lower for word in ['weather', 'temperature', 'forecast', 'climate']):
                # Extract location for weather search
                location_match = re.search(r'(?:weather|temperature|forecast|climate)\s+(?:in|at|for)\s+([a-zA-Z\s]+)', query_lower)
                if location_match:
                    location = location_match.group(1).strip()
                    result = self.search_engine.search_weather(location)
                else:
                    result = self.search_engine.search_general(query)

            elif any(word in query_lower for word in ['news', 'latest', 'breaking', 'headlines']):
                # News search
                result = self.search_engine.search_news(query)

            elif any(word in query_lower for word in ['match', 'game', 'score', 'won', 'cricket', 'football', 'ipl', 'nba']):
                # Sports search
                result = self.search_engine.search_sports(query)

            else:
                # General search
                result = self.search_engine.search_general(query)

            if result['success']:
                return result['response']
            else:
                return result.get('response', "I couldn't find information about that.")

        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            print(f"❌ {error_msg}")
            return f"I encountered an error while searching: {str(e)}"

    def extract_response_and_command(self, ai_output: str):
        """Extract conversational response and command from AI output"""
        # Check for COMMAND[...] pattern
        command_match = re.search(r'COMMAND\[(.*?)\]', ai_output, re.IGNORECASE)
        command = command_match.group(1).strip() if command_match else None

        # Check for SEARCH[...] pattern
        search_match = re.search(r'SEARCH\[(.*?)\]', ai_output, re.IGNORECASE)
        search_query = search_match.group(1).strip() if search_match else None

        # Remove COMMAND[...] and SEARCH[...] from response
        conversational_response = re.sub(r'COMMAND\[.*?\]', '', ai_output, flags=re.IGNORECASE)
        conversational_response = re.sub(r'SEARCH\[.*?\]', '', conversational_response, flags=re.IGNORECASE)
        conversational_response = conversational_response.strip()

        # If search query detected, perform search
        if search_query:
            search_results = self._perform_internet_search(search_query)
            conversational_response += f"\n\n{search_results}"

        return conversational_response, command

    def _extract_memory_from_response(self, ai_output: str):
        """Extract memories marked by AI"""
        memory_pattern = r'MEMORY\[(.*?)\]'
        memories = re.findall(memory_pattern, ai_output, re.IGNORECASE)
        return memories

    def _process_memories(self, memories: list, context: str):
        """Process and store extracted memories"""
        for memory_text in memories:
            # Determine memory type and importance
            memory_type = 'general'
            importance = 3

            if any(word in memory_text.lower() for word in ['name', 'called']):
                memory_type = 'personal'
                importance = 5
            elif any(word in memory_text.lower() for word in ['like', 'prefer', 'favorite']):
                memory_type = 'preference'
                importance = 4
            elif any(word in memory_text.lower() for word in ['remember', 'don\'t forget']):
                memory_type = 'task'
                importance = 4

            self.db.add_memory(
                memory_type=memory_type,
                content=memory_text,
                importance=importance,
                tags=[memory_type],
                metadata={'context': context}
            )
            print(f"💾 Stored memory: {memory_text[:50]}...")

    def _auto_extract_memories(self, user_input: str):
        """Automatically extract important information from user input"""
        # Name detection
        name_patterns = [
            r'my name is (\w+)',
            r'i am (\w+)',
            r'call me (\w+)',
            r'i\'m (\w+)'
        ]

        for pattern in name_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                name = match.group(1)
                self.db.add_memory(
                    memory_type='personal',
                    content=f"User's name is {name}",
                    importance=5,
                    tags=['name', 'personal']
                )
                self.user_name = name
                print(f"💾 Auto-stored: User name = {name}")

        # Preference detection
        preference_patterns = [
            r'i (like|love|prefer|enjoy) (.*)',
            r'my favorite (.*) is (.*)'
        ]

        for pattern in preference_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                preference = match.group(0)
                self.db.add_memory(
                    memory_type='preference',
                    content=preference,
                    importance=4,
                    tags=['preference', 'personal']
                )
                print(f"💾 Auto-stored preference: {preference[:50]}...")

    def execute_command(self, command: str) -> str:
        """Execute system commands using the automation engine"""
        if not self.automation:
            return "❌ Automation engine not available"

        try:
            print(f"\n🔧 Executing command: {command}")
            result = self.automation.run_task(command)
            return result
        except Exception as e:
            error = f"❌ Command execution error: {str(e)}"
            print('='*60)
            print(error)
            print('='*60 + '\n')
            return error

    def process_message(self, user_input: str) -> str:
        """Process message with memory, internet search, and learning capabilities"""


        # ============ SCREEN CONTROL CHECK ============
        # Intercept screen commands before AI processing
        if self.screen_control and is_screen_command(user_input):
            print("🖥️ Screen control command detected!")
            screen_response = self.screen_control.process_command(user_input)
            if screen_response:
                # Save to conversation history
                self.db.add_conversation_turn(
                    user_input,
                    assistant_response=screen_response,
                    session_id=self.current_session,
                    category="screen_control"
                )
                return screen_response  # EXIT EARLY
        # =============================================

        # ============ TASK AUTOMATION CHECK ============
        if hasattr(self, 'task_automation') and self.task_automation:
            task_result = self.task_automation.handle(user_input)
            if task_result:
                print(f"✅ TaskAutomation: {task_result[:60]}")
                self.db.add_conversation_turn(
                    user_input,
                    assistant_response=task_result,
                    session_id=self.current_session,
                    category="task_automation"
                )
                return task_result
        # ===============================================

        # ============ BATTERY CHECK FIRST ============
        # Intercept battery commands BEFORE AI processing
        if any(word in user_input.lower() for word in ['battery', 'charging', 'charge']):
            print("🔋 Battery command detected!")
            try:
                battery_response = self.battery_commands.process_command(user_input)
                if battery_response:
                    print(f"✅ Battery response: {battery_response}")

                    # Save to conversation history
                    conversation_id = self.db.add_conversation_turn(
                        user_input,
                        assistant_response=battery_response,
                        session_id=self.current_session,
                        category="battery_query"
                    )



                    return battery_response  # EXIT EARLY - Don't process with AI
            except Exception as e:
                print(f"❌ Battery error: {e}")
        # ============================================

        # ============ PERSONAL INFO CHECK ============
        # Check personal information BEFORE internet search
        # This prevents searching online for private data
        if self.personal_info:
            personal_answer = self.personal_info.search_personal_info(user_input)
            if personal_answer:
                print("🔒 Personal info query detected!")

                # Auto-extract memories
                self._auto_extract_memories(user_input)

                # Add conversation to database
                conversation_id = self.db.add_conversation_turn(
                    user_input,
                    assistant_response=personal_answer,
                    session_id=self.current_session,
                    category="personal_info"
                )

                # Update conversation in database
                self.db.update_assistant_response(conversation_id, personal_answer)

                # Don't speak here - SEEU.py will handle TTS

                return personal_answer  # EXIT EARLY - Don't search internet or process with AI
        # ============================================

        # ============ INTERNET SEARCH CHECK ============
        # Check if query needs internet search
        if self._is_internet_search_query(user_input):
            print("🌐 Internet search query detected!")

            # Auto-extract memories before search
            self._auto_extract_memories(user_input)

            # Add conversation to database
            conversation_id = self.db.add_conversation_turn(
                user_input,
                session_id=self.current_session,
                category="internet_search"
            )

            # Perform internet search
            search_response = self._perform_internet_search(user_input)

            # Update conversation in database
            self.db.update_assistant_response(conversation_id, search_response)

            # Don't speak here - SEEU.py will handle TTS
            # This prevents duplicate speaking

            return search_response  # EXIT EARLY - Don't process with AI
        # ============================================

        # Auto-extract memories from user input
        self._auto_extract_memories(user_input)

        # Add conversation to database
        conversation_id = self.db.add_conversation_turn(
            user_input,
            session_id=self.current_session,
            category="general"
        )

        try:
            # Get recent conversation history
            history = self.db.get_recent_conversation(limit=8, session_id=self.current_session)

            # Get relevant memories for this query
            relevant_memories = self.db.get_relevant_memories(user_input, limit=3)

            # Build enhanced system prompt with memories
            enhanced_system = self.system_instructions

            if relevant_memories:
                memory_context = "Relevant memories from previous conversations:"
                for memory in relevant_memories:
                    content = memory.get('content', '')
                    if content:
                        memory_context += f"\n- {content}"
                enhanced_system += f"\n\n{memory_context}"

            # Build messages
            messages = [
                {"role": "system", "content": enhanced_system}
            ]
            messages.extend(history)
            messages.append({"role": "user", "content": user_input})

            print(f"\n📤 User: {user_input}")
            if relevant_memories:
                print(f"📚 Retrieved {len(relevant_memories)} relevant memories")

            # Get response from Groq
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )

            ai_output = response.choices[0].message.content.strip()
            print(f"🤖 AI Output: {ai_output[:200]}...")

            # Extract response, command, and memories
            conversational_response, command = self.extract_response_and_command(ai_output)

            # Extract and process explicit memories from AI
            memories = self._extract_memory_from_response(ai_output)
            if memories:
                self._process_memories(memories, user_input)

            final_response = conversational_response

            # Execute command if present
            if command:
                print(f"🔍 Detected command: {command}")
                execution_result = self.execute_command(command)

                if "✅" in execution_result:
                    final_response += f"\n\n{execution_result}"
                elif "❌" in execution_result:
                    final_response += f"\n\nHmm, there was an issue: {execution_result}"

            print(f"📥 Final response: {final_response[:150]}...")

            # Update conversation in database
            self.db.update_assistant_response(conversation_id, final_response)

            # Store conversation as memory if important
            if any(word in user_input.lower() for word in ['remember', 'recall', 'don\'t forget', 'keep in mind']):
                self.db.add_memory(
                    memory_type='task',
                    content=f"User asked to remember: {user_input}",
                    importance=4
                )

            return final_response

        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            print(f"\n❌ {error_msg}\n")
            self.db.update_assistant_response(conversation_id, error_msg)
            return error_msg

    def get_summary(self):
        """Get a summary of what SEEU remembers"""
        important_memories = self.db.get_important_memories(limit=10)
        recent_conversations = self.db.get_recent_conversation(limit=5)

        summary = f"🧠 SEEU Memory Summary\n"
        summary += f"====================\n"
        summary += f"👤 User: {self.user_name}\n"
        summary += f"💾 Important Memories ({len(important_memories)}):\n"

        for memory in important_memories:
            content = memory.get('content', '')
            if content:
                summary += f"  • {content[:80]}...\n"

        return summary

    def search_messages(self, keyword: str):
        """Search for messages containing keyword"""
        return self.db.search_conversations(keyword)

    def export_chat_history(self, format_type: str = 'json'):
        """Export chat history"""
        conversations = self.db.data['conversations']

        if format_type == 'json':
            return json.dumps(conversations, indent=2, default=str)
        elif format_type == 'csv':
            import csv
            import io
            output = io.StringIO()
            if conversations:
                writer = csv.DictWriter(output, fieldnames=conversations[0].keys())
                writer.writeheader()
                writer.writerows(conversations)
            return output.getvalue()
        else:
            return None

    def cleanup(self):
        """Clean up old data and end session"""
        print("🧹 Cleaning up old data...")
        deleted_count = self.db.cleanup_old_data(days_to_keep=60)
        print(f"🗑️  Cleaned up {deleted_count} old records")

        self.db.end_session(self.current_session)
        print(f"📁 Session {self.current_session} ended")

        # Save database one last time
        self.db._save_database()
        print("💾 Database saved successfully")

def reset_database():
    """Reset the database to fix schema issues"""
    import os
    db_path = 'Database/SEEU.json'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️  Database reset. New database will be created on next run.")
    else:
        print("✅ Database file doesn't exist. It will be created on first run.")

if __name__ == "__main__":
    print("\n👁️ SEEU Brain - Conversational Mode with Memory & Internet Search (JSON-based)")
    print("="*60)
    print("Now remembers your name, preferences, and conversations!")
    print("Try: 'My name is John' or 'Remember that I like coffee'")
    print("Try: 'What's the weather in Mumbai?' or 'Who won the match?'")
    print("="*60)

    assistant = SEEUAssistant()

    print("\nType 'summary' to see memory, 'exit' to quit\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\n👋 Take care! I'll remember our conversation!")
            assistant.cleanup()
            break

        if user_input.lower() == 'summary':
            summary = assistant.get_summary()
            print(f"\n{summary}")
            continue

        response = assistant.process_message(user_input)
        print(f"\nSEEU: {response}\n")