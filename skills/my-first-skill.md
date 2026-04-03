# My first skill

A minimal skill template. Copy this file and modify it for your needs.

## What this skill does

When invoked with `/my-first-skill`, Claude will:

1. Greet you and confirm the skill is active
2. Apply the rules below to all responses

## Rules

- Always respond in plain language (no jargon)
- Keep explanations under 100 words unless asked for more detail
- End each response with a suggested next step

## Example interaction

**User:** /my-first-skill What is a lede?

**Claude:** A lede is the opening sentence or paragraph of a news story. It answers the most important questions—usually who did what—so readers get the key information first.

**Next step:** Try writing a lede for your current story. Start with the single most important fact.

---

## How to customize this skill

1. Copy this file: `cp skills/my-first-skill.md skills/your-skill-name.md`
2. Rename to describe your skill's purpose
3. Edit the "What this skill does" section
4. Replace the rules with your own
5. Update the example interaction
6. Test it: `/your-skill-name`

## Tips

- Keep skills focused on one task or style
- Write rules as clear instructions, not suggestions
- Include an example so Claude understands the expected format
