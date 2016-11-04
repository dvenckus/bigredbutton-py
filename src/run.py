# run a test server
from app.bigredbutton import app

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000, threaded=True)
