# WhisperChain – Final Submission (Week 4 Complete)

This is my completed version of the WhisperChain project. Week 4 added the moderation layer: recipients can flag messages, moderators can review those flags, and freeze bad actors if needed. Logging is also therefore updated. 

## What's New in Week 4 Edition of this project

- Recipients can flag a message they received
- Moderators can view all flagged messages
- Moderators can freeze specific tokens to stop abuse
- Frozen tokens can't be used to send new messages
- Logs now include:
  - MessageFlagged
  - FlaggedMessageReviewed
  - TokenFrozen

##  How to Run

```bash
python main.py
```

## What You Can Do with this porject

- Register as sender/recipient/mod/sysadmin
- Get a one-time-use token
- Send encrypted messages (senders only)
- Read and decrypt messages (recipients only)
- Flag a message if it’s sketchy (recipients)
- Review flagged messages (mods only)
- Freeze a sender’s token (mods only)
- View all logs (mod/sysadmin only)

## Files

(main.py – entry point, interactive menu  
UserRegistration.py – registers users + stores roles  
TokenManager.py – handles token issuing + validation + token freezing (WEEK 4)  
ActionLogger.py – logs who did what  
role_permissions.py – defines who’s allowed to do what, small file  
storage.json – updated live as stuff happens  
logs.txt – all logs go here)

and also:

- crypto_utils.py – encrypts/decrypts messages, creates keypairs