"""Standalone macOS launcher. Starts a local Vonza server and opens its UI in a browser.

This source entry point is compiled into the macOS .app by PyInstaller.
The application doesn't require the user to install Python or use Terminal.
"""
from __future__ import annotations

import os
import threading
import webbrowser

import server


def open_browser(port: int) -> None:
    url = f"http://127.0.0.1:{port}/"
    # Allow the local server a moment to enter its accept loop.
    timer = threading.Timer(0.65, lambda: webbrowser.open(url, new=1))
    timer.daemon = True
    timer.start()


def main() -> None:
    os.environ["VONZA_HOST"] = "127.0.0.1"  # Never expose the local dev server to the network.
    # Keep the API optional: the owner can configure the key after first launch.
    server.main(on_ready=open_browser)


if __name__ == "__main__":
    main()
