# Cook Universality Construction - Task List

This document tracks the gap between our current implementation and Cook's proof that Rule 110 is Turing complete.

## Current State vs. Cook's Construction

Our implementation uses ad-hoc boolean/arithmetic gate encodings with small, bounded patterns. Cook's proof uses a cyclic tag system (CTS) encoded via glider interactions on an infinite periodic "ether" background.

## Tasks

### COOK-1: Define CTS-based computational model per Cook
**Status:** Pending  
**Problem:** We implement ad-hoc boolean/arithmetic gates, not the cyclic tag system (CTS) that Cook uses to prove universality.  
**Action:** Research Cook's CTS encoding scheme and design a CTS-based computational model to replace our current gate-based approach.

### COOK-2: Adopt ether + glider package initial conditions
**Status:** Pending  
**Problem:** We start from small, bespoke patterns with zero padding. Cook's construction uses a long ether background with precisely spaced glider packages and delimiters.  
**Action:** Implement ether pattern generation and glider package placement according to Cook's specifications.

### COOK-3: Implement phase/spacing scheduler for glider collisions
**Status:** Pending  
**Problem:** No phase alignment or spacing control. Cook's collisions are timing-critical and phase-dependent.  
**Action:** Build a scheduler that maintains phase alignment and ensures glider collisions occur at the correct times.

### COOK-4: Rebuild gates as Cook glider interactions
**Status:** Pending  
**Problem:** Our "gates" are local static patterns. Cook derives logic from orchestrated glider collisions.  
**Action:** Replace static gate patterns with glider-based logic gates that use Cook's proven glider interaction patterns.

### COOK-5: Support unbounded/dynamic tape (no edge artifacts)
**Status:** Pending  
**Problem:** Finite-width arrays with zero boundaries cause truncation/reflection. Cook assumes effectively infinite medium.  
**Action:** Implement dynamic tape extension or infinite boundary conditions to avoid edge artifacts.

### COOK-6: Move output semantics to CTS/glider-derived reads
**Status:** Pending  
**Problem:** We read fixed offsets after fixed steps. Cook reads results from CTS/glider evolution.  
**Action:** Implement CTS output extraction that reads results from the evolving glider system rather than fixed positions.

### COOK-7: Align encodings with proven packages; add validation
**Status:** Pending  
**Problem:** Our encodings aren't tied to the published universal glider packages and aren't validated against them.  
**Action:** Replace custom encodings with Cook's proven glider packages and add validation tests.

### COOK-8: Add long-run visualization to verify ether/glider integrity
**Status:** Pending  
**Problem:** Current visualization is short-run/bounded and doesn't check ether stability, phase coherence, or long-run CTS evolution.  
**Action:** Extend visualization to show ether patterns, glider trajectories, collision points, and verify long-run correctness.

## References

- Cook, M. (2004). "Universality in Elementary Cellular Automaton Rule 110"
- Related papers on Rule 110 glider patterns and cyclic tag systems
