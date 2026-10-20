# Polaris CropPilot: Usability and Comprehension Test Script (task 5.35)

For tasks 5.36–5.37 (AC-10, AC-11) and the owner's UAT. Run each session one to one, about 15 minutes.

## Before the session

- **Testers:** 3–5 farmers or extension staff from Kalyana-Karnataka (stand-ins if needed: record who). At least one session in Kannada.
- **Device:** a phone with the deployed link open on the welcome page, plus a desktop for one session. Clear any saved language choice first.
- **Do not collect** names, phone numbers, ID numbers or locations (PRD 3.3). Record only a tester code (T1, T2 …), their role and the language used.
- **Say:** "We are testing the app, not you. There are no wrong answers. Please think aloud. I cannot help while you use it, but I can answer questions afterwards."

## Task A: timed journey (AC-10: ≥ 4 of 5 finish in ≤ 5 minutes)

Give the tester a farm card (or let them use their own farm):

> Kalaburagi district · 2 acres 20 guntas · medium black soil · water drains within a day · rain only · last Kharif: tur · "middle path" on risk · sowing on time.

Say: **"Use the app to see which crop it suggests for this farm, then choose the crop you would grow."**
Start the timer at the first tap on Start. Stop it when they have picked a crop under "Your choice".

| Tester | Language | Device | Time (m:ss) | Finished? | Where they hesitated or asked for help |
|---|---|---|---|---|---|
| T1 | | | | | |
| T2 | | | | | |
| T3 | | | | | |
| T4 | | | | | |
| T5 | | | | | |

## Task B: comprehension (AC-11: ≥ 4 of 5 explain "low" and why the top crop ranked first)

Ask on the results screen, without pointing at the answer:

1. **"What does 'Bad year' mean here?"** Pass if they say something like "in a poor season it could be this low, and about one season in ten could be even worse." Fail if they read it as a fixed loss or the most they can lose.
2. **"Why is the first crop at the top?"** Pass if they point to a reason shown (earns most in a typical year, holds up in a bad year, lower chance of loss, and so on).
3. **"Is the app telling you what to grow?"** Pass if they say the choice is theirs, or that it is an estimate to discuss with the RSK or KVK.
4. **"What does 'Loses money in 15 of 100 seasons' mean?"** (Optional, for notes.)
5. **"Was anything confusing or worrying?"** (Open; write the words they use.)

| Tester | Q1 "bad year" | Q2 "why first" | Q3 "whose decision" | Notes and quotes |
|---|---|---|---|---|
| T1 | | | | |
| T2 | | | | |
| T3 | | | | |
| T4 | | | | |
| T5 | | | | |

## Task C: risk setting (feeds A-15, A-16; task 5.38)

Ask the tester to change their answer to **"Play safe"** (tap the "Middle path ✎" chip). For this farm the top crop changes from cotton to tur.
Ask: **"Does that change make sense to you?"** Record yes, no or unsure, and why.

## After the sessions

- Count AC-10 and AC-11 passes; record them in `acceptance_report.md`.
- List every problem seen in at least two sessions; fix those first (task 5.39).
- Kannada sessions: note any word the tester did not understand (input to the R17 native-speaker review).
