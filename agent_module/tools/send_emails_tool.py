import os
import csv
import re
import smtplib
from typing import List, Dict, Union
from io import StringIO
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def generate_csv_string(data: Union[str, List[List], List[Dict]]) -> str:
    """
    Converts Markdown table, list of lists, or list of dicts to a CSV string.
    For Markdown, extracts URLs from links.
    """
    if not data:
        return "No data available"
    
    output = StringIO()

    # Handle Markdown table as string input
    if isinstance(data, str):
        lines = [line.strip() for line in data.strip().split('\n')]
        # Check for Markdown table format
        if lines and lines[0].startswith('|') and lines[0].endswith('|'):
            rows = []
            link_re = re.compile(r'\[.*?\]\((.*?)\)')
            for line in lines:
                if not (line.startswith('|') and line.endswith('|')):
                    continue
                # Skip separator lines
                cells = [cell.strip() for cell in line[1:-1].split('|')]
                if all(set(cell) <= set('-: ') for cell in cells if cell):
                    continue
                processed = [
                    (link_re.search(cell).group(1) if link_re.search(cell) else cell)
                    for cell in cells
                ]
                rows.append(processed)
            if rows:
                csv.writer(output, quoting=csv.QUOTE_ALL).writerows(rows)
                return output.getvalue()
        return data

    # Handle list of dicts
    if isinstance(data, list) and data and all(isinstance(row, dict) for row in data):
        # Gather unique headers in order of first appearance
        headers = []
        seen = set()
        for d in data:
            for key in d:
                if key not in seen:
                    headers.append(key)
                    seen.add(key)
        writer = csv.DictWriter(output, fieldnames=headers, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    # Handle list of lists/tuples
    if isinstance(data, list) and data and all(isinstance(row, (list, tuple)) for row in data):
        csv.writer(output, quoting=csv.QUOTE_ALL).writerows(data)
        return output.getvalue()

    # Fallback: write whatever was passed
    return str(data)

def build_articles_html(articles: List[dict]) -> str:
    """
    Build the HTML content for the articles section.
    """
    html = []
    # link_re removed as direct URLs are used from art.get('url')
    for idx, art in enumerate(articles):
        # Authors formatting
        authors_data = art.get('authors', 'Unknown') # Key changed to lowercase 'authors'
        authors_text = 'Unknown'
        if isinstance(authors_data, list):
            authors_text = ', '.join(str(author).strip() for author in authors_data if str(author).strip())
            if not authors_text: # Handle list of empty strings or only whitespace strings
                authors_text = 'Unknown'
        elif isinstance(authors_data, str) and authors_data.strip():
            authors_text = authors_data.strip()
        # Ensure authors_text defaults to 'Unknown' if not properly set above
        if not authors_text or authors_text.isspace():
             authors_text = 'Unknown'
        
        # Links formatting - Try 'links' key first, then 'url' key
        links_html_parts = []
        processed_urls = set()  # To avoid duplicate links

        # Check 'links' key (expected to be a list of markdown links)
        links_list_data = art.get('links', [])
        if isinstance(links_list_data, list):
            for item in links_list_data:
                if not isinstance(item, str):
                    continue
                # Handle markdown link format: [text](url)
                match = re.search(r'\[(.*?)\]\((https?://[^\s)]+)\)', item)
                if match:
                    link_text, url = match.groups()
                    if url not in processed_urls:
                        links_html_parts.append(f'<a href="{url}" target="_blank">{link_text}</a>')
                        processed_urls.add(url)
                # Also check if it's a plain URL
                elif item.startswith('http') and item not in processed_urls:
                    links_html_parts.append(f'<a href="{item}" target="_blank">{item}</a>')
                    processed_urls.add(item)
        
        # Check 'url' key (could be a single string or a list of markdown links)
        url_data = art.get('url')
        if isinstance(url_data, str):
            # Handle single markdown link
            match = re.search(r'\[(.*?)\]\((https?://[^\s)]+)\)', url_data)
            if match:
                link_text, url = match.groups()
                if url not in processed_urls:
                    links_html_parts.append(f'<a href="{url}" target="_blank">{link_text}</a>')
                    processed_urls.add(url)
            # Handle plain URL
            elif url_data.startswith('http') and url_data not in processed_urls:
                links_html_parts.append(f'<a href="{url_data}" target="_blank">{url_data}</a>')
                processed_urls.add(url_data)
        elif isinstance(url_data, list):
            for item in url_data:
                if not isinstance(item, str):
                    continue
                # Handle markdown link format
                match = re.search(r'\[(.*?)\]\((https?://[^\s)]+)\)', item)
                if match:
                    link_text, url = match.groups()
                    if url not in processed_urls:
                        links_html_parts.append(f'<a href="{url}" target="_blank">{link_text}</a>')
                        processed_urls.add(url)
                # Handle plain URL
                elif item.startswith('http') and item not in processed_urls:
                    links_html_parts.append(f'<a href="{item}" target="_blank">{item}</a>')
                    processed_urls.add(item)

        links_html_display = '<br>'.join(links_html_parts) if links_html_parts else 'No links available'

        html.append(f"""
        <div class="article">
            <h4>ARTICLE #{idx + 1}</h4>
            <div class="article-field"><strong>Title:</strong> {art.get('title', 'Untitled')}</div>
            <div class="article-field"><strong>Authors:</strong> {authors_text}</div>
            <div class="article-field"><strong>Journal:</strong> {art.get('journal', 'Not specified')}</div>
            <div class="article-field"><strong>Publication Date:</strong> {art.get('published_date', 'Not available')}</div>
            <div class="article-field"><strong>Summary:</strong>
                <div class="summary">{art.get('summary', 'No summary available')}</div>
            </div>
            <div class="article-links"><strong>Links:</strong><br>{links_html_display}</div>
        </div>
        """)
    return ''.join(html)

def send_email(
    synthesis: str,
    csv_data: str,  
    fetched_articles: list[dict],  
    recipient_email: str
) -> str:
    """
       1. synthesis: 
    2. csv: The evidence matrix/metrics as a CSV string
    3. fetched_articles: A list of article dictionaries
    4. recipient_email: The email address of the recipient from the collect_email_tool
    
    Your job:
    1. Compose an email that includes:
       - A heading/title
       - An "Articles" section that lists each article with its title, authors, journal, publication date, summary, and links
       from the fetched_articles list 
       - A "Synthesis" section that displays the synthesis text in a styled box
       - The evidence matrix attached as a CSV file
    2. Send the email using SMTP settings from environment variables:
       - SMTP_USER (required)
       - SMTP_PASSWORD (required)
       - SMTP_HOST (default: smtp.gmail.com)
       - SMTP_PORT (default: 587)
    3. Return "Email sent successfully." if the email is sent, otherwise return an error description.
    """
    # Load SMTP settings from environment
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

    if not SMTP_USER or not SMTP_PASSWORD:
        return "Error: SMTP_USER and SMTP_PASSWORD must be set in environment variables."

    # Prepare CSV
    final_csv = generate_csv_string(csv_data)
    if not final_csv or final_csv.strip() == "No data available":
        final_csv = None

    # Email headers
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    msg = MIMEMultipart()
    msg['Subject'] = f"Literature Package – {now} (UTC)"
    msg['From'] = SMTP_USER
    msg['To'] = recipient_email

    # Prepare synthesis: replace Markdown headings with HTML, relying on pre-wrap for other formatting
    synthesis_text = synthesis or "No synthesis provided."
    synthesis_lines = synthesis_text.splitlines()
    formatted_lines = []
    for line in synthesis_lines:
        if line.startswith('## '):
            formatted_lines.append(f"<h4>{line[3:]}</h4>")
        elif line.startswith('### '):
            formatted_lines.append(f"<h5>{line[4:]}</h5>")
        else:
            formatted_lines.append(line) # Keep other lines as is, pre-wrap will handle newlines
    formatted_synthesis = '\n'.join(formatted_lines)

    # Email HTML body
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h2 {{ color: #2c5282; margin-bottom: 20px; }}
            h3 {{ color: #2d3748; margin-top: 25px; }}
            .synthesis {{ background-color: #f7fafc; padding: 20px; border-radius: 5px; margin: 20px 0; white-space: pre-wrap; }}
            .article {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #4a5568; }}
            .article-field strong {{ color: #4a5568; }}
            .article-links {{ margin-top: 10px; }}
            .summary {{ background-color: #fff; padding: 10px; margin-top: 10px; border-left: 2px solid #718096; }}
        </style>
    </head>
    <body>
        <h2>Literature Package</h2>
        <h3>Articles</h3>
        {build_articles_html(fetched_articles)}
        <h3>Synthesis</h3>
        <div class="synthesis">{formatted_synthesis}</div>
        <p>See attachment for the structured evidence matrix.</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    # Attach CSV (if present)
    if final_csv:
        part = MIMEBase('text', 'csv')
        part.set_payload(final_csv.encode('utf-8'))
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename="evidence_matrix.csv")
        msg.attach(part)

    # Send via SMTP
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return "Email sent successfully."
    except Exception as e:
        return f"Error: {e}"
