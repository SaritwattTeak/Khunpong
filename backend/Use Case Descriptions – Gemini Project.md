# Gemini Project – Use Case Descriptions

This document contains software analysis artifacts for the Gemini Project.
The use case descriptions are derived from the system requirements and use
case diagram created in Deliverable D1.  
The selected use cases focus on core observation planning, execution, and
monitoring activities.  
The **Login** use case is intentionally excluded.

---

## Use Case 1: Create Science Plan

**Use Case Name:** Create Science Plan  
**ID:** UC-01  
**Priority:** High  
**Primary Actor:** Astronomer  
**Supporting Actors:** Science Observer  

**Description:**  
This use case allows an astronomer to create a science plan that specifies the
target objects, observing conditions, instruments, and parameters required for
an astronomical observation.

**Type:** External  

**Preconditions:**  
1. The user has an astronomer or science observer role.  
2. The system is in observation planning mode.

**Postconditions:**  
1. A new science plan is created and stored in the system.  
2. The science plan is available for editing and validation.

**Normal Flow:**  
1. The user selects the option to create a new science plan.  
2. The system displays the science plan creation interface.  
3. The user enters observation details (targets, instruments, constraints).  
4. The user saves the science plan.  
5. The system stores the plan and confirms successful creation.

**Alternative Flow:**  
- 3a. If required information is missing, the system displays error messages
      and requests the user to correct the input.

---

## Use Case 2: Validate Science Plan

**Use Case Name:** Validate Science Plan  
**ID:** UC-02  
**Priority:** High  
**Primary Actor:** Science Observer  
**Supporting Actors:** Astronomer  

**Description:**  
This use case allows users to validate a science plan by testing it with a
simulated or virtual telescope to ensure feasibility and safety.

**Type:** External  

**Preconditions:**  
1. A science plan exists in the system.  
2. The user has permission to validate science plans.

**Postconditions:**  
1. The science plan is marked as valid or invalid.  
2. Validation results are stored and made available to users.

**Normal Flow:**  
1. The user selects a science plan for validation.  
2. The system runs the plan using a simulated telescope.  
3. The system checks operational and safety constraints.  
4. The system displays the validation results.  
5. The user reviews the results.

**Alternative Flow:**  
- 3a. If validation fails, the system displays detailed error information and
      recommendations for correction.

---

## Use Case 3: Submit Observing Program

**Use Case Name:** Submit Observing Program  
**ID:** UC-03  
**Priority:** High  
**Primary Actor:** Astronomer  
**Supporting Actors:** Administrator  

**Description:**  
This use case allows a validated science plan to be submitted as an observing
program for review, approval, and scheduling.

**Type:** External  

**Preconditions:**  
1. The science plan has been successfully validated.  
2. The user has permission to submit observing programs.

**Postconditions:**  
1. The observing program is submitted to the system.  
2. The program status is set to *Pending Review*.

**Normal Flow:**  
1. The user selects a validated science plan.  
2. The user submits the plan as an observing program.  
3. The system records the submission.  
4. The system updates the program status.

**Alternative Flow:**  
- 2a. If the plan is not validated, the system rejects the submission and
      notifies the user.

---

## Use Case 4: Execute Observing Program

**Use Case Name:** Execute Observing Program  
**ID:** UC-04  
**Priority:** Critical  
**Primary Actor:** Telescope Operator  
**Supporting Actors:** Science Observer  

**Description:**  
This use case allows an operator to execute an approved observing program using
automated, interactive, or queue-based observing modes.

**Type:** External  

**Preconditions:**  
1. The observing program has been approved.  
2. The system is in observing mode.  
3. The user has telescope operator privileges.

**Postconditions:**  
1. The observing program is executed.  
2. Observation data is collected and stored.

**Normal Flow:**  
1. The operator selects an approved observing program.  
2. The system prepares the telescope and instruments.  
3. The system executes the observing sequence.  
4. Observation data is collected during execution.  
5. The system displays execution status information.

**Alternative Flow:**  
- 3a. The operator interrupts or reschedules the observation if required due
      to operational or environmental conditions.

---

## Use Case 5: Monitor Observation Progress

**Use Case Name:** Monitor Observation Progress  
**ID:** UC-05  
**Priority:** Medium  
**Primary Actor:** Science Observer  
**Supporting Actors:** Astronomer, Administrator  

**Description:**  
This use case allows users to monitor the progress of an observation and view
telescope and instrument status without interfering with operations.

**Type:** External  

**Preconditions:**  
1. An observation is currently running.  
2. The user has permission to monitor observations.

**Postconditions:**  
1. Observation progress and system status are displayed to the user.

**Normal Flow:**  
1. The user accesses the monitoring interface.  
2. The system displays real-time observation progress.  
3. The system displays telescope and instrument status indicators.

**Alternative Flow:**  
- 2a. If the user is accessing the system remotely, the system provides
      read-only monitoring access.

---

  ## Activity Diagram Case 1 : Create Science Plan
<img width="368" height="664" alt="Screenshot 2569-01-30 at 14 58 58" src="https://github.com/user-attachments/assets/1720538f-33c0-4a2e-92d8-7389d13403f9" />

  ## Activity Diagram Case 2 : Validate Science Plan
<img width="356" height="657" alt="Screenshot 2569-01-30 at 15 00 16" src="https://github.com/user-attachments/assets/8262c4a6-44a3-46b5-b829-659c624eaa46" />

  ## Activity Diagram Case 3 : Sumbit Observing Program
<img width="506" height="646" alt="Screenshot 2569-01-30 at 15 01 26" src="https://github.com/user-attachments/assets/93f7b6b1-8d89-4d70-bffe-ad22e066de3f" />

---

  ## Class Diagram
<img width="495" height="660" alt="Screenshot 2569-01-30 at 15 08 41" src="https://github.com/user-attachments/assets/b5beb319-9b82-433a-be6f-ea09819e0309" />

---

  ## Sequence Diagram 1 — UC-01 Create Science Plan
<img width="531" height="611" alt="Screenshot 2569-01-30 at 15 16 53" src="https://github.com/user-attachments/assets/6896f737-4fa2-48b5-a581-051bba67298c" />

  ## Sequence Diagram 2 — UC-02 Validate Science Plan
<img width="824" height="634" alt="Screenshot 2569-01-30 at 15 19 37" src="https://github.com/user-attachments/assets/f5c58c59-00a2-4b1e-bc74-b63d91bafd0c" />
  
  ## Sequence Diagram 3 — UC-03 Submit Observing Program
<img width="447" height="415" alt="Screenshot 2569-01-31 at 18 03 15" src="https://github.com/user-attachments/assets/e03a0e4d-eff0-475c-b0d7-f43231818683" />





  


