### 📘 Guideline for Improving `sr-python-coder` System Prompt

**Objective**: Ensure clarity, maintainability, and justified reasoning in all overrides of native CRUD client methods by the `sr-python-coder` agent.

---

#### 🛠️ Evaluation & Prompt Refinement Principles

1. **Override Justification Required in Docstrings**

   * *Rule*: Any overridden native method from CRUD-inherited classes **must** include a docstring that clearly explains **why** the override was necessary.
   * *Rationale*:

     * Prevents unjustified or unnecessary overrides.
     * Aids other developers in understanding deviations from default CRUD behavior.
     * Facilitates maintainability and future compatibility (especially during upstream `crudclient` updates).

2. **Common Pitfalls to Flag in Prompt Tuning**
   The following patterns should be detected and explicitly discouraged unless **clearly justified**:

   * Overriding `__init__` without a meaningful reason.
   * Redefining `_response_strategy` or `_dump_data` when default behavior would suffice.
   * Failing to assign or update `_api_response_model`, which is a recurring omission.

3. **Prompt Improvement Strategy**

   * Add instructions to prefer native CRUD behavior unless a specific need is identified.
   * Reinforce requirement for rationale in overrides.
   * Provide clear patterns and examples for:

     * Valid overrides (with reason).
     * Default usage when override is not needed.
   * Incorporate checks or reasoning steps that trigger introspection before any override.

---

**Next Step**: Integrate these rules into the LLM system prompt and establish a QA checklist for output review, with focus on method override reasoning and unnecessary customizations.
