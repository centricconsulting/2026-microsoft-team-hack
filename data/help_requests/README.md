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
- Use this data as a reference for understanding ticket patterns
- Analyze resolution patterns to improve classification accuracy
- Build few-shot prompts with relevant examples
- Test classification logic against known resolutions

**Data Notes:**
- Contains 50 fictional DCI help desk tickets spanning all four classification categories
- All names, companies, and account IDs are fictional — drawn from the Marvel Universe setting
- Includes 7 entries with a populated `what_we_think_should_have_been_done` field, illustrating common misrouting scenarios teams can learn from

### sample_requests.json

Ten example help requests for testing the triage API during the hackathon. Covers all four routing categories and includes at least one intentionally vague ticket (REQ0006) to exercise edge-case handling.
