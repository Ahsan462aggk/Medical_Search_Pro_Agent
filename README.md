# MedicalSearch Pro Agent

## Overview
This agent-based system is designed to help users search for, analyze, and receive biomedical literature on specific medical topics. The system consists of multiple specialized agents working together in a workflow to process natural language queries, search PubMed Central, analyze results, and deliver findings via email.

## System Architecture

The system is composed of the following main components:

### 1. Query Ingestor Agent
**File:** `agent_module/sub_agents/query_ingestor_agent.py`

**Responsibilities:**
- Handles initial user interaction and query processing
- Validates and processes biomedical queries
- Enhances search terms with relevant synonyms and MeSH terms
- Initiates the literature search process

**Key Features:**
- Greeting and introduction responses
- Human-in-the-loop handling for additional information
- Biomedical query validation and enhancement

### 2. Evidence Builder Agent
**File:** `agent_module/sub_agents/evidence_builder_agent.py`

**Responsibilities:**
- Processes search results from PubMed
- Generates structured evidence matrices
- Creates narrative synthesis of findings
- Formats output for user presentation

**Key Features:**
- Structured data extraction
- Evidence matrix generation
- Narrative synthesis creation

### 3. Email Dispatcher Agent
**File:** `agent_module/sub_agents/email_dispatcher_agent.py`

**Responsibilities:**
- Manages email delivery of search results
- Handles recipient email collection
- Formats and sends comprehensive email reports
- Manages email delivery status

**Key Features:**
- Email template management
- Attachment handling
- Delivery status tracking

## Tools

### 1. PubMed Search Tool
**File:** `agent_module/tools/pubmed_tool.py`

**Functionality:**
- Interfaces with PubMed API
- Performs full-text searches
- Retrieves article metadata and abstracts

### 2. Email Sending Tool
**File:** `agent_module/tools/send_emails_tool.py`

**Functionality:**
- Sends HTML-formatted emails
- Handles file attachments
- Manages SMTP connections
- Formats article data for email display

## Workflow

1. **Query Processing**
   - User submits a medical query
   - Query Ingestor Agent validates and enhances the query
   - System checks for required additional information (e.g., email)

2. **Literature Search**
   - Enhanced query is used to search PubMed Central
   - Results are collected and processed

3. **Analysis & Synthesis**
   - Evidence Builder Agent structures the results
   - Narrative synthesis is generated
   - Evidence matrix is created

4. **Delivery**
   - Email Dispatcher Agent collects recipient email if not provided
   - Formatted results are sent via email
   - User receives comprehensive report with findings

## Setup and Installation

1. **Prerequisites**
   - Python 3.8+
   - Required Python packages (install via `pip install -r requirements.txt`)
   - PubMed API access (if required)
   - SMTP server credentials for email delivery

2. **Configuration**
   - Set up environment variables for API keys and credentials
   - Configure SMTP settings in the email tool
   - Adjust search parameters as needed

3. **Running the System**
   ```bash
   # Start the agent system
   python -m agent_module.agent
   ```

## Usage Examples

### Basic Search
```
User: Find recent studies on diabetes treatment
Agent: [Processes query and returns results]
```

### Email Delivery
```
User: Send me information about COVID-19 treatments to example@email.com
Agent: [Processes query and sends results to specified email]
```

## Error Handling

The system includes comprehensive error handling for:
- Invalid or ambiguous queries
- Missing or invalid email addresses
- API connection issues
- Search result processing errors

## Security Considerations

- API keys and credentials are stored as environment variables
- Email addresses are handled confidentially
- All external API calls use secure connections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request



## Contact

For any questions or support, please contact:

- **Name:** Ahsan Ali Gill  
- **Email:** [ahs462agk@gmail.com](mailto:ahs462agk@gmail.com)  
- **Phone:** +92 317 6346185  
- **Location:** Pakistan

