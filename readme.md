Try to redo backend in python, why not

### next step:
1. ~~ddb trigger when a session is created~~
  - ~~if it has a profilePicture~~
  - ~~save picture to s3~~
  - ~~update session and spotifyProfile records displayPicture properties with s3 url~~

### Refactor ops:
1. ~~profile and session sharing properties, probably could remove one of these tables~~
  - ~~User table, Profile table~~
2. Don't do any auth my side, use spotify auth.
  - No sessions, user must auth with spotify every time (does automatically after first time I think right?)
  - SpotifyTable
  - This makes most sense for sure. But I'm trying stuff out.
  - Flow is
    1. User clicks start - goes to spotify
    2. Allows app access to their spotify, redirect to login with code
    3. My page submits code on load
    4. Save spotifyId + token to backend, sign jwt for Frontend to use
    5. Next time user logs in I just overwrite the spotify record in ddb
    6. Handle user refresh? go back to validatejwt / expiry flow
    7. Could still do persistent sessions? nah all good