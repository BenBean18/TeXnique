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
    - [ ] Toggle to disable skipping?
- [x] Start at the same time
- [x] View others' current score
- [x] Send score and problem when completed
- [x] Store latest problem solved in leaderboard
- [x] Allow staying in game even after reload (need a way to get current problem index, note: has to account for skipping, maybe we can store it in the leaderboard also as last problem solved?)
- [x] Allow joining a game late
- [x] Only allow person who created game to start it
- [x] Only allow person who created game to delete it
- [x] View others' current problem and time spent so far
- [x] Allow viewing who is currently in a game
- [x] Don't allow users to join multiple games
- [x] Timed mode, ends simultaneously for everyone
- [x] Show leaderboard at end

TODO:
- [ ] Make multiplayer its own button
- [ ] Make it look nicer
- [ ] At end of game, show time it took everyone for each individual problem
- [ ] Add more problems
- [ ] Make deleting a game actually end it for everyone
- [ ] Visible feedback for when an action fails (e.g. create, start, delete) instead of silent failure
    - [ ] Move start to a request instead of a socket message
- [ ] Allow going back to view previous problems you missed

- [ ] Server restart = logged out, need a more permanent storage method
- [ ] Usernames can be duplicated + no way to prove authentication