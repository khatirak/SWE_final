# NYUAD Bazaar -  Instructions on how to run the app

## Frontend
When running on frontend, you'll get a message like
```
You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://10.228.253.234:3000
```
Run the 'on your network' option on your phone to see app view
```
cd frontend
npm install (ONLY AFTER A PULL FOR THE FIRST TIME - ONLY NEEDED ONCE)
npm start
```
## Backend
 Be in the root directory
 ```
uvicorn backend.main:app --reload
 ```
