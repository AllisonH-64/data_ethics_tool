# Policy Appendix: Incident Management Workflow

## Purpose
This appendix defines a consistent incident workflow for events related to Data Collection, Data Cleaning, Data Engineering, and Governance/Compliance.

## Scope
This workflow applies to incidents reported by employees, customers, and vendors, including internal and external incidents.

## Principles
- Single-owner accountability: one owning department per incident stage.
- No overlap: advisory functions support but do not own actions.
- Evidence integrity: all records must be complete and traceable.

## Standard Workflow

### 1. Report Incident
Required fields:
- Incident type and category
- Date and time
- Description
- Affected systems or data
- Evidence attachments (if available)

Output:
- Unique incident ID and initial record

### 2. Classification
Classify:
- Internal or External
- Primary incident domain: Governance and Compliance, Cybersecurity, Operational, or Reputational
- Data lifecycle area: Data Collection, Data Cleaning, or Data Engineering

Output:
- Classified record with routing tags

### 3. Initial Review and Risk Triage
Reviewer:
- Compliance Officer or IT Security Lead

Activities:
- Validate reported facts
- Assess immediate impact
- Assign preliminary risk: Low, Medium, or High

Output:
- Risk-rated incident and response owner assignment

### 4. Department Routing (No Overlap)
Owning department must be one only:
- IT Security for cybersecurity incidents
- HR for internal misconduct
- Legal for regulatory and legal exposure
- Compliance for governance or policy breaches

Control requirements:
- One primary domain per incident
- One active owning department at a time
- Advisory departments may provide input only

Output:
- Ownership assignment and acknowledgment timestamp

### 5. Response Actions
Required activities:
- Containment to stop immediate harm
- Corrective actions (e.g., patching, training, access changes, disciplinary action)
- Evidence preservation and chain-of-custody documentation

Output:
- Action log with owner, timestamps, and status

### 6. Resolution and Follow-Up
Required activities:
- Root cause analysis
- Lessons learned
- Preventive measures (policy, training, technical controls, awareness)
- Communication plan (internal memo and external disclosure when required)

Output:
- Remediation and prevention plan with due dates

### 7. Approval and Closure
Closure criteria:
- Containment complete
- Corrective actions complete
- Preventive actions assigned or complete
- Documentation complete

Required sign-off:
- Owning Department Lead
- Compliance Officer
- Secondary reviewer when required by risk or regulation

Output:
- Closed incident file archived in compliance records

## RACI (No Overlap)

| Stage | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Report Intake | Compliance Intake | Compliance Officer | Reporter | Department Lead |
| Classification | Compliance | Compliance Officer | IT Security, HR, Legal | Executive Sponsor |
| Triage | Compliance or IT Security | Triage Lead | Legal, HR (as needed) | Department Lead |
| Active Response | Single Owning Department | Case Owner | Advisory Departments | Executive Sponsor |
| Root Cause and Prevention | Owning Department | Case Owner | Compliance, Legal, IT Security, HR | Department Lead |
| Closure | Owning Department | Compliance Officer | Secondary Reviewer (if needed) | Executive Sponsor |

## Record Retention
- Archive each incident in the compliance record repository.
- Retain records according to applicable legal, contractual, and policy requirements.

## Public Information Requirement
- If public information is required, it must be issued within 30 calendar days of incident confirmation unless legal hold or regulator instructions require a different timeline.
- The incident record must include deadline date, completion date, and approval owner.

## Review Cycle
- Review this appendix annually, or earlier after high-risk incidents.
