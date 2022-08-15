SST task output was interpreted as follows:
- column 1 - trial number

- column 3 - trial type. 0=Go, 1=NoGo, 2=null trial (there are 96 Go, 32 NoGo, 128 null)

- column 7 - subject response (keycode). 0=no response.

  - In MRI imager, button box presses of pairs (`3`, `6`), (`4`, `5`), (`2`, `6`), corresponding to keycode pairs (`91`, `94`), (`92`, `93`), (`90`, `94`), or one key shifts for a single trial (`94` -> `95` or `94` -> `93`), if occurring on Go trials, are interpreted as successful Go trials.

  - In behavioral response at a computer keyboard, key presses of (`r`, `l`), (`<`, `>`), corresponding to keycodes (`21`, `15`), (`197`, `198`), if occurring on Go trials, are interpreted as successful Go trials.

  - One-off keypresses of random keys during Go trials are treated as failed Go trials. Keys pressed were `3`, `f`, `u`, corresponding to keycodes `32`, `9`, `24`.

  - Errors in interpreting the keycode during the task are recorded as `9999` and if occurring in during Go trials are treated as failed Go trials.

- column 9 - reaction time. For Go trials, this is the duration.
- column 15 - trial duration (seconds). For NoGo or null trials, this is the duration.
- column 16 - start time of trial (seconds)

Keycodes are interpreted as keys on keyboards as defined by [KbName function of Psychtoolbox](https://github.com/Psychtoolbox-3/Psychtoolbox-3/blob/master/Psychtoolbox/PsychBasic/KbName.m#L334).
