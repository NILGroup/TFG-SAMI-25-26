# uvicorn main:app --reload

import uvicorn
from API import app

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=5555)
