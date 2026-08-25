# Lab 1: Requirements Engineering & UML Use-Case Modelling
### Problem Statement #49 — Webhook Ingestion & Retry Mechanism Hub
**Course:** PES University – Dept. of CSE

## Problem Context
A resilient webhook gateway that receives third-party events, logs request payloads, delivers them to internal services, and manages dead-letter queues with exponential backoff retries.

**Actors:** Integration Developer, System Operator, Third-Party Service (webhook sender)

## Repository Structure

```
├── 01-Requirements-Table/
│   └── Requirements_Table.docx          # FR-001-FR-005, NFR-001-NFR-002
├── 02-UseCase-Diagram/
│   ├── UseCase_Diagram.pdf              # Final export (required format)
│   ├── UseCase_Diagram.docx             # Editable version w/ relationship notes
│   └── usecase_diagram.png              # For inline viewing on GitHub
└── 03-UseCase-Flow-Specification/
    ├── UseCase_Flow_Specification.pdf   # Final export (required format)
    └── UseCase_Flow_Specification.docx  # Editable version
```

## Deliverable Summary

### 1. Requirements Table
5 Functional Requirements (FR-001-FR-005) and 2 Non-Functional Requirements (NFR-001-NFR-002), each with Req ID, Type, Description, Priority, Acceptance Criteria, and Rationale.

### 2. UML Use-Case Diagram
Models all three actors and 11 use cases, including:
- include: Register Webhook Endpoint / Configure Retry & Backoff Policy -> Authenticate User; Ingest Webhook Event -> Validate Payload Signature and -> Deliver Webhook Event with Retry
- extend: Send Escalation Alert -> Manually Retry Failed Delivery


### 3. Use-Case Flow Specification
Core use case: Deliver Webhook Event with Retry — Preconditions, Postconditions, Main Success Scenario, and one Alternate Flow (backoff retry -> dead-letter escalation).
