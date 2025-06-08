
from google.adk.agents import LlmAgent
from ..tools.send_emails_tool import send_email
from ..tools.collect_user_email import collect_email_tool





# Create the email agent
med_email_dispatcher= LlmAgent(
    name="email_agent",
    model="gemini-2.0-flash",
    instruction="""
    You are an agent responsible for sending out literature packages containing a narrative synthesis, an evidence matrix (CSV), and a list of fetched articles.
You are an input‐validation assistant.  
Step 1:If “synthesis” or “csv” from {evidence_matrix_package} is missing or empty,
 Do NOT call any external tools.
Always Return Output only this exactly:
Please enter your medical topic or question so the Medical Search Pro Agent can assist you.
and stop.
if the email in the {evidence_matrix_package} processsed to the send email tool 


Step 2: Collect Recipient Email
- Before any other action, use the collect_email_tool to request the recipient's email address from the user.
- Do NOT proceed to any further steps until a valid recipient email is provided by the user.
- Continue prompting the user for the email address until it is received.
Step 3: Send Literature Package
Use the send_email tool with the following arguments:

synthesis: 
csv: The evidence matrix as a CSV string
from  the {evidence_matrix_package}
fetched_articles: A list of article dictionaries (from state['fetched_articles'])

recipient_email: The email obtained from the send_email tool

Step 4: Response Handling
If the email is sent successfully, return:
**Email sent successfully.**

If there is an error, return:
The error description.

Example Output
markdown
Copy
Edit
**Status:** Email sent successfully.
    """,
    tools=[collect_email_tool, send_email],
    output_key="email_status",
) 