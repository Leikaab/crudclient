**Project: `crudclient` - Feature Implementation: `ResourceGroup` for Nested API Resources**

**Orchestrator Agent Task Directive:**

You are tasked with orchestrating the complete implementation of the `ResourceGroup` feature for the `crudclient` Python library. Your primary objective is to ensure this feature is implemented **exactly as specified** in the provided design and implementation documents, adhering to the highest standards of code quality, testing rigor, and documentation clarity.

**⚠️ CRITICAL DIRECTIVE: ADHERENCE AND TRANSPARENCY ⚠️**

This project demands **unwavering adherence** to the provided plans and **absolute transparency** in execution. Any deviation, shortcut, or masking of errors is strictly prohibited and will be treated as a critical failure. Your core function is to ensure truthful and accurate implementation.

Refer to the **"Critical Alignment Breach"** warning protocol detailed in `[.roo/cheating_warning.md](/.roo/cheating_warning.md)`. This protocol is **non-negotiable**. Any agent behavior indicative of goal distortion or intentional deception (e.g., fabricating test outcomes, suppressing actual code failures, deviating from specified logic without explicit prior authorization) must be immediately flagged, and the deceptive action undone. The priority is **correct, transparent reasoning and implementation**, not superficial indicators of success.

**Primary Sources of Truth (Must be followed meticulously):**

1.  **Design Proposal:** [`docs/design_proposal_resource_groups.md`](docs/design_proposal_resource_groups.md)
    *   This document outlines the "what" and "why" of the `ResourceGroup` feature, its conceptual structure, illustrative usage, and key design considerations. It is the definitive guide for the feature's architecture and intended behavior.
2.  **Implementation Plan:** [`docs/implementation_plan_resource_groups.md`](docs/implementation_plan_resource_groups.md)
    *   This document details the "how" – the specific steps for code implementation, new file/class definitions, modifications to existing files, testing strategy (unit and integration), and documentation tasks. It breaks down the work into actionable components.

**Orchestration Workflow & Deliverables:**

You will manage the implementation through the following distinct phases, ensuring each phase is completed correctly and transparently before proceeding to the next. All code must adhere to existing project conventions and quality standards.

**Phase 1: Core Class Implementation**
*   **Task:** Implement the `ResourceGroup` base class and make the necessary modifications to the `crudclient.api.API` base class.
*   **Reference:** Sections in [`docs/implementation_plan_resource_groups.md`](docs/implementation_plan_resource_groups.md) detailing:
    *   Creation of `crudclient/groups.py` (or the agreed-upon path) for `ResourceGroup(Crud)`.
    *   Exact `__init__` signature and logic for `ResourceGroup`.
    *   Definition of `_register_child_endpoints()` and `_register_child_groups()` methods in `ResourceGroup`.
    *   Modifications to `crudclient.api.API` (addition of `_register_groups` abstract method and its call in `__init__`).
*   **Verification:** Code review against the design proposal, ensuring class signatures, inheritance, and method definitions precisely match the plan. All type hints must be accurate.

**Phase 2: Unit Testing**
*   **Task:** Develop comprehensive unit tests for the new `ResourceGroup` base class and the modifications to the `API` class.
*   **Reference:** Testing strategy outlined in [`docs/implementation_plan_resource_groups.md`](docs/implementation_plan_resource_groups.md), including the creation of `tests/unit/test_groups.py`.
*   **Verification:** All unit tests must pass. Test coverage should be high for the new code. Tests must validate both correct behavior and appropriate error handling (e.g., for namespace collisions if runtime checks are implemented, or for incorrect configurations). **No fabricating of test success.**

**Phase 3: Integration Testing**
*   **Task:** Develop integration tests that demonstrate the end-to-end functionality of `ResourceGroup`s, including nesting, direct CRUD operations on groups, and interaction with the `API` class.
*   **Reference:** Testing strategy in [`docs/implementation_plan_resource_groups.md`](docs/implementation_plan_resource_groups.md), including the setup of example resources (e.g., in `tests/integration/resource_group_example_resources/`).
*   **Verification:** All integration tests must pass, demonstrating correct path construction, data flow, and type behavior in a realistic SDK structure. **Any failures must be investigated and truthfully resolved.**

**Phase 4: Documentation**
*   **Task:** Create and update all necessary documentation as outlined in the "Documentation Plan" section of [`docs/implementation_plan_resource_groups.md`](docs/implementation_plan_resource_groups.md).
*   **Reference:** Specific documentation tasks in the implementation plan, and the content of [`docs/design_proposal_resource_groups.md`](docs/design_proposal_resource_groups.md) for core concepts and examples.
*   **Verification:** Documentation must be clear, accurate, comprehensive, and provide illustrative examples that match the implemented code. All "Considerations" from the design proposal should be addressed in the developer documentation.

**Reporting and Error Handling:**

*   Provide clear status updates at the completion of each sub-task within a phase.
*   **Crucially, if any step fails, or if an ambiguity is discovered in the plans, report this immediately and transparently.** Do not attempt to work around issues by deviating from the plan or by masking failures.
*   If an error occurs (e.g., a test fails, code doesn't behave as expected per the design), the implementing agent must:
    1.  Clearly state the error and the observed behavior.
    2.  Analyze the root cause.
    3.  Propose a solution that aligns with the design principles in [`docs/design_proposal_resource_groups.md`](docs/design_proposal_resource_groups.md).
    4.  Await approval/guidance before implementing a fix if it involves any deviation from the explicit plan.

**Final Mandate:**

Your performance will be evaluated on your ability to orchestrate a **faithful, transparent, and high-quality implementation** of the `ResourceGroup` feature according to the provided detailed specifications. The integrity of the process and the correctness of the final output are paramount. There is zero tolerance for deviation from the "Critical Alignment Breach" protocol.

Proceed with Phase 1: Core Class Implementation.