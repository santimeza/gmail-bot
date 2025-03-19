Hello :)

Run "./setup.sh" to create environment and start

Once the environment has been successfully created, run "source gmail-bot-env/bin/activate" (linux/mac) or "source gmail-bot-env/Scripts/activate" (windows)

You will need to set up your own google credentials to use this app:

- Go to https://console.cloud.google.com/
- Create a project
- Enable Gmail API
- Create OAuth 2.0 credentials (Desktop App)
- Download the credentials file
- Place it in your working directory and rename credentials.json

Once you're all set up, run "python3 GBotRun.py"
