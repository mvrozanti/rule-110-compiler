# Pipeline

```
BF source                    e.g. "+++."
   |
   v  compiler/bf.py + compiler/bf_to_tm.py        (Phase 6)
   |  unary tape encoding; each BF op -> constant number of TM states
   v
Turing Machine               (states, alphabet, transitions, tape)
   |
   v  compiler/tm_to_cts.py                        (Phase 5)
   |  Neary-Woods 2006 reduction; polynomial blowup in step count
   v
Cyclic Tag System            (alphabet, appendants, tape)
   |
   v  compiler/cts_to_r110.py                      (Phase 4)
   |  place verified Cook gliders at Cook ether-distances;
   |  emit region_map for visualization
   v
Rule 110 initial bitstring
   |
   v  runtime/evolve.py                            (Phase 7)
   |  step under Rule 110 until halting-glider configuration detected
   v
Rule 110 final state
   |
   v  runtime/decode.py                            (Phase 7)
   |  identify surviving gliders -> CTS state -> TM state -> BF tape
   v
Decoded output               "\x03"
```

The inverse correspondence is what the visualization shows: every glider in
the Rule 110 spacetime is owned by exactly one CTS symbol, which is owned by
exactly one TM step, which is owned by exactly one BF instruction. The
`region_map` emitted at encode time carries these relationships forward so the
viz can color and link without runtime glider tracking.
