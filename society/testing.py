import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, ""),
]

STATIC_ROOT  = [
    os.path.join(BASE_DIR, "static"),
]

print ("ROOT", STATIC_ROOT)
print ("FILE", STATICFILES_DIRS)