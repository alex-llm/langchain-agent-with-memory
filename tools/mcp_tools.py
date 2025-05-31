"""
MCP (Model Context Protocol) Tools Module

Provides support for integrating external MCP servers and their tools.
MCP tools allow extending the agent with external services and capabilities.

Features:
- Dynamic MCP server integration
- Tool discovery and registration
- Configuration-based tool creation
- Simulated MCP responses for testing
"""

import time
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool

from .registry import BaseToolModule, ToolConfig, ToolCategory


class MCPToolsModule(BaseToolModule):
    """Module for MCP (Model Context Protocol) tools"""
    
    def __init__(self, memory_manager=None, enable_user_approval=False, mcp_servers=None):
        super().__init__(memory_manager, enable_user_approval)
        self.mcp_servers = mcp_servers or []
        self._mcp_tools = {}
        self._initialize_mcp_tools()
    
    def _initialize_mcp_tools(self):
        """Initialize MCP tools from server configurations"""
        for server_config in self.mcp_servers:
            if not server_config.get('enabled', False):
                continue
            
            server_name = server_config.get('name', 'unknown')
            tools_config = server_config.get('tools', [])
            
            for tool_config in tools_config:
                tool_name = f"mcp_{server_name}_{tool_config['name']}"
                self._mcp_tools[tool_name] = {
                    'config': tool_config,
                    'server': server_name,
                    'server_config': server_config
                }
    
    def get_tools(self) -> List:
        """Get all MCP tools"""
        tools = []
        
        for tool_name, tool_info in self._mcp_tools.items():
            tool_instance = self._create_mcp_tool(tool_name, tool_info)
            if tool_instance:
                tools.append(tool_instance)
        
        return tools
    
    def get_tool_configs(self) -> Dict[str, ToolConfig]:
        """Get tool configurations for MCP tools"""
        configs = {}
        
        for tool_name, tool_info in self._mcp_tools.items():
            tool_config = tool_info['config']
            server_name = tool_info['server']
            
            configs[tool_name] = ToolConfig(
                name=tool_name,
                category=ToolCategory.MCP,
                description=f"MCP Tool: {tool_config.get('description', tool_config['name'])} (from {server_name})",
                requires_approval=tool_config.get('requires_approval', False),
                risk_level=tool_config.get('risk_level', 'low'),
                example_usage=tool_config.get('example', f"Use {tool_config['name']} from {server_name}"),
                parameters=tool_config.get('parameters', {}),
                tags=["mcp", "external", server_name] + tool_config.get('tags', [])
            )
        
        return configs
    
    def _create_mcp_tool(self, tool_name: str, tool_info: Dict[str, Any]):
        """Create a specific MCP tool"""
        tool_config = tool_info['config']
        server_name = tool_info['server']
        server_config = tool_info['server_config']
        
        # Get tool parameters schema
        parameters = tool_config.get('parameters', {})
        description = tool_config.get('description', f"{tool_config['name']} from {server_name}")
        
        # Create the actual tool function
        def create_tool_func():
            @tool
            def mcp_tool(input_data: str = "") -> str:
                """MCP Tool from external server"""
                
                def _execute_mcp_tool():
                    try:
                        # Simulate MCP communication delay
                        time.sleep(0.5)
                        
                        # In a real implementation, this would:
                        # 1. Connect to the MCP server
                        # 2. Send the tool request with parameters
                        # 3. Wait for response
                        # 4. Return the result
                        
                        # For now, return a simulated response
                        result = self._simulate_mcp_response(tool_config, server_config, input_data)
                        return result
                        
                    except Exception as e:
                        return f"❌ MCP Tool Error: {str(e)}"
                
                return self.request_approval(
                    f"MCP Tool {tool_config['name']} from {server_name}: {input_data}",
                    _execute_mcp_tool
                )
            
            # Set the tool name dynamically
            mcp_tool.__name__ = tool_name
            mcp_tool.name = tool_name
            return mcp_tool
        
        return create_tool_func()
    
    def _simulate_mcp_response(self, tool_config: Dict, server_config: Dict, input_data: str) -> str:
        """Simulate an MCP server response for testing purposes"""
        tool_name = tool_config['name']
        server_name = server_config['name']
        
        # Simulate different types of MCP tools
        if 'search' in tool_name.lower():
            return f"""🔍 MCP Search Results from {server_name}:

Query: {input_data}

📋 Simulated Results:
• Result 1: Information about {input_data} from external source
• Result 2: Related data from {server_name} server
• Result 3: Additional context and details

🔗 Source: {server_name} MCP Server
⚡ Response time: 0.5s
✅ Status: Success

[This is a simulated MCP response for testing purposes]"""
        
        elif 'file' in tool_name.lower() or 'read' in tool_name.lower():
            return f"""📄 MCP File Operation from {server_name}:

Operation: {tool_name}
Input: {input_data}

📊 Simulated File Content:
```
Sample file content from {server_name}
This would contain the actual file data
Retrieved via MCP protocol
```

💾 File Info:
• Size: 1.2 KB
• Type: text/plain
• Source: {server_name} MCP Server

[This is a simulated MCP response for testing purposes]"""
        
        elif 'api' in tool_name.lower() or 'call' in tool_name.lower():
            return f"""🔌 MCP API Call from {server_name}:

Endpoint: {tool_name}
Parameters: {input_data}

📡 Simulated API Response:
{{
  "status": "success",
  "data": {{
    "message": "API call successful",
    "input": "{input_data}",
    "server": "{server_name}",
    "timestamp": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
  }},
  "mcp_server": "{server_name}"
}}

✅ Status: 200 OK
⚡ Response time: 0.5s

[This is a simulated MCP response for testing purposes]"""
        
        elif 'database' in tool_name.lower() or 'db' in tool_name.lower():
            return f"""🗄️ MCP Database Query from {server_name}:

Query: {input_data}

📊 Simulated Query Results:
+-------+------------------+
| ID    | Data             |
+-------+------------------+
| 1     | Sample data 1    |
| 2     | Sample data 2    |
| 3     | Related to input |
+-------+------------------+

📈 Query Stats:
• Rows returned: 3
• Execution time: 0.05s
• Database: {server_name}

[This is a simulated MCP response for testing purposes]"""
        
        else:
            # Generic MCP tool response
            return f"""🛠️ MCP Tool Execution from {server_name}:

Tool: {tool_name}
Input: {input_data}

📤 Simulated Output:
Successfully executed {tool_name} with input: {input_data}

🔧 Tool Details:
• Server: {server_name}
• Protocol: MCP (Model Context Protocol)
• Status: Completed successfully
• Execution time: 0.5s

📋 Description: {tool_config.get('description', 'No description available')}

[This is a simulated MCP response for testing purposes]"""
    
    def add_mcp_server(self, server_config: Dict):
        """Add a new MCP server configuration"""
        self.mcp_servers.append(server_config)
        self._initialize_mcp_tools()
    
    def remove_mcp_server(self, server_name: str):
        """Remove an MCP server and its tools"""
        # Remove server from config
        self.mcp_servers = [s for s in self.mcp_servers if s.get('name') != server_name]
        
        # Remove tools from registry
        tools_to_remove = [
            tool_name for tool_name in self._mcp_tools.keys()
            if self._mcp_tools[tool_name]['server'] == server_name
        ]
        
        for tool_name in tools_to_remove:
            del self._mcp_tools[tool_name]
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get information about configured MCP servers"""
        info = {
            'total_servers': len(self.mcp_servers),
            'enabled_servers': len([s for s in self.mcp_servers if s.get('enabled', False)]),
            'total_tools': len(self._mcp_tools),
            'servers': []
        }
        
        for server in self.mcp_servers:
            server_tools = [
                tool_name for tool_name, tool_info in self._mcp_tools.items()
                if tool_info['server'] == server.get('name', 'unknown')
            ]
            
            info['servers'].append({
                'name': server.get('name', 'unknown'),
                'enabled': server.get('enabled', False),
                'url': server.get('url', 'N/A'),
                'description': server.get('description', 'No description'),
                'tools_count': len(server_tools),
                'tools': server_tools
            })
        
        return info


# Example MCP server configurations for reference
EXAMPLE_MCP_CONFIGS = [
    {
        "name": "filesystem",
        "enabled": True,
        "url": "mcp://localhost:8001",
        "description": "File system operations via MCP",
        "tools": [
            {
                "name": "read_file",
                "description": "Read file contents via MCP",
                "requires_approval": True,
                "risk_level": "medium",
                "parameters": {"path": "File path to read"},
                "tags": ["files", "read"]
            },
            {
                "name": "list_directory",
                "description": "List directory contents via MCP",
                "requires_approval": False,
                "risk_level": "low",
                "parameters": {"path": "Directory path to list"},
                "tags": ["files", "list"]
            }
        ]
    },
    {
        "name": "database",
        "enabled": False,
        "url": "mcp://localhost:8002",
        "description": "Database operations via MCP",
        "tools": [
            {
                "name": "query_database",
                "description": "Execute database queries via MCP",
                "requires_approval": True,
                "risk_level": "high",
                "parameters": {"query": "SQL query to execute"},
                "tags": ["database", "sql", "query"]
            },
            {
                "name": "get_schema",
                "description": "Get database schema information via MCP",
                "requires_approval": False,
                "risk_level": "low",
                "parameters": {},
                "tags": ["database", "schema", "info"]
            }
        ]
    },
    {
        "name": "external_api",
        "enabled": True,
        "url": "mcp://localhost:8003",
        "description": "External API access via MCP",
        "tools": [
            {
                "name": "api_call",
                "description": "Make external API calls via MCP",
                "requires_approval": True,
                "risk_level": "medium",
                "parameters": {
                    "endpoint": "API endpoint URL",
                    "method": "HTTP method",
                    "data": "Request data"
                },
                "tags": ["api", "external", "http"]
            }
        ]
    }
] 