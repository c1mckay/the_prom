import sys

sys.path.insert(0, "/root/py_prom_exporter/app/project")

if __name__ == '__main__':
    from project import app
    # kick_off app
    app.run()
