  CODING PATTERNS
  
  Impact Assessment Plan                                                                  
                                                                                          
  For each fix, I need to check:                                                          
  1. Who calls this code? (find all usage)                                                  2. What depends on current behavior? (existing tests, other components)                 
  3. What will break? (tests, integrations, assumptions)                                  
  4. Migration path? (old data, backward compatibility)     