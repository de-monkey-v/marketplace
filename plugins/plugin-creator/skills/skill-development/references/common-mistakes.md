# Common Mistakes in Skill Development

This reference documents common mistakes when developing skills and how to avoid them.

## Mistake 1: Weak Trigger Description

❌ **Bad:**
```yaml
description: Provides guidance for working with hooks.
```

**Why bad:** Vague, no specific trigger phrases, not third person

✅ **Good:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events. Provides comprehensive hooks API guidance.
```

**Why good:** Third person, specific phrases, concrete scenarios

### More Examples

**Bad descriptions:**
```yaml
# Too vague
description: Use this skill when working with hooks.

# Not third person
description: Load when user needs hook help.

# No trigger phrases
description: Provides hook guidance.

# Missing action verbs
description: Hook-related tasks.
```

**Good descriptions:**
```yaml
# Specific actions
description: This skill should be used when the user asks to "create a hook",
"add a PreToolUse hook", "validate tool use", "implement prompt-based hooks",
or mentions hook events (PreToolUse, PostToolUse, Stop).

# Multiple concrete triggers
description: This skill should be used when the user asks to "create a skill",
"add a skill to plugin", "write a new skill", "improve skill description",
"organize skill content", or needs guidance on skill structure or progressive disclosure.
```

## Mistake 2: Too Much in SKILL.md

❌ **Bad:**
```
skill-name/
└── SKILL.md  (8,000 words - everything in one file)
```

**Why bad:** Bloats context when skill loads, detailed content always loaded

✅ **Good:**
```
skill-name/
├── SKILL.md  (1,800 words - core essentials)
└── references/
    ├── patterns.md (2,500 words)
    └── advanced.md (3,700 words)
```

**Why good:** Progressive disclosure, detailed content loaded only when needed

### Content Distribution Guidelines

**Keep in SKILL.md:**
- Core concepts (300-500 words)
- Essential procedures (500-800 words)
- Quick reference tables
- Resource pointers (50-100 words)

**Move to references/:**
- Detailed API documentation
- Comprehensive examples
- Advanced techniques
- Migration guides
- Troubleshooting guides
- Historical context

## Mistake 3: Second Person Writing

❌ **Bad:**
```markdown
You should start by reading the configuration file.
You need to validate the input.
You can use the grep tool to search.
```

**Why bad:** Second person, not imperative form

✅ **Good:**
```markdown
Start by reading the configuration file.
Validate the input before processing.
Use the grep tool to search for patterns.
```

**Why good:** Imperative form, direct instructions

### Transformation Examples

| Avoid | Use Instead |
|-------|-------------|
| You should create... | Create... |
| You need to validate... | Validate... |
| You can use... | Use... |
| You must ensure... | Ensure... |
| You will want to... | Consider... |
| If you need to... | To accomplish X... |

## Mistake 4: Missing Resource References

❌ **Bad:**
```markdown
# SKILL.md

[Core content]

[No mention of references/ or examples/]
```

**Why bad:** Claude doesn't know references exist

✅ **Good:**
```markdown
# SKILL.md

[Core content]

## Additional Resources

### Reference Files
- **`references/patterns.md`** - Detailed patterns
- **`references/advanced.md`** - Advanced techniques

### Examples
- **`examples/script.sh`** - Working example
```

**Why good:** Claude knows where to find additional information

## Mistake 5: Inconsistent Naming

❌ **Bad:**
```yaml
name: My Skill Name
name: mySkillName
name: my_skill_name
```

**Why bad:** Spaces, camelCase, underscores not allowed

✅ **Good:**
```yaml
name: my-skill-name
name: skill-v2
name: api-integration
```

**Why good:** kebab-case format, lowercase, hyphens only

## Mistake 6: Orphaned Resources

❌ **Bad:**
```
skill-name/
├── SKILL.md
└── scripts/
    └── helper.sh  ← Never mentioned in SKILL.md
```

**Why bad:** Script exists but Claude doesn't know about it

✅ **Good:**
```
skill-name/
├── SKILL.md  ← Contains: "Use scripts/helper.sh to validate"
└── scripts/
    └── helper.sh
```

**Why good:** Resource is discoverable through SKILL.md

## Mistake 7: Duplicated Content

❌ **Bad:**
```
skill-name/
├── SKILL.md         ← Contains full API docs
└── references/
    └── api-docs.md  ← Same API docs repeated
```

**Why bad:** Wastes context, creates maintenance burden

✅ **Good:**
```
skill-name/
├── SKILL.md         ← "For API details, see references/api-docs.md"
└── references/
    └── api-docs.md  ← Complete API documentation
```

**Why good:** Single source of truth, progressive disclosure

## Mistake 8: Empty Directories

❌ **Bad:**
```
skill-name/
├── SKILL.md
├── references/   ← Empty
├── examples/     ← Empty
└── scripts/      ← Empty
```

**Why bad:** Unnecessary structure, confusing

✅ **Good:**
```
skill-name/
├── SKILL.md
└── references/
    └── guide.md  ← Only create directories you need
```

**Why good:** Minimal structure, only what's needed

## Mistake 9: Broken File References

❌ **Bad:**
```markdown
See `references/patterns.md` for details.
```
(But file doesn't exist)

**Why bad:** Claude tries to read non-existent file

✅ **Good:**
```markdown
See `references/patterns.md` for details.
```
(And file exists at that path)

**Validation:** Check all referenced files exist before publishing

## Mistake 10: Generic Skills

❌ **Bad:**
```yaml
name: helper
description: This skill helps with things.
```

**Why bad:** Too generic, no clear purpose

✅ **Good:**
```yaml
name: api-integration-testing
description: This skill should be used when the user asks to "test API endpoints",
"validate API responses", "mock API calls", or needs guidance on API testing patterns.
```

**Why good:** Specific purpose, clear triggering

## Prevention Checklist

Before publishing a skill:

- [ ] Description uses third person
- [ ] Description has 3-5 specific trigger phrases
- [ ] SKILL.md uses imperative form throughout
- [ ] SKILL.md is under 3,000 words
- [ ] Detailed content moved to references/
- [ ] All file references are valid
- [ ] No duplicated content
- [ ] No empty directories
- [ ] Resources mentioned in SKILL.md
- [ ] Name uses kebab-case format
