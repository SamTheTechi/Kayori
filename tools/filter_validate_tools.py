
# Filters a list of tools, returning only those with valid API keys.
def filter_valid_tools(tools: list):
    valid_tools = []
    for tool in tools:
        try:
            if hasattr(tool, 'check_api_key') and callable(tool.check_api_key):
                tool.check_api_key()
                valid_tools.append(tool)
            else:
                if hasattr(tool, 'api_key') and tool.api_key:
                    valid_tools.append(tool)
        except Exception as e:
            print(f"Skipping tool {tool.__class__.__name__}: {e}")
    return valid_tools
