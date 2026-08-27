#!/usr/bin/env python3
import subprocess
import os
import signal

def kill():
    try:
        out = subprocess.check_output(['pgrep', '-f', 'tv_emulator.py']).decode().strip().split()
        for pid in out:
            os.kill(int(pid), signal.SIGTERM)
            print(f"Killed {pid}")
    except Exception:
        pass

if __name__ == "__main__":
    kill()
