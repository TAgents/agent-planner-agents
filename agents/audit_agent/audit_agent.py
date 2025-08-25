
import os
import json

# Define a basic analysis function
def analyze_codebase_basic(directory_path):
    """
    Performs a basic text-based analysis of files in a directory.
    Note: This is a very limited analysis. A real audit agent would
    require understanding code structure, language specifics, and
    potentially integrate with static analysis tools.

    Args:
        directory_path (str): The path to the directory to analyze.

    Returns:
        dict: A dictionary containing basic findings.
    """
    findings = {
        "TODOs": [],
        "FIXMEs": [],
        " encontrados": [], # Example for demonstration
        "issues_found_count": 0
    }

    try:
        # Use search_files to find all python files (or other relevant types)
        # In a real scenario, you might want to configure file types or patterns
        search_results = default_api.search_files(path=directory_path, pattern=".*\.py$")
        
        files_to_analyze = []
        if search_results and search_results.get('search_files_response') and search_results['search_files_response'].get('content'):
             # Assuming the content is a list of file paths
             files_to_analyze = [item['text'] for item in search_results['search_files_response']['content']]


        if not files_to_analyze:
            return {"status": "No relevant files found for analysis."}

        # Read the content of the found files
        read_results = default_api.read_multiple_files(paths=files_to_analyze)

        if read_results and read_results.get('read_multiple_files_response') and read_results['read_multiple_files_response'].get('content'):
            for file_content_item in read_results['read_multiple_files_response']['content']:
                file_path = file_content_item.get('path', 'Unknown File')
                content = file_content_item.get('content', '')

                if content:
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        if "TODO" in line:
                            findings["TODOs"].append(f"{file_path}: Line {i+1} - {line.strip()}")
                            findings["issues_found_count"] += 1
                        if "FIXME" in line:
                            findings["FIXMEs"].append(f"{file_path}: Line {i+1} - {line.strip()}")
                            findings["issues_found_count"] += 1
                        # Add more basic checks here
                        if " print(" in line or " console.log(" in line: # Example: look for debug prints
                             findings[" encontrados"].append(f"{file_path}: Line {i+1} - {line.strip()}")
                             findings["issues_found_count"] += 1


    except Exception as e:
        return {"error": f"An error occurred during analysis: {e}"}

    return findings

# Example of how you might run this function (this part would likely be
# integrated into a larger agent execution framework)
if __name__ == "__main__":
    # Replace with the actual path you want to analyze
    target_directory = "/Users/michmalk/dev/talkingagents/agent-planner-agents"
    print(f"Starting basic analysis of: {target_directory}")
    analysis_results = analyze_codebase_basic(target_directory)
    print(json.dumps(analysis_results, indent=2))

