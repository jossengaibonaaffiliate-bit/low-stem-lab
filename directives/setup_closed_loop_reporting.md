# Directive: ElevenLabs Post-Call Email Reporting (Serverless)

## Objective
Establish a zero-infrastructure, "Serverless" reporting system that sends a professional "Lead Dossier" straight to your email as soon as an ElevenLabs call ends using n8n.

## Workflow (100% in n8n)
1.  **Trigger (Webhook):** Receives the `post_call_transcription` event from ElevenLabs.
2.  **Action (Gmail/Email):** Formats and sends the lead details, summary, and transcript to your inbox.

## Batching Architecture (Store & Forward)
We will split this into two workflows to keep your data organized and your inbox clean.

1.  **Workflow 1 (Real-Time Logger):** 
    *   **Trigger:** ElevenLabs Webhook (Call Ends).
    *   **Action:** Analyzes the call -> Saves row to **Google Sheets**.
2.  **Workflow 2 (Daily Digest):** 
    *   **Trigger:** Schedule (e.g., 6:00 PM).
    *   **Action:** Reads all rows from today -> Sends **One Summary Email**.

## Setup Instructions

### Phase 1: The Database (Google Sheets)
1.  Create a new Google Sheet named `Pete Lead Database`.
2.  Create the following headers in Row 1:
    *   `Date`
    *   `Lead Name`
    *   `Phone`
    *   `Qualification Status`
    *   `Reason for Call`
    *   `Pain Points`
    *   `Proposed Solution`
    *   `Summary`

### Phase 2: The Logger (n8n)
1.  Import `pete_workflow_1_logging.json`.
2.  **Configure:**
    *   **ElevenLabs Webhook:** Add the URL to your ElevenLabs agent settings.
    *   **Google Sheets Node:** Select your new `Pete Lead Database` sheet.
    *   **Mapping:** Ensure the AI output maps to the correct Columns (A-H).

### Phase 3: The Digest (n8n)
1.  Import `pete_workflow_2_digest.json`.
2.  **Configure:**
    *   **Schedule Node:** Set your preferred time (default: 6 PM).
    *   **Google Sheets Node:** Select the same `Pete Lead Database`.
    *   **Email Node:** Confirm your email address.

This ensures you have a permanent Excel-style record of every lead, plus a clean daily executive summary.

