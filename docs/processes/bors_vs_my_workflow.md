how about this. am i not doing any of these?\                                             

  Boris Cherny                                                                              
  @bcherny                                                                                    I'm Boris and I created Claude Code. I wanted to quickly share a few tips for using       
  Claude Code, sourced directly from the Claude Code team. The way the team uses Claude     
  is different than how I use it. Remember: there is no one right way to use Claude         
  Code -- everyones' setup is different. You should experiment to see what works for        
  you!                                                                                      
  3:32 PM · Jan 31, 2026                                                                    
  ·                                                                                         
  7.6M                                                                                      
  Views                                                                                     
  Relevant                                                                                  
  View quotes                                                                               
                                                                                            
  Boris Cherny                                                                              
  @bcherny                                                                                  
  ·                                                                                         
  Jan 31                                                                                    
  1. Do more in parallel                                                                    
                                                                                            
  Spin up 3–5 git worktrees at once, each running its own Claude session in parallel.       
  It's the single biggest productivity unlock, and the top tip from the team.               
  Personally, I use multiple git checkouts, but most of the Claude Code team prefers        
  worktrees --                                                                              
  Show more                                                                                 
  Boris Cherny                                                                              
  @bcherny                                                                                  
  ·                                                                                         
  Jan 31                                                                                    
  2. Start every complex task in plan mode. Pour your energy into the plan so Claude        
  can 1-shot the implementation.                                                            
                                                                                            
  One person has one Claude write the plan, then they spin up a second Claude to review     
  it as a staff engineer.                                                                   
                                                                                            
  Another says the moment something goes sideways, they                                     
  Show more                                                                                 
  Boris Cherny                                                                              
  @bcherny                                                                                  
  ·                                                                                         
  Jan 31                                                                                    
  3. Invest in your http://CLAUDE.md. After every correction, end with: "Update your        
  http://CLAUDE.md so you don't make that mistake again." Claude is eerily good at          
  writing rules for itself.                                                                 
                                                                                            
  Ruthlessly edit your http://CLAUDE.md over time. Keep iterating                           
  Show more                                                                                 
  Boris Cherny                                                                              
  @bcherny                                                                                  
  ·                                                                                         
  Jan 31                                                                                    
  4. Create your own skills and commit them to git. Reuse across every project.             
                                                                                            
  Tips from the team:                                                                       
  - If you do something more than once a day, turn it into a skill or command               
  - Build a /techdebt slash command and run it at the end of every session to find and      
  kill duplicated code                                                                      
  Show more                                                                                 
  From code.claude.com                                                                      
  Boris Cherny                                                                              
  @bcherny                                                                                  
  ·                                                                                         
  Jan 31                                                                                    
  5. Claude fixes most bugs by itself. Here's how we do it:                                 
                                                                                            
  Enable the Slack MCP, then paste a Slack bug thread into Claude and just say "fix."       
  Zero context switching required.                                                          
                                                                                            
  Or, just say "Go fix the failing CI tests." Don't micromanage how.                        
                                                                                            
  Point Claude at docker logs to troubleshoot distributed systems -- it's surprisingly      
  capable at this.                                                                          
  Boris Cherny                                                                              
  @bcherny                                                                                  
  ·                                                                                         
  Jan 31                                                                                    
  6. Level up your prompting                                                                
                                                                                            
  a. Challenge Claude. Say "Grill me on these changes and don't make a PR until I pass      
  your test." Make Claude be your reviewer.  Or, say "Prove to me this works" and have      
  Claude diff behavior between main and your feature branch                                 
                                                                                            
  b. After a mediocre fix, say: "Knowing everything you know now, scrap this and            
  implement the elegant solution"                                                           
                                                                                            
  c. Write detailed specs and reduce ambiguity before handing work off. The more            
  specific you are, the better the output 
  
  ---
  ---
