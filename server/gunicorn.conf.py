# Gunicorn settings for the droplet. The systemd service starts gunicorn with
# "--config server/gunicorn.conf.py", and gunicorn reads the variables below.
# Gunicorn is the production server; "flask run" is only for development.

# Apache listens on the public ports and forwards requests here. Binding to
# 127.0.0.1 means only programs on the droplet itself can reach gunicorn.
GUNICORN_PORT = 8000
bind = "127.0.0.1:" + str(GUNICORN_PORT)

# Exactly one worker process. The two result caches in app/result_cache.py
# live in process memory, so a second worker would not see results stored by
# the first one.
workers = 1

# One process can still serve several visitors at once by using threads.
# Threads share the process memory, so the caches keep working. Without this,
# one visitor's long research stream would block everyone else.
worker_class = "gthread"
threads = 8

# Seconds a request may run before gunicorn gives up on it. The research and
# generation streams can take a few minutes, well past the default of 30.
STREAM_TIMEOUT_SECONDS = 600
timeout = STREAM_TIMEOUT_SECONDS

# Send logs to stdout and stderr so "journalctl -u circular-concept" shows them.
accesslog = "-"
errorlog = "-"
