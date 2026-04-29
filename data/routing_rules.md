# Routing Definitions

When triaging a help desk ticket, the AI must classify it into **one of four categories**:

---

## 🗄️ Data Patch

**Route here when the issue can be resolved by running a database script** — typically a SQL `UPDATE`, `INSERT`, or `DELETE` against a known, DBA-maintained data table. No application code changes are needed.

**Route here when the request involves:**
- Correcting a work order record, status flag, or reference data entry
- Adding or updating rows in a contractor mapping or site configuration table
- Relinking a contractor assignment or work order to the correct project
- Backfilling a field or resetting a data flag after a bad import
- Any data-only fix where no schema change is implied

**Examples:**
- "The nightly work order sync hasn't run in 3 days"
- "The active work order count in the dashboard doesn't match our backend"
- "We need a feature flag turned on for our account in the config table"

### Suggested Query Scaffolds

Based on the ticket description, the AI should suggest the most applicable scaffold below. All scripts must be wrapped in a `BEGIN TRAN / ROLLBACK` block so the DBA can inspect results before committing.

**Insert missing reference / lookup data (e.g., damage category, site type)**
```sql
BEGIN TRAN

INSERT INTO [dbo].[TableName] ([Column1], [Column2], [Column3])
VALUES
    ('Value1', 'Value2', 'Value3');
-- Add additional rows as needed

-- Verify before committing:
SELECT * FROM [dbo].[TableName] WHERE [Column1] = 'Value1';

ROLLBACK -- Change to COMMIT once verified
```

**Update a work order status, configuration flag, or field value**
```sql
BEGIN TRAN

UPDATE [dbo].[WorkOrders]
SET    [StatusCode] = 'ACTIVE',       -- or the target value
       [UpdatedDate] = GETUTCDATE()
WHERE  [WorkOrderId] = '<work_order_id>'; -- scope tightly

-- Verify:
SELECT [WorkOrderId], [StatusCode], [UpdatedDate]
FROM   [dbo].[WorkOrders]
WHERE  [WorkOrderId] = '<work_order_id>';

ROLLBACK -- Change to COMMIT once verified
```

**Relink a contractor or work order to the correct project**
```sql
BEGIN TRAN

-- Step 1: relink child records from the incorrect project to the correct one
UPDATE [dbo].[SiteAssignments]
SET    [ProjectId] = <correct_project_id>
WHERE  [ProjectId] = <incorrect_project_id>
  AND  [ContractorId] = <contractor_id>;

-- Step 2: verify no orphaned assignments remain
SELECT COUNT(*) AS OrphanCount
FROM   [dbo].[SiteAssignments]
WHERE  [ProjectId] = <incorrect_project_id>;

-- Step 3: if the incorrect project record should be deactivated
UPDATE [dbo].[Projects]
SET    [IsActive] = 0,
       [UpdatedDate] = GETUTCDATE()
WHERE  [Id] = <incorrect_project_id>;

ROLLBACK -- Change to COMMIT once verified
```

**Add a site or damage-zone mapping entry**
```sql
BEGIN TRAN

INSERT INTO [dbo].[SiteMappings] ([SiteCode], [ZoneCode], [Description], [CreatedDate])
VALUES ('<site_value>', '<zone_value>', '<description>', GETUTCDATE());

-- Verify:
SELECT * FROM [dbo].[SiteMappings]
WHERE  [SiteCode] = '<site_value>';

ROLLBACK -- Change to COMMIT once verified
```

> ⚠️ **All scripts require DBA review and approval before execution.** No automated execution is permitted.

---

## 💻 Engineering Ticket

**Route here when the issue requires a developer to modify application code**, fix a bug, or build a new feature. The problem cannot be resolved by a data change alone.

**Route here when the request involves:**
- A software bug, crash, or unexpected system behavior
- A broken UI element, 404 error, or regression after a deployment
- A feature request or enhancement requiring new or changed code
- A technical integration failure (API, data feed, authentication)

**Examples:**
- "The export button on the site status report doesn't work"
- "The site sync API returns a 500 error after midnight"
- "We need the ability to filter work orders by incident type"

---

## 🎫 Field Support

**Route here for standard support requests** that do not require code or database changes — typically portal access, how-to questions, contractor onboarding, or operational issues handled by the service desk.

**Route here when the request involves:**
- Portal access (password resets, lockouts, new contractor onboarding)
- Safety certification questions or training enrollment from the approved catalog
- Equipment requisition or procurement how-to guidance
- Billing, invoicing, or project cost questions
- General procedural guidance or SLA-tracked follow-up

**Examples:**
- "How do I add a new contractor to our crew roster?"
- "We haven't received our invoice for the February reconstruction project"
- "Can someone walk us through the new portal?"

---

## ⚠️ Needs Human Review

**Use this classification when the ticket is ambiguous**, contains insufficient information, or does not clearly fall into any category above. Route to the triage lead for manual assessment.

**Use this when:**
- The description is too vague to classify confidently
- Key context is missing (system name, error message, affected site, steps to reproduce)
- The request could plausibly span multiple categories
- The issue involves multiple systems and requires deeper analysis

The response should include a specific follow-up question to ask the requester.
