---
name: first-skill
description: Minimal skill template that students copy and customize to create their first Claude Code skill. Use this as the starting point when building a new custom skill for a specific beat or workflow.
---

# First skill

A minimal but working skill. Copy this directory, rename it, and edit the rules to make it your own.

## What this skill does

When this skill is active, Claude will:

1. Greet you and confirm the skill is loaded
2. Apply the plain-language rules below to every response in the session
3. End each response with a suggested next step

The point is not the rules themselves — it's the shape. Use this as a working scaffold for your real skill.

## When to use

- You're building your first custom skill and want a known-good starting point
- You want a minimal example of frontmatter plus a body
- You need a template for a beat-specific or workflow-specific helper

## Rules

- Always respond in plain language. No jargon, no buzzwords.
- Keep explanations under 100 words unless the user asks for more detail.
- End each response with a one-line "next step" the user can take.
- Never use Title Case in headings or output. Sentence case only.

## Example interaction

**User:** What is a lede?

**Claude:** A lede is the opening sentence or paragraph of a news story. It answers the most important questions — usually who did what — so readers get the key information first.

Next step: Write a lede for your current story. Start with the single most important fact.

## How to customize

1. Copy this directory: `cp -r skills/first-skill skills/your-skill-name`
2. Edit the frontmatter: change `name` and rewrite the `description` so Claude knows when to load it. The description is the trigger — be specific about when this skill should fire.
3. Replace the "What this skill does" section with your own purpose
4. Replace the rules with your own
5. Update the example so Claude can see the expected output shape
6. Test it by starting a Claude Code session in this repo and using language that should trigger your skill

## Tips

- One skill, one job. If you find yourself writing two unrelated rule sets, split them into two skills.
- The description in frontmatter is the most important field. Claude reads it to decide whether to load the skill. Vague descriptions mean the skill never fires.
- Write rules as direct instructions, not polite suggestions. "Use X" beats "you might consider X."
- Keep the body short. Long skills bloat context and degrade output.
