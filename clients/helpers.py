from datetime import datetime

def now_ts() -> int:
  return int(datetime.utcnow().timestamp()) * 1000