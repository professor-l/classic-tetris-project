# TODO

## Auth

+ Create `WebsiteUser` model
- Discord command `!website`
  - Check if they have a `WebsiteUser` already
  - DM user custom auth link to create an account
- Create `CreateAccountController` controller
  - GET:
    - require an auth token as URL param, tell them to run the command on Discord otherwise
    - Render a form to create username and password
    - Auth key expires 1 hour after generation
  - POST:
    - create AuthUser and WebsiteUser, linking to the User associated with auth token
+ Create `LoginController`
  + GET: login page
  + POST: do login


