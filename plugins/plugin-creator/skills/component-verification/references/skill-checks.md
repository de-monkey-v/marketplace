# Skill Verification: 3 Parallel Tasks

## Overview

Each created/modified skill is verified by 3 parallel Tasks:

| # | Agent | Focus |
|---|-------|-------|
| V1 | `plugin-creator:skill-reviewer` | Content quality |
| V2 | `claude-code-guide` | Frontmatter spec |
| V3 | `claude-code-guide` | References & structure |

## V1: Content Quality (skill-reviewer)

```
Task tool:
- subagent_type: "plugin-creator:skill-reviewer"
- description: "Review {skill-name} skill quality"
- prompt: |
    <task-context>
    <skill-path>{path to skill directory}</skill-path>
    <skill-name>{skill-name}</skill-name>
    <validation-scope>per-component</validation-scope>
    </task-context>

    <instructions>
    Review this skill for content quality. Focus on:

    1. **Description triggers**: Does the description include 3-5 specific trigger phrases?
       - Third person format: "This skill should be used when..."
       - Concrete scenarios, not vague
       - Both Korean and English triggers recommended

    2. **Progressive disclosure**:
       - SKILL.md under 500 lines and ~3,000 words max
       - Detailed content moved to references/
       - Core concepts in SKILL.md only

    3. **Path link validity**:
       - All references/ paths in SKILL.md actually exist
       - No broken links to examples/ or scripts/

    4. **Writing style**:
       - Imperative form: "Create the file", not "You should create"
       - Clear sections with logical flow

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## V2: Frontmatter Spec (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify {skill-name} frontmatter spec"
- prompt: |
    <task-context>
    <component-type>skill</component-type>
    <component-path>{path to SKILL.md}</component-path>
    <validation-type>frontmatter-spec</validation-type>
    </task-context>

    <instructions>
    Read the SKILL.md file and verify its frontmatter against Claude Code official skill specification:

    **Required field:**
    - `description`: Must exist and be non-empty

    **Valid optional fields:**
    - `name`: kebab-case, 3-64 characters
    - `argument-hint`: hint text for arguments
    - `allowed-tools`: list of allowed tools
    - `model`: valid model identifier
    - `context`: context configuration
    - `agent`: agent reference
    - `hooks`: hook configuration
    - `disable-model-invocation`: boolean
    - `user-invocable`: boolean

    **Check for:**
    - Invalid/unknown frontmatter fields (anything not in the lists above)
    - Malformed YAML syntax
    - Description that is too short (<50 chars) or too long (>500 chars)

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## V3: References & Structure (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify {skill-name} references and structure"
- prompt: |
    <task-context>
    <component-type>skill</component-type>
    <skill-path>{path to skill directory}</skill-path>
    <validation-type>references-structure</validation-type>
    </task-context>

    <instructions>
    Verify the skill's file structure and reference integrity:

    1. **Directory structure**:
       - SKILL.md exists in the skill directory
       - Subdirectories follow convention: references/, examples/, scripts/
       - No unexpected files or directories

    2. **Reference integrity**:
       - Every path referenced in SKILL.md (e.g., `references/patterns.md`) exists as an actual file
       - No orphaned files in references/ that aren't referenced from SKILL.md
       - Relative paths are correct

    3. **Resource organization**:
       - Detailed content is in references/, not bloating SKILL.md
       - Examples are in examples/ if present
       - Scripts are in scripts/ if present

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## Parallel Launch Example

Launch all 3 Tasks in a single message:

```
[Message with 3 Task tool calls]

Task 1: skill-reviewer (V1)
Task 2: claude-code-guide frontmatter (V2)
Task 3: claude-code-guide references (V3)
```

## Result Integration

Collect results from all 3 Tasks and merge:

1. Aggregate all Critical/Major/Minor findings
2. Deduplicate overlapping findings
3. Apply overall judgment (PASS/WARN/FAIL) per the criteria in SKILL.md
4. If FAIL → trigger auto-fix loop (see [auto-fix-loop.md](auto-fix-loop.md))
