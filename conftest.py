# Empty conftest.py at the project root.
# Its presence tells pytest where the project root is and adds this
# directory to sys.path so tests can `import git_heartbeat` regardless
# of how pytest is launched (`pytest`, `python -m pytest`, IDE, etc.).