● Let me compare directly:

  ---                                                                                         Boris's Tips vs Your Workflow
  Tip: 1. Parallel worktrees                                                                
  You Do This?: ❓ Unknown                                                                  
  Evidence: I haven't seen you run multiple sessions. Do you?
  ────────────────────────────────────────
  Tip: 2. Plan mode for complex tasks
  You Do This?: ✅ YES
  Evidence: 4D Framework, EnterPlanMode, structured PRDs before implementation
  ────────────────────────────────────────
  Tip: 3. Invest in CLAUDE.md
  You Do This?: ✅✅ STRONG
  Evidence: Your CLAUDE.md is 500+ lines with 28 DDs, architecture rules, protocols
  ────────────────────────────────────────
  Tip: 4. Create skills, commit to git
  You Do This?: ✅✅ STRONG
  Evidence: .claude/skills/ with qa-management-layer, dialogue-engine, testing, fix-workflow
  ────────────────────────────────────────
  Tip: 5. Claude fixes bugs by itself
  You Do This?: ⚠️ OPPOSITE
  Evidence: DD-22 Stop-and-Discuss: "Never loop through fixes without user"
  ────────────────────────────────────────
  Tip: 6. Level up prompting
  You Do This?: ⚠️ PARTIAL
  Evidence: Structured specs yes, but not "grill me" / "prove it works" patterns
  ---
  Where You're Strong

  Tips 3 & 4 — you're ahead of most users.

  Your CLAUDE.md + Skills setup is more sophisticated than what Boris describes. You have:  
  - Layered context (CLAUDE.md → Skills → Step references)
  - Self-updating rules via defect log
  - Versioned protocols committed to git

  ---
  Where You Might Be Leaving Value

  Tip 1: Parallel Worktrees

  Boris says this is "the single biggest productivity unlock."

  Do you run multiple Claude sessions on different features simultaneously?

  # Example setup:
  git worktree add ../feature-1 feature/branch-1
  git worktree add ../feature-2 feature/branch-2
  git worktree add ../feature-3 feature/branch-3

  # Then 3 terminals, each running Claude in different worktree

  If not, you could be 3-5x faster on parallel-able work.

  ---
  Tip 5: Bug Fixing Philosophy

  Boris: "Just say 'fix.' Zero context switching."

  You: "STOP → REPORT → DISCUSS → PROCEED" (DD-22)

  These are opposite philosophies.

  Boris's approach: Trust Claude to iterate, intervene only when needed.

  Your approach: Don't trust Claude to iterate, intervene at every step.

  Your approach is more controlled (fewer runaway fixes), but potentially slower.

  Question for you: Has DD-22 saved you from bad fixes, or does it mostly just add friction?

  If Claude's fixes are usually right, you might be over-controlling.
  If Claude's fixes are often wrong, DD-22 is correct.

  ---
  Tip 6: Specific Prompting Patterns

  Boris mentions:
  - "Grill me on these changes and don't make a PR until I pass your test"
  - "Prove to me this works"
  - "Knowing everything you know now, scrap this and implement the elegant solution"        

  I don't see these in your workflow. You have structure (great), but not these
  adversarial/reflective prompts.

  Could add to your Skills:
  ## Review Prompts (add to testing skill?)
  - After implementation: "Grill me on this implementation. What could break?"
  - After mediocre fix: "Knowing everything now, what's the elegant solution?"
  - Before PR: "Prove to me this works - diff behavior between main and this branch"        

  ---
  The One You Should Try First

  Parallel worktrees. If you're not doing this, it's the highest-leverage change.

  Your workflow is already sophisticated for single-threaded work. But 3-5 parallel sessions
   = multiplicative, not additive.

  ---
  Summary
  ┌─────────────────────┬───────────────────────────────────────────────┐
  │      Category       │                  Your Status                  │
  ├─────────────────────┼───────────────────────────────────────────────┤
  │ CLAUDE.md           │ ✅ Already excellent                          │
  ├─────────────────────┼───────────────────────────────────────────────┤
  │ Skills              │ ✅ Already excellent                          │
  ├─────────────────────┼───────────────────────────────────────────────┤
  │ Plan mode           │ ✅ Already doing                              │
  ├─────────────────────┼───────────────────────────────────────────────┤
  │ Parallel execution  │ ❓ Probably not - big opportunity             │
  ├─────────────────────┼───────────────────────────────────────────────┤
  │ Bug fix autonomy    │ ⚠️ Opposite philosophy - intentional tradeoff │
  ├─────────────────────┼───────────────────────────────────────────────┤
  │ Adversarial prompts │ ⚠️ Could add to toolkit                       │
  └─────────────────────┴───────────────────────────────────────────────┘
  You're doing 4/6 well. The question is whether parallel worktrees and loosening DD-22     
  would help or hurt your specific workflow.