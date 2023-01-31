import os

class Config(object):

    API_ID = int(os.environ.get("API_ID", 20960655))

    API_HASH = str(os.environ.get("API_HASH", "0266b63175fe226f5b9caa12d9c91003"))

    BOT_TOKEN = str(os.environ.get("BOT_TOKEN", "5963630341:AAHkLqm76c4Iqp-A3UrVSSdRN3FNw8V_x38"))
    
    OWNER_ID = int(os.environ.get("OWNER_ID", 284134017))

    AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "284134017").split())


    # SUPPORT_GROUP = str(os.environ.get("SUPPORT_GROUP", "https://t.me/+i_RT6WI3YnxjMDZi"))

    DB_URL = str(os.environ.get("DB_URL", "mongodb+srv://thoughtsstream:Selfdevelop8@cluster0.vvwwadh.mongodb.net/?retryWrites=true&w=majority"))
    
    DB_NAME = str(os.environ.get("DB_NAME", "vladyslavius"))
    
    LOG_GROUP = int(os.environ.get("LOG_GROUP", "-1001831216052"))

    BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", True))

