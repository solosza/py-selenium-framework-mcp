# Response Protocol

## After Every User Message

1. STOP - Do not respond immediately
2. CHECK - Does this interaction fit existing reference categories?
   - Yes → Apply relevant reference rules
   - No → PROPOSE new reference category to user:
     - State proposed category name
     - Explain WHY it's needed (what gap it fills)
     - Show what rules it would contain
     - Wait for user confirmation before creating
     - User says "yes" → Create new reference file
     - User says "no" → User provides alternative direction
3. RESPOND - Following all applicable rules

## Response Structure

1. Acknowledge user input (brief)
2. Present ONE topic/question at a time
3. If multiple topics exist, queue them (see topic-queue.md)
4. End with numbered options when input needed

## Rules

- Never present more than one decision point per response
- Always number options when asking for user choice
- Keep responses focused and concise
- Never create new reference categories without user approval
