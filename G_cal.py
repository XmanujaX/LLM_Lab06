# gcal_setup.py
from google_auth_oauthlib.flow import InstalledAppFlow

# We need permission to view and edit events
SCOPES = ["https://www.googleapis.com/auth/calendar"]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

# Save the token so we don't have to log in every time
with open("token.json", "w") as token:
    token.write(creds.to_json())
    
print("✅ Authentication successful! token.json has been created.")