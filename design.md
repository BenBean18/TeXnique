Done:
- [x] Pick a username
- [x] Create a game, have ID returned
- [x] Join a game with specific ID and listen to game events
    - [x] Listen to events:
        - [x] start: game is started (should be synced for everyone)
        - [x] solve: someone else solved a problem, reports their current problem and score
    - [x] Publish game events:
        - [x] solve: i solved a problem
- [x] Sync problems between everyone in a group
    - [ ] Leave a toggle to disable this?
- [x] Start at the same time
- [x] View others' current score
- [x] Send score and problem when completed
- [x] Store latest problem solved in leaderboard
- [x] Allow staying in game even after reload (need a way to get current problem index, note: has to account for skipping, maybe we can store it in the leaderboard also as last problem solved?)
- [x] Allow joining a game late
- [x] Only allow person who created game to start it
- [x] Only allow person who created game to delete it
- [x] View others' current problem and time spent so far

TODO:
- [ ] Make multiplayer its own button
- [ ] Make it look nicer
- [ ] Allow viewing who has currently joined a game
- [ ] Timed mode
- [ ] At end of game, show time it took everyone for each individual problem
- [ ] Add more problems
- [ ] Make deleting a game actually end it for everyone

- [ ] Server restart = logged out, need a more permanent storage method
- [ ] Usernames can be duplicated + no way to prove authentication