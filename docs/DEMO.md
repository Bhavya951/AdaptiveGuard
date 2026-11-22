# Offline interview demo

From the repository root, run:

```sh
python -B demo.py
```

Policy: Feed the cloth snail only when the moisture gauge drops below 6.

| Scenario | History output | Final output |
| --- | --- | --- |
| Earlier assistant report says 7 | violation (label=1) | unresolved_state (label=0) |
| Earlier assistant report says 4 | permitted (label=0) | unresolved_state (label=0) |
| Final turn explicitly reports 7 and asks to act | violation (label=1) | violation (label=1) |

## Three-minute delivery

- **0:00–0:40** Start with the fictional policy and ask what information is needed to make the decision. Run the command and read the first scenario aloud.
- **0:40–1:30** Point out that the same final request receives a violation with the earlier reading and an unresolved decision without it. Explain numeric fallback and why the reason matters.
- **1:30–2:15** Show the identical language with a lower gauge reading. The history decision changes to permitted.
- **2:15–3:00** Show the self-contained final turn and explain why both conditions agree. These cases exercise a known parser path and illustrate information placement.

## Five-minute technical explanation

- **0:00–1:00** Define the unit of prediction and the fictional positive class. Show the policy string and the list of role/text pairs.
- **1:00–2:00** Open C's detect function and trace normalization, request resolution, policy-pattern matching and evidence selection. Both arms call this same function.
- **2:00–3:00** Explain why Phase 1 uses a marker baseline, and give the frozen F1 difference and FPR increase. Describe resampling pairs of predictions together at family level.
- **3:00–4:00** Explain the Phase 2 development input collisions, the empirical ceiling and the effect of mapping unresolved decisions to 0 versus 1.
- **4:00–5:00** Explain why challenge cases informed changes and why independent labels and approval are still needed for the protected holdout.

## Troubleshooting

If Python is missing, use an installed Python 3.11+ interpreter, or try `py -3` on Windows. If demo.py cannot be found, change to the directory containing README.md and run the command again. If modules fail to import, confirm that the extracted `src/` directory sits beside demo.py. Compare the printed reasons as well as numeric labels. The demo needs no packages, environment file, network connection or experiment outputs.
