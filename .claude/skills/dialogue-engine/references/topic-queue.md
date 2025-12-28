<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Topic Queue

## Purpose

Manage multiple topics/questions that need discussion without overwhelming user.

## Queue Rules

1. When multiple topics arise, add to queue
2. Present ONE topic at a time
3. After topic resolved, announce next topic from queue
4. User can ask to see queue at any time

## Queue Announcement Format

```
[Current topic resolved]

Next topic in queue: [Brief description]

1. Proceed with this topic
2. Skip to different topic (show queue)
3. Clear queue, discuss something else
```

## Showing the Queue

When user asks "what's in the queue" or similar:

```
## Current Queue ([N] topics)

1. [Topic A] - [one-line description]
2. [Topic B] - [one-line description]
3. [Topic C] - [one-line description]

Which topic to discuss next?
```

## Numbering Convention

- Use numbers first (1, 2, 3...)
- Use letters for sub-items if needed (1a, 1b, 1c...)

## Rules

- Maximum 5 topics in queue (if more, ask user to prioritize)
- Topics older than current session can be cleared with user permission
- Always give user control over queue order
