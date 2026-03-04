#!/usr/bin/env python3
"""
Jennifer Eye 👁️ — Menubar app voor macOS
Maakt een screenshot, vraagt een beschrijving, stuurt het naar Jennifer.

Installatie:
    pip3 install rumps requests
    python3 jennifer_eye.py

Of maak er een .app van:
    pip3 install py2app
    python3 setup.py py2app
"""

import rumps
import subprocess
import tempfile
import base64
import json
import os
import requests
import threading

# === CONFIGURATIE ===
HOOK_URL = "https://openclaw-vm.tail66c752.ts.net/hooks/screenshot"
HOOK_TOKEN = "07406efaf9b4bf6cc1b31ce51c4eb91daa03a9029db013ac4f1b701f741eeced"


class JenniferEyeApp(rumps.App):
    def __init__(self):
        super().__init__("👁️", quit_button="Afsluiten")
        self.menu = [
            rumps.MenuItem("📸 Screenshot naar Jennifer", callback=self.take_screenshot),
            rumps.MenuItem("📸 Selectie naar Jennifer", callback=self.take_selection),
            None,  # separator
        ]

    def _capture_and_send(self, selection=False):
        """Screenshot maken en versturen."""
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.close()

        try:
            # Screenshot maken
            cmd = ["screencapture"]
            if selection:
                cmd.append("-i")  # interactieve selectie
            cmd.append(tmp.name)

            result = subprocess.run(cmd, capture_output=True)
            if result.returncode != 0 or not os.path.exists(tmp.name) or os.path.getsize(tmp.name) == 0:
                rumps.notification("Jennifer Eye", "Geannuleerd", "Geen screenshot gemaakt.")
                return

            # Beschrijving vragen
            response = rumps.Window(
                message="Wat wil je dat Jennifer bekijkt?",
                title="Jennifer Eye 👁️",
                default_text="",
                ok="Versturen",
                cancel="Annuleren",
                dimensions=(320, 100),
            ).run()

            if not response.clicked:
                rumps.notification("Jennifer Eye", "Geannuleerd", "Screenshot niet verstuurd.")
                return

            text = response.text.strip() or "(geen beschrijving)"

            # Versturen in achtergrond
            threading.Thread(target=self._send, args=(tmp.name, text), daemon=True).start()

        except Exception as e:
            rumps.notification("Jennifer Eye", "Fout", str(e))

    def _send(self, filepath, text):
        """Screenshot naar Jennifer sturen via webhook."""
        try:
            with open(filepath, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            payload = {"text": text, "image": image_data}

            resp = requests.post(
                HOOK_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {HOOK_TOKEN}",
                },
                timeout=30,
            )

            if resp.ok:
                rumps.notification(
                    "Jennifer Eye 👁️",
                    "Verstuurd!",
                    f"Jennifer kijkt mee: \"{text[:50]}...\"" if len(text) > 50 else f"Jennifer kijkt mee: \"{text}\"",
                )
            else:
                rumps.notification("Jennifer Eye", "Fout", f"HTTP {resp.status_code}: {resp.text[:100]}")

        except Exception as e:
            rumps.notification("Jennifer Eye", "Verzenden mislukt", str(e))
        finally:
            try:
                os.unlink(filepath)
            except OSError:
                pass

    @rumps.clicked("📸 Screenshot naar Jennifer")
    def take_screenshot(self, _):
        self._capture_and_send(selection=False)

    @rumps.clicked("📸 Selectie naar Jennifer")
    def take_selection(self, _):
        self._capture_and_send(selection=True)


if __name__ == "__main__":
    JenniferEyeApp().run()
