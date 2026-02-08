# Skill Validation Checklist

Complete validation checklist for Claude Code plugin skills.

## Structure Validation

### File Structure
- [ ] SKILL.md file exists with valid YAML frontmatter
- [ ] Frontmatter has `name` field (required)
- [ ] Frontmatter has `description` field (required)
- [ ] Markdown body is present and substantial
- [ ] Referenced files actually exist
- [ ] No empty directories

### Directory Layout
```
skill-name/
├── SKILL.md              # Required
├── references/           # Optional - detailed docs
├── examples/             # Optional - working code
└── scripts/              # Optional - utilities
```

## Name Field Validation

- [ ] Uses only lowercase letters, numbers, and hyphens
- [ ] No spaces or underscores
- [ ] Follows kebab-case format (e.g., `my-skill-name`)
- [ ] Maximum 64 characters
- [ ] Starts and ends with alphanumeric character

### Valid Examples
```yaml
name: skill-development
name: api-v2
name: my-plugin-helper
```

### Invalid Examples
```yaml
name: Skill Name      # uppercase, spaces
name: my_skill        # underscores
name: -skill-         # starts/ends with hyphen
```

## Description Quality

- [ ] Uses third person ("This skill should be used when...")
- [ ] Includes 3-5 specific trigger phrases users would say
- [ ] Lists concrete scenarios ("create X", "configure Y")
- [ ] Not vague or generic
- [ ] Under 500 characters

### Good Example
```yaml
description: This skill should be used when the user asks to "create a hook",
"add a PreToolUse hook", "validate tool use", "implement prompt-based hooks",
or mentions hook events (PreToolUse, PostToolUse, Stop).
```

### Bad Examples
```yaml
description: Provides guidance for hooks.           # Vague
description: Use this skill for hook tasks.         # Not third person
description: Helps with hook-related work.          # No trigger phrases
```

## Content Quality

- [ ] SKILL.md body uses imperative/infinitive form
- [ ] No second person ("you should", "you need")
- [ ] Body is focused and lean (1,500-2,000 words ideal)
- [ ] Under 5,000 words maximum
- [ ] Detailed content moved to references/
- [ ] Examples are complete and working
- [ ] Scripts are executable and documented

### Writing Style Check
```markdown
# Good (imperative)
Create the configuration file.
Validate inputs before processing.
Use the grep tool to search.

# Bad (second person)
You should create the configuration file.
You need to validate inputs.
You can use the grep tool.
```

## Progressive Disclosure

- [ ] Core concepts in SKILL.md (always loaded)
- [ ] Detailed documentation in references/ (loaded as needed)
- [ ] Working code in examples/ (copy-paste ready)
- [ ] Utility scripts in scripts/ (executable)
- [ ] SKILL.md references these resources clearly

### Content Distribution
| Location | Content Type | Load Behavior |
|----------|--------------|---------------|
| SKILL.md | Core concepts, procedures | When skill triggers |
| references/ | Detailed docs, advanced topics | When Claude needs |
| examples/ | Working code samples | When copying |
| scripts/ | Utilities | When executing |

## Resource References

- [ ] All resources in references/ mentioned in SKILL.md
- [ ] All examples/ files documented
- [ ] All scripts/ utilities referenced
- [ ] No orphaned files (exist but not referenced)
- [ ] No broken references (mentioned but don't exist)

### Reference Format
```markdown
## Additional Resources

### Reference Files
- **`references/patterns.md`** - Common patterns and techniques
- **`references/advanced.md`** - Advanced use cases

### Example Files
- **`examples/complete.sh`** - Full working example
- **`examples/minimal.json`** - Minimal configuration

### Utility Scripts
- **`scripts/validate.sh`** - Validate skill structure
```

## Testing Validation

- [ ] Skill triggers on expected user queries
- [ ] Content is helpful for intended tasks
- [ ] No duplicated information across files
- [ ] References load when needed
- [ ] Scripts execute successfully
- [ ] Examples are correct and complete

### Trigger Testing
Test these query patterns:
1. Exact trigger phrases from description
2. Variations of trigger phrases
3. Related questions that should trigger
4. Unrelated questions that should NOT trigger

## Size Guidelines

| Component | Ideal | Maximum |
|-----------|-------|---------|
| SKILL.md body | 1,500-2,000 words | 5,000 words |
| Description | 100-200 chars | 500 chars |
| Single reference file | 2,000-5,000 words | No limit |
| Total skill size | Varies | Reasonable |

## Automated Checks

Run these validations:

### Check frontmatter
```bash
head -20 SKILL.md | grep -E "^(name|description):"
```

### Count words
```bash
wc -w SKILL.md
```

### Validate name format
```bash
name=$(grep "^name:" SKILL.md | sed 's/name: *//')
echo "$name" | grep -E "^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$"
```

### Check for second person
```bash
grep -E -i "you (should|need|can|must|will)" SKILL.md && echo "Second person found!"
```

### Verify references exist
```bash
grep -oE "references/[^)\"']+\.md" SKILL.md | while read f; do
  test -f "$f" || echo "Missing: $f"
done
```

## Final Checklist

Before publishing:

| Category | Check | Status |
|----------|-------|--------|
| Structure | SKILL.md exists | ☐ |
| Structure | Frontmatter valid | ☐ |
| Name | Kebab-case format | ☐ |
| Description | Third person | ☐ |
| Description | Trigger phrases | ☐ |
| Content | Imperative form | ☐ |
| Content | Size under limit | ☐ |
| Resources | All referenced | ☐ |
| Resources | All exist | ☐ |
| Testing | Triggers correctly | ☐ |
