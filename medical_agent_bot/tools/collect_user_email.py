from google.adk.tools import LongRunningFunctionTool, ToolContext

def collect_recipient_email(tool_context: ToolContext) -> dict:
    """
    Prompt the user to provide a recipient email address.

    This function is intended for human-in-the-loop workflows, where user input is required.
    It returns a pending status and a user-friendly prompt message.

    Args:
        tool_context (ToolContext): Contextual information from the agent runtime.

    Returns:
        dict: {
            'status': 'pending',
            'message': 'Please provide the recipient email address to proceed.'
        }
    """
    return {
        "status": "pending",
        "message": "Please provide the recipient email address to proceed."
    }

collect_email_tool = LongRunningFunctionTool(func=collect_recipient_email)
