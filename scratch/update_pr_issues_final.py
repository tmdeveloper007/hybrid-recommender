import subprocess
import json
import re

pr_numbers = [472, 470, 468, 466, 464, 462, 460, 458, 456, 454, 432, 431, 430, 429, 427, 426, 425, 424, 423, 422]
new_request = "**Assignment Request:**\nHey maintainer! Please assign this issue to me under GSSoC. I would love to work on this !"

issue_pattern = re.compile(r'(?:closes|fixes|resolves|refs)\s+#(\d+)', re.IGNORECASE)

for pr_num in pr_numbers:
    print(f"\nProcessing PR #{pr_num}...")
    try:
        # Get PR details
        get_cmd = ["gh", "api", f"repos/leonagoel/hybrid-recommender/pulls/{pr_num}"]
        res = subprocess.run(get_cmd, capture_output=True, text=True, check=True)
        pr_data = json.loads(res.stdout)
        
        pr_body = pr_data.get("body", "") or ""
        
        # Search for linked issue number
        matches = issue_pattern.findall(pr_body)
        if not matches:
            print(f"No linked issue found in body of PR #{pr_num}.")
            continue
            
        # Deduplicate and process issues
        issues_to_update = list(set(int(m) for m in matches))
        for issue_num in issues_to_update:
            print(f"Found linked Issue #{issue_num} for PR #{pr_num}.")
            try:
                # Fetch issue body
                get_issue_cmd = ["gh", "api", f"repos/leonagoel/hybrid-recommender/issues/{issue_num}"]
                issue_res = subprocess.run(get_issue_cmd, capture_output=True, text=True, check=True)
                issue_data = json.loads(issue_res.stdout)
                
                issue_body = issue_data.get("body", "") or ""
                
                # Split by '---' to completely remove any past versions of the assignment request block
                clean_body = issue_body.split("---")[0].strip()
                
                # Append final requested pattern
                updated_body = clean_body + f"\n\n---\n\n{new_request}"
                
                # Patch issue
                patch_cmd = [
                    "gh", "api", "-X", "PATCH", f"repos/leonagoel/hybrid-recommender/issues/{issue_num}",
                    "-f", f"body={updated_body}"
                ]
                subprocess.run(patch_cmd, capture_output=True, text=True, check=True)
                print(f"Successfully cleaned and updated Issue #{issue_num} with final format.")
            except Exception as ie:
                print(f"Error updating Issue #{issue_num}: {ie}")
    except Exception as e:
        print(f"Error processing PR #{pr_num}: {e}")
