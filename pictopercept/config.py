import uuid

class Config:
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_PARTITIONED = True

    # This yet to be tested:
    CSRF_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SECURE = True
