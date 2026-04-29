# Help Request Data

This folder contains help desk ticket data for training and testing the DCI AI triage assistant.

## Files

### historical_data.json

**Purpose:** Training data for the AI triage system to learn historical ticket classifications and resolutions.

**Structure:**
```json
{
  "request": "Subject and description of the help request",
  "resolution": "Routing category: Data Patch, Engineering Ticket, Field Support, or Needs Human Review",
  "what_we_did": "The specific action taken to resolve the ticket",
  "what_we_think_should_have_been_done": "Notes on misrouting or process improvements, if applicable"
}
```

**Usage:**
- Use this data to train or fine-tune your AI model to understand ticket patterns
- Analyze resolution patterns to improve classification accuracy
- Build few-shot prompts with relevant examples
- Test classification logic against known resolutions

**Data Notes:**
- Contains 50 real-world help desk tickets from a technology support system
- All personally identifiable information (PII) has been replaced with Marvel character names and example data for privacy
- Resolution categories are actual support workflow outcomes (Content Update, Certificate Merge, Exam Error, etc.)

### sample_requests.json

Example help requests for testing the triage API during the hackathon.

### RAW-help-desk-tickets.csv

Original source data exported from the help desk system. Contains full ticket metadata with redacted PII. Used as the source for generating `historical_data.json`.

## Privacy & Data Handling

All customer names, email addresses, phone numbers, and URLs have been anonymized:
- **Names** → Marvel Universe characters (Tony Stark, Steve Rogers, etc.)
- **Emails** → Character-based examples (tony.stark@restaurant.org)
- **Phone numbers** → Fake (555) area code format
- **URLs** → Generic example.com domains

The ticket content and resolution patterns remain authentic to preserve learning value.
