import os

class Config(object):

    API_ID = int(os.environ.get("API_ID", 20960655))

    API_HASH = str(os.environ.get("API_HASH", "0266b63175fe226f5b9caa12d9c91003"))

    BOT_TOKEN = str(os.environ.get("BOT_TOKEN", "6046558159:AAHbVK5VsHI9j1gBzQ7OpB1QAEiROeqnQdo"))
    
    OWNER_ID = int(os.environ.get("OWNER_ID", 284134017))

    DB_URL = str(os.environ.get("DB_URL", "mongodb+srv://thoughtsstream:Selfdevelop8@cluster0.vvwwadh.mongodb.net/?retryWrites=true&w=majority"))
    
    DB_NAME = str(os.environ.get("DB_NAME", "vladyslavius"))
    
    # LOG_GROUP = int(os.environ.get("LOG_GROUP", "-859771439"))

    LOG_GROUP = int(os.environ.get("LOG_GROUP", "-1001801500302")) # Main group

    BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", True))


