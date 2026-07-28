"""
AI Foundry Chat Client

A command-line chat interface that connects to AI Foundry agents via MCP.
Supports continuous conversation with thread persistence.

Usage:
    python client.py --agent_name <agent_name>   # Specify agent name
"""

import sys
import os
import argparse
from typing import Optional

# Add the parent directory to the path to import ai_foundry_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai_foundry_agent import invoke_agent
except ImportError as e:
    print(f"❌ Error importing ai_foundry_agent: {e}")
    print("Make sure the ai_foundry_agent package is available")
    sys.exit(1)

class AIFoundryChat:
    """Chat interface for AI Foundry agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.thread_id: Optional[str] = None
        self.message_count = 0
        
    def send_message(self, user_message: str) -> dict:
        """Send a message to the AI Foundry agent"""
        try:
            # For the first message, we don't have a thread_id yet
            # For subsequent messages, we'll pass the existing thread_id to continue the conversation
            
            result = invoke_agent(self.agent_name, user_message, thread_id=self.thread_id)
            
            # Store the thread_id from the first response
            if self.thread_id is None:
                self.thread_id = result.get('thread_id')
                print(f"🔗 Started new conversation (Thread: {self.thread_id})")
            
            self.message_count += 1
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def display_response(self, result: dict):
        """Display the agent's response in a formatted way"""
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Display response messages
        for msg in result.get('response', []):
            role = msg.get('role', 'UNKNOWN')
            content = msg.get('content', '')
            
            if role == 'ASSISTANT':
                print(f"\n🤖 Assistant:")
                print(f"{content}")
            elif role == 'ERROR':
                print(f"\n❌ Error:")
                print(f"{content}")
            # We don't need to display USER messages as they're what the user just typed
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("=" * 60)
        print("🚀 AI Foundry Chat Interface")
        print("=" * 60)
        print(f"Agent: {self.agent_name}")
        print("Type 'exit', 'quit', or 'bye' to end the conversation")
        print("Type 'help' for available commands")
        print("-" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n💬 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    print("\n👋 Goodbye! Thanks for chatting!")
                    break
                
                # Check for help command
                if user_input.lower() in ['help', '?']:
                    self.show_help()
                    continue
                
                # Check for status command
                if user_input.lower() == 'status':
                    self.show_status()
                    continue
                
                # Skip empty messages
                if not user_input:
                    print("Please enter a message or type 'help' for commands.")
                    continue
                
                # Send message to agent
                print("🔄 Thinking...")
                result = self.send_message(user_input)
                
                # Display the response
                self.display_response(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 End of input. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("You can continue chatting or type 'exit' to quit.")
    
    def show_help(self):
        """Display help information"""
        print("\n📖 Available Commands:")
        print("  help, ?     - Show this help message")
        print("  status      - Show current chat status")
        print("  exit, quit  - End the chat session")
        print("  bye, q      - End the chat session")
        print("\n💡 Just type your message to chat with the AI agent!")
    
    def show_status(self):
        """Display current chat status"""
        print(f"\n📊 Chat Status:")
        print(f"  Agent: {self.agent_name}")
        print(f"  Thread ID: {self.thread_id or 'Not started'}")
        print(f"  Messages sent: {self.message_count}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AI Foundry Chat Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python client.py                               # Will prompt for agent name
  python client.py --agent_name <agent name>     # Use custom agent
        """
    )
    
    parser.add_argument(
        '--agent_name',
        type=str,
        help='Name of the AI Foundry agent to use (if not provided, you will be prompted)'
    )
    
    return parser.parse_args()

def get_agent_name_from_user():
    """Prompt the user to enter an agent name"""
    print("🤖 AI Foundry Chat Client")
    print("=" * 40)
    
    while True:
        try:
            agent_name = input("Enter the agent name: ").strip()
            
            if agent_name:
                return agent_name
            else:
                print("❌ Agent name cannot be empty. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

def main():
    """Main entry point for the chat client"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Get agent name from command line or prompt user
        if args.agent_name:
            agent_name = args.agent_name
        else:
            agent_name = get_agent_name_from_user()
        
        # Create and start the chat interface
        chat = AIFoundryChat(agent_name)
        chat.start_chat()
        
    except Exception as e:
        print(f"❌ Failed to start chat client: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()