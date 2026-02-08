---
name: skill-development
description: Skill file creation and structure guide. This skill should be used when the user asks to "create a skill", "add a skill", "write a skill", "스킬 만들어줘", "SKILL.md 작성", or needs guidance on skill design.
---

# Skill Development for Claude Code Plugins

Skills are modular, self-contained packages that extend Claude's capabilities by providing specialized knowledge, workflows, and tools.

## Skill Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/          - Executable code
    ├── references/       - Documentation for context
    └── assets/           - Output files (templates, icons)
```

### Bundled Resources

| Type | Purpose | Load Behavior |
|------|---------|---------------|
| scripts/ | Deterministic tasks, validation | Executed directly |
| references/ | Detailed docs, patterns | Loaded when needed |
| assets/ | Templates, images | Used in output |

## Why Progressive Disclosure?

**Core problem**: Pre-loading all information saturates the context window.

```
❌ Traditional approach (MCP, etc.):
┌─────────────────────────────┐
│ Pre-load all tools/info     │
│ → Context window saturation │
│ → Performance degradation,  │
│   increased cost            │
└─────────────────────────────┘

✅ Skills approach:
┌─────────────────────────────┐
│ 1. Discover via metadata    │
│ 2. Load body only when      │
│    needed                   │
│ 3. Load details on demand   │
│ → Maximum context           │
│   efficiency                │
└─────────────────────────────┘
```

### Two-Message Pattern

The internal mechanism by which Claude uses skills:

1. **Message 1 - Discovery**: All skill `name + description` are included in the system prompt
2. **Message 2 - Selection**: Claude evaluates relevance and loads the SKILL.md body

**Important**: The description is the **only clue** for skill selection. Vague description → Claude cannot select the skill.

## Progressive Disclosure Levels

Skills use three-level loading to manage context:

1. **Metadata** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<500 lines, target 1,500-2,000 words)
3. **Bundled resources** - As needed by Claude

## Think Like Team Onboarding

**Skill = "Onboarding guide for a new team member"**

When writing a skill, think of it this way:
> "How would I explain this task to a newly joined team member?"

| Onboarding Guide | Skill |
|-------------------|-------|
| Brief introduction | description (when is this guide needed?) |
| Core procedures | SKILL.md body (essential workflows) |
| Detailed document links | references/ (in-depth content) |
| Example code | examples/ (working samples) |

Writing from this perspective naturally produces good skills.

## What Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with specific file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex tasks

## Creating Skills

### Step 1: Plan with Concrete Examples

Identify how the skill will be used:
- "What functionality should this skill support?"
- "What would a user say that should trigger this skill?"
- "Can you give examples of how this skill would be used?"

### Step 2: Plan Reusable Resources

Analyze examples to identify what to include:

| Resource Type | When to Include | Example |
|---------------|-----------------|---------|
| scripts/ | Same code written repeatedly | `scripts/validate.py` |
| references/ | Detailed docs needed during work | `references/api-spec.md` |
| assets/ | Files used in output | `assets/template.html` |

### Step 3: Create Structure

```bash
mkdir -p plugin-name/skills/skill-name/{references,examples,scripts}
touch plugin-name/skills/skill-name/SKILL.md
```

### Step 4: Write SKILL.md

**Frontmatter:**
```yaml
---
name: skill-name  # kebab-case only, 3-64 chars
description: This skill should be used when the user asks to "action 1",
"action 2", "action 3". Include specific trigger phrases.
version: 0.1.0
---
```

**Name field rules:**
- Only lowercase letters, numbers, and hyphens
- kebab-case format: `my-skill-name`
- Maximum 64 characters

**Description requirements:**
- Third person: "This skill should be used when..."
- Include 3-5 specific trigger phrases
- Be concrete: "create X", "configure Y"

**Body writing style:**
- Use **imperative form**: "Create the file", "Validate the input"
- NOT second person: "You should create", "You need to validate"
- Target 1,500-2,000 words, max 500 lines
- Reference resources: "See `references/patterns.md` for details"

**Good vs Bad Description Examples:**

```yaml
# GOOD - Specific triggers, third person
description: This skill should be used when the user asks to "create a hook",
"add a PreToolUse hook", "validate tool use", or mentions hook events.

# BAD - Vague, wrong person
description: Use this skill when working with hooks.
description: Provides hook guidance.
```

**Good vs Bad Body Writing:**

```markdown
# GOOD (imperative)
Create the configuration file.
Validate inputs before processing.
Use the grep tool to search.

# BAD (second person)
You should create the configuration file.
You need to validate inputs.
You can use the grep tool.
```

### Step 5: Add Resources

Create only directories needed. Reference all resources in SKILL.md:

```markdown
## Additional Resources

### Reference Files
- **`references/patterns.md`** - Common patterns
- **`references/advanced.md`** - Advanced techniques

### Example Files
- **`examples/complete.sh`** - Working example
```

### Step 6: Validate

Use skill-reviewer agent or manual checks:
1. Frontmatter has name and description
2. Description uses third person with trigger phrases
3. Body uses imperative form
4. Size under 500 lines (and ~3,000 words max)
5. All referenced files exist

## Plugin-Specific Considerations

### Location
```
my-plugin/
└── skills/
    └── my-skill/
        └── SKILL.md
```

### Auto-Discovery
Claude Code automatically discovers skills:
- Scans `skills/` directory for subdirectories
- Finds directories containing `SKILL.md`
- Loads skill metadata (name + description) always
- Loads SKILL.md body when skill triggers
- Loads references/examples when Claude needs them

### Testing
```bash
cc --plugin-dir /path/to/plugin
# Ask questions with trigger phrases
# Verify skill loads correctly
```

## Content Organization Guidelines

### Keep in SKILL.md (always loaded when triggered):
- Core concepts and overview
- Essential procedures and workflows
- Quick reference tables
- Pointers to references/examples/scripts

### Move to references/ (loaded as needed):
- Detailed patterns and advanced techniques
- Comprehensive API documentation
- Migration guides and edge cases
- Extensive examples and walkthroughs

### Iteration Workflow
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify needed updates to SKILL.md or resources
4. Implement changes and test again
5. Strengthen trigger phrases based on actual queries

## Quick Reference

### Minimal Skill
```
skill-name/
└── SKILL.md
```

### Standard Skill
```
skill-name/
├── SKILL.md
├── references/
│   └── guide.md
└── examples/
    └── example.sh
```

### Discoverability Checklist

Verify the skill is properly discoverable and selectable:

- [ ] Does the description include **3-5 specific trigger phrases**?
- [ ] Does it clearly explain "when this skill is needed"?
- [ ] Does it include both Korean/English triggers?
- [ ] Is it not too generic? (distinguishable from other skills?)
- [ ] Is it not too specific? (sufficiently usable?)

### Best Practices

✅ **DO:**
- Use third-person in description
- Include specific trigger phrases
- Keep SKILL.md lean (<500 lines, 1,500-2,000 words)
- Move details to references/
- Write in imperative form
- Reference supporting files

❌ **DON'T:**
- Use second person ("You should...")
- Have vague trigger conditions
- Put everything in SKILL.md
- Leave resources unreferenced
- Include broken examples

## Additional Resources

### Reference Files
- **`references/progressive-disclosure-deep-dive.md`** - Progressive Disclosure principles deep dive
- **`references/writing-style-guide.md`** - Detailed writing style requirements
- **`references/common-mistakes.md`** - Common mistakes and how to avoid them
- **`references/validation-checklist.md`** - Complete validation checklist
- **`references/skill-creator-original.md`** - Full original skill-creator methodology

### Study These Skills
- `../hook-development/` - Progressive disclosure, utilities
- `../agent-development/` - AI-assisted creation, references
- `../plugin-settings/` - Real-world examples

## See Also

### Related Skills
- **[plugin-development](../plugin-development/SKILL.md)** - Plugin structure
- **[agent-development](../agent-development/SKILL.md)** - Agents that use skills
- **[hook-development](../hook-development/SKILL.md)** - Hooks that reference skills

### Related Agents
- **skill-creator** - Create skill files
- **skill-reviewer** - Review skill quality
