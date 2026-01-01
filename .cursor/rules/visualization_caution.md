# Visualization Code Quality Rule

## IMPERATIVE: Extreme Caution with Visualization Code

### Core Principle
**BE EXTREMELY PESSIMISTIC** about any visualization code changes. Assume they are wrong until proven correct through rigorous testing and user validation.

### Required Process for Visualization Changes

#### 1. Pre-Implementation Scrutiny
- **Question every assumption**: What exactly should be visible? What should be colored? What represents information flow vs structure?
- **Define success criteria**: What specific visual result do we want? How will we know it's correct?
- **Get user confirmation**: "Is this what you want to see?" before implementing

#### 2. Implementation Rules
- **NO assumptions**: Do not assume "this looks right" or "this should work"
- **Simple over complex**: Prefer simple, obvious solutions over clever optimizations
- **Test incrementally**: Change one thing, test immediately, get feedback
- **Document intent**: Every color, every region must have a clear, documented purpose

#### 3. Validation Requirements
- **User validation mandatory**: Do NOT claim "fixed" without explicit user confirmation
- **Multiple test cases**: Test with different programs, different scenarios
- **Visual verification**: Show actual screenshots/results, not just code
- **Regression testing**: Ensure previous working features still work

#### 4. Error Prevention
- **Conservative defaults**: When in doubt, show less rather than more
- **Clear labeling**: Every visual element must be clearly identifiable
- **Toggle controls**: Allow users to turn elements on/off to verify correctness
- **Debug information**: Provide ways for users to inspect what's being shown

#### 5. Communication Rules
- **Admit uncertainty**: "I'm not sure this is correct" is better than "This should work"
- **Ask for clarification**: If requirements are ambiguous, ask immediately
- **Show, don't tell**: Demonstrate actual results, don't just describe them
- **Accept criticism**: User feedback trumps implementation assumptions

### Consequences of Violation
- **Do not claim "fixed"** unless user explicitly confirms
- **Re-implement if wrong** - no excuses, no "it was close"
- **Accept that visualization code is fragile** and requires extra scrutiny

### Success Criteria
- User says "Yes, this shows exactly what I want to see"
- Visual result matches user's mental model precisely
- No ambiguity about what represents what
- User can explain what they're seeing and why it's correct

### Remember
**The user is the ultimate arbiter of correctness.** Code that "looks right to the developer" is not good enough. Only user validation counts.




