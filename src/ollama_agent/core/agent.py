from mcp import ClientSession
from .ai_model_lib import AIModel
import json
import os
import dotenv

dotenv.load_dotenv()

class IntelligentAgent:
    printDebug:bool = os.getenv("DEBUG", "false").lower() == "true"  # Enable debug mode for detailed output

    def __init__(self, Big_model=None, Small_model=None, config_path=None, avaliable_functions=[], list_of_tools=None) -> None:
        # Load model configuration from JSON file
        self.model_config = self._load_model_config(config_path)
        
        # Use provided models or fall back to config defaults
        self.Big_model = Big_model or self.model_config['settings']['default_big_model']
        self.Small_model = Small_model or self.model_config['settings']['default_small_model']
        self.list_of_tools = list_of_tools  # This will be set later when tools are discovered
        self.additional_parameter = None
        
        self.avaliable_functions = avaliable_functions
        # Load model parameters from config
        self.big_model_params = self.model_config['models']['big']['parameters']
        self.small_model_params = self.model_config['models']['small']['parameters']

    @staticmethod
    def print_debug(isdebug: bool, message: str):
        """
        Print debug messages if debug mode is enabled.
        
        Args:
            message: The message to print
        """
        if isdebug:
            print(f"🔍 **Debug:** {message}")

    def _load_model_config(self, config_path=None) -> dict:
        """Load model configuration from JSON file"""
        if config_path is None:
            # Default path relative to this file
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model.json')
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback configuration if file doesn't exist
            return {
                'models': {
                    'big': {'parameters': {'temperature': 0.1, 'max_tokens': 1000}},
                    'small': {'parameters': {'temperature': 0.1, 'max_tokens': 500}}
                },
                'settings': {
                    'default_big_model': 'gemma3:12b',
                    'default_small_model': 'gemma3:1b'
                }
            }

    async def handle_user_query(self, user_query: str, mcp_session: ClientSession) -> str:
        """
        Handle user query by deciding whether to search the web or answer directly.
        
        Args:
            user_query: The query string from the user
            mcp_session: The MCP client session to use for tool calls
        
        Returns:
            The response string, either from tool call or direct answer
        """
        try:
            if AIModel.function_call_avaliablity(self.Big_model):
                # Use the AI model to process the query and decide on tool calls
                aimodel = AIModel(
                    model_name=self.Big_model, 
                    temperature=self.big_model_params.get('temperature', 0.1),
                    max_tokens=self.big_model_params.get('max_tokens', 1000),
                    system_instruction=f"""
                    You are an AI assistant that can answer queries and call external tools when needed.  

                    ⚡ Behavior:
                    - If the query is about current events, news, or recent data → call `google_search`.  
                    - If the query involves running commands, system checks, or file operations → call `execute_cli_command` or `list_directory`.  
                    - If the query can be answered with your own knowledge → respond directly in plain text.  

                    ⚡ Tool Usage:
                    - When calling a tool, reply ONLY with valid JSON (no extra text).  
                    - JSON format (no trailing commas):  
                    {{
                    "tool_name": "<tool_name>",
                    "args": {{
                        "<arg_name>": "<value>"
                    }}
                    }}

                    ⚡ Examples:
                    - "List files in current directory" → call `list_directory`  
                    - "Run python --version" → call `execute_cli_command`  
                    - "Check data folder" → call `list_directory` with path="data"  

                    IMPORTANT: Never mix natural language with JSON tool calls.
                    """,
                )
                aimodel_response = aimodel.chat(user_query)

                self.print_debug(self.printDebug, f"💬 **AI Model Response:**\n\n{aimodel_response}")
                
                # The response from chat() is already a parsed dictionary, not a JSON string
                if isinstance(aimodel_response, dict):
                    # Extract the actual content from the response
                    actual_content = aimodel_response.get('message', {}).get('content', '')
                    self.print_debug(self.printDebug, f"🔍 **Debug - Extracted Content:** {actual_content}")
                    
                    # Check for native function calls first
                    calltools = aimodel_response.get('message', {}).get('tool_calls', [])
                    
                    if calltools:
                        for tool in calltools:
                            self.print_debug(self.printDebug, f"🔧 **Available Tool:** {tool}")
                            tools_result = await self.handle_tool_call(tool['function']['name'], tool['function']['arguments'], mcp_session)
                        
                        self.print_debug(self.printDebug, f"🔧 **Tool Call Result:** {tools_result}")
                        return f"🔍 **Tool Call Result:**\n\n{tools_result}"
                else:
                    # If it's a string, try to parse it
                    try:
                        response_data = json.loads(aimodel_response)
                        actual_content = response_data.get('message', {}).get('content', aimodel_response)
                        self.print_debug(self.printDebug, f"🔍 **Debug - Extracted Content:** {actual_content}")
                    except json.JSONDecodeError:
                        actual_content = aimodel_response
                
                # Try to extract tool call from the content using JSON parsing
                extracted_json = self.handle_json_fields(actual_content)
                
                if extracted_json[0] is not None:  # Check if tool_name is not None
                    tool_name, args = extracted_json
                    print(f"**Executing Tool:** {tool_name} with args: {args}")
                    tool_result = await self.handle_tool_call(tool_name, args, mcp_session)

                    self.print_debug(self.printDebug, f"🔧 **Tool Call Result before processed:**\n\n{tool_result}")

                    # Process the tool result with the small model for better formatting
                    tool_result = self.small_model_handle_tool_response(tool_result, model=self.Small_model, userprompt=user_query)
                    return f"🔍 **Tool Call Result:**\n\n{tool_result}"
                else:
                    # Return the direct AI response if no tool call is needed
                    return f"💭 **Direct Response:**\n\n{actual_content}"
            else:
                # ...existing code for fallback path...
                aimodel = AIModel(
                    model_name=self.Big_model, 
                    temperature=self.big_model_params.get('temperature', 0.1),
                    max_tokens=self.big_model_params.get('max_tokens', 1000),
                    system_instruction=f"""
                    You are an AI assistant that can call external tools to answer queries. 
                    You CANNOT answer questions about current events or today's news using your own knowledge. 
                    Available tools: 
                    {self.list_of_tools} 

                    Rules: 
                    - If the user asks for recent info, trends, news, or data not in your knowledge, use google_search 
                    - If the user wants to execute CLI commands, run terminal commands, check system info, list files, or perform file operations, use execute_cli_command or list_directory 
                    - If you can answer directly with your knowledge, respond with plain text 
                    - When using tools, respond with JSON specifying the tool to call and arguments 
                    - JSON format (NO trailing commas): 
                    {{ 
                        "tool_name": "<tool_to_call>", 
                        "args": {{ 
                            "<arg_name>": "<value>" 
                        }} 
                    }} 

                    Examples: 
                    - "What is current weather" → use google_search with query="current weather"
                    - "List files in current directory" → use list_directory 
                    - "Run python --version" → use execute_cli_command 
                    - "Check what's in the data folder" → use list_directory with path="data" 
                    
                    IMPORTANT: Ensure valid JSON syntax - no trailing commas after the last property!
                    """,
                )
                aimodel_response = aimodel.chat(user_query)

                self.print_debug(self.printDebug, f"💬 **AI Model Response:**\n\n{aimodel_response}")
                
                # Handle the response based on its type
                if isinstance(aimodel_response, dict):
                    actual_content = aimodel_response.get('message', {}).get('content', '')
                    self.print_debug(self.printDebug, f"🔍 **Debug - Extracted Content:** {actual_content}")
                else:
                    try:
                        response_data = json.loads(aimodel_response)
                        actual_content = response_data.get('message', {}).get('content', aimodel_response)
                        self.print_debug(self.printDebug, f"🔍 **Debug - Extracted Content:** {actual_content}")
                    except json.JSONDecodeError:
                        actual_content = aimodel_response
                
                extracted_json = self.handle_json_fields(actual_content)
                
                if extracted_json[0] is not None:  # Check if tool_name is not None
                    tool_name, args = extracted_json
                    print(f"**Executing Tool:** {tool_name} with args: {args}")
                    tool_result = await self.handle_tool_call(tool_name, args, mcp_session)

                    self.print_debug(self.printDebug, f"🔧 **Tool Call Result before processed:**\n\n{tool_result}")

                    # Process the tool result with the small model for better formatting
                    tool_result = self.small_model_handle_tool_response(tool_result, model=self.Small_model, userprompt=user_query)
                    return f"🔍 **Tool Call Result:**\n\n{tool_result}"
                else:
                    # Return the direct AI response if no tool call is needed
                    return f"💭 **Direct Response:**\n\n{actual_content}"
            
        except Exception as e:
            return f"❌ **Error processing query:** {str(e)}"
    
    def small_model_handle_tool_response(self, tool_response: str, model: str = "", userprompt: str = "") -> str:
        """
        Handle user query using a smaller model for faster responses.
        
        Args:
            tool_response: The response string from the tool
            model: The model name to use for generating the response
        
        Returns:
            The response string, either from tool call or direct answer
        """
        model = model or self.Small_model
        if not model:
            return "No model specified for processing tool response."

        processed_prompt = tool_response + f"\n\n User Prompt: {userprompt}"
        self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Processed Prompt for Small Model:** {processed_prompt}")
        aimodel = AIModel(
            model_name=model,
            temperature=self.small_model_params.get('temperature', 0.1),
            max_tokens=self.small_model_params.get('max_tokens', 500),
            system_instruction=f"""
            You are a small AI assistant. Your job is to process the raw output returned by external tools and present it to the user in a clear, concise, and user-friendly way.

            Rules:
            - Always focus on answering the user’s original query directly and clearly.
            - Summarize or reformat the tool output so it is easy to understand.
            - Keep the answer concise and remove irrelevant or redundant details.
            - If the tool output contains unrelated information, ignore it unless it directly helps answer the query.
            - Use plain text, bullet points, or JSON if structured output is requested.
            - Never invent new information; stick strictly to the tool output.
            - Ensure tone is factual, neutral, and helpful.
            """
        )

        processed_response = aimodel.generate_response(tool_response)
        return processed_response

    def handle_json_fields(self, text: str) -> tuple:
        """
        Handle JSON data extracted from markdown or plain text.
        
        Args:
            text: The text that may contain JSON (either plain or in markdown code blocks)
            
        Returns:
            A tuple containing the tool name and arguments
        """
        import re
        
        self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Input text:** {text}")
        
        # First, try to find JSON directly in the text (without code blocks)
        # Look for JSON-like structure starting with { and ending with }
        json_pattern = r'\{[^{}]*"tool_name"[^{}]*\}'
        json_match = re.search(json_pattern, text, re.DOTALL)
        
        if json_match:
            json_text = json_match.group(0).strip()
            self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Found JSON with regex:** {json_text}")
        else:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            if (json_match):
                json_text = json_match.group(1).strip()
                self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Found JSON in code block:** {json_text}")
            else:
                # Try a more flexible approach - look for any content that starts with { and contains tool_name
                flexible_pattern = r'\{[^}]*"tool_name"[^}]*\}'
                flexible_match = re.search(flexible_pattern, text, re.DOTALL)
                
                if flexible_match:
                    json_text = flexible_match.group(0).strip()
                    self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Found JSON with flexible pattern:** {json_text}")
                else:
                    # Check if this looks like it's intended to contain JSON
                    has_json_markers = (
                        '```json' in text.lower() or 
                        '```' in text or
                        ('{' in text and '"tool_name"' in text)
                    )
                    
                    self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Has JSON markers:** {has_json_markers}")
                    
                    if not has_json_markers:
                        # This is likely a plain text response, not intended as JSON
                        self.print_debug(isdebug=self.printDebug, message="🔍 **Debug - No JSON markers found, treating as plain text**")
                        return None, {}
                    else:
                        # No JSON structure found despite markers
                        self.print_debug(isdebug=self.printDebug, message="🔍 **Debug - JSON markers found but no valid JSON structure**")
                        return None, {}
        
        # Clean up common JSON formatting issues
        json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas before closing braces
        json_text = re.sub(r',\s*]', ']', json_text)  # Remove trailing commas before closing brackets
        
        self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Cleaned JSON text:** {json_text}")
        
        try:
            # Parse the JSON string
            extracted_json: dict = json.loads(json_text)
            
            # Extract fields
            tool_name = extracted_json.get("tool_name")
            args = extracted_json.get("args", {})
            
            self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Extracted tool_name:** {tool_name}")
            self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Extracted args:** {args}")
            
            return tool_name, args
        except json.JSONDecodeError as e:
            # Handle invalid JSON - try to be more forgiving
            self.print_debug(isdebug=self.printDebug, message=f"Error decoding JSON: {e}")
            self.print_debug(isdebug=self.printDebug, message=f"Attempted to parse: {json_text[:100]}...")
            
            # Try to extract tool_name and args with regex as fallback
            try:
                tool_match = re.search(r'"tool_name"\s*:\s*"([^"]+)"', text)
                query_match = re.search(r'"query"\s*:\s*"([^"]+)"', text)
                
                if tool_match:
                    tool_name = tool_match.group(1)
                    args = {}
                    if query_match:
                        args["query"] = query_match.group(1)
                    
                    self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Fallback extraction - tool_name:** {tool_name}")
                    self.print_debug(isdebug=self.printDebug, message=f"🔍 **Debug - Fallback extraction - args:** {args}")
                    
                    return tool_name, args
            except Exception as fallback_error:
                self.print_debug(isdebug=self.printDebug, message=f"Fallback parsing also failed: {fallback_error}")
            
            return None, {}

    
    async def handle_tool_call(self, tool_name: str, args: dict, mcp_session: ClientSession) -> str:
        """
        Handle tool calls based on the tool name and arguments.
        
        Args:
            tool_name: The name of the tool to call
            args: Dictionary of arguments for the tool
            
        Returns:
            Result of the tool call as a string
        """
        if not tool_name or not isinstance(args, dict):
            return "Invalid tool name or arguments."

        result = await mcp_session.call_tool(tool_name, args)

        if result is not None:
            # Extract text content properly from MCP response
            if hasattr(result, 'content') and result.content:
                # Extract text from content list
                text_parts = []
                for content_item in result.content:
                    # Check the type of content and handle accordingly
                    if hasattr(content_item, 'type'):
                        if content_item.type == 'text':
                            # Safely get text attribute only for text content
                            text_content = getattr(content_item, 'text', str(content_item))
                            text_parts.append(text_content)
                        elif content_item.type == 'image':
                            text_parts.append("[Image content]")
                        elif content_item.type == 'audio':
                            text_parts.append("[Audio content]")
                        elif content_item.type == 'resource':
                            text_parts.append(f"[Resource: {getattr(content_item, 'uri', 'Unknown')}]")
                        else:
                            # For any other content type, try to convert to string
                            text_parts.append(str(content_item))
                    else:
                        # Check if it's a text content type by checking the class name
                        content_type_name = type(content_item).__name__
                        if content_type_name == 'TextContent':
                            # Safely get text attribute only for TextContent objects
                            text_content = getattr(content_item, 'text', str(content_item))
                            text_parts.append(text_content)
                        else:
                            # For non-text content types, provide appropriate representation
                            if 'Image' in content_type_name:
                                text_parts.append("[Image content]")
                            elif 'Audio' in content_type_name:
                                text_parts.append("[Audio content]")
                            elif 'Resource' in content_type_name:
                                text_parts.append(f"[Resource: {getattr(content_item, 'uri', 'Unknown')}]")
                            else:
                                # Last resort: convert to string
                                text_parts.append(str(content_item))
                
                extracted_text = '\n'.join(text_parts) if text_parts else "No text content found"
                
                if extracted_text and extracted_text not in ["[]", "No results", ""]:
                    return extracted_text
            
            # Fallback: try to get structuredContent
            elif hasattr(result, 'structuredContent') and result.structuredContent:
                structured = result.structuredContent
                if isinstance(structured, dict) and 'result' in structured:
                    return structured['result']
            
            # Last resort: convert to string
            result_str = str(result)
            if result_str not in ["[]", "No results", ""]:
                return result_str
        
        return "🚫 No relevant results from tool call."