#!/usr/bin/env python3
"""
Jennifer Eye 👁️ — Menubar app voor macOS
Maakt een screenshot, vraagt een beschrijving, stuurt het naar Jennifer.
"""

import rumps
import subprocess
import AppKit
import tempfile
import base64
import json
import os
import logging
import threading
from datetime import datetime

import requests

# === CONFIGURATIE ===
HOOK_URL = "https://jennifer.code42.nl/hooks/screenshot"
HOOK_TOKEN = "07406efaf9b4bf6cc1b31ce51c4eb91daa03a9029db013ac4f1b701f741eeced"

# === LOGGING ===
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "jennifer-eye.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("jennifer-eye")


class JenniferEyeApp(rumps.App):
    def __init__(self):
        super().__init__("👁️", quit_button="Afsluiten")
        self.menu = [
            rumps.MenuItem("📸 Screenshot naar Jennifer", callback=self.take_screenshot),
            rumps.MenuItem("📸 Selectie naar Jennifer", callback=self.take_selection),
            None,  # separator
        ]
        log.info("Jennifer Eye gestart")

    def _capture_and_send(self, selection=False):
        """Screenshot maken en versturen."""
        mode = "selectie" if selection else "volledig scherm"
        log.info(f"Screenshot starten ({mode})")

        png_path = tempfile.mktemp(suffix=".png")

        try:
            # Screenshot maken
            cmd = ["screencapture"]
            if selection:
                cmd.append("-i")
            cmd.append(png_path)

            log.debug(f"Commando: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            log.debug(f"screencapture returncode: {result.returncode}")

            if result.returncode != 0:
                log.warning(f"screencapture failed: {result.stderr}")
                rumps.notification("Jennifer Eye", "Fout", f"screencapture mislukt: {result.stderr}")
                return

            if not os.path.exists(png_path) or os.path.getsize(png_path) == 0:
                log.info("Screenshot geannuleerd (leeg bestand)")
                rumps.notification("Jennifer Eye", "Geannuleerd", "Geen screenshot gemaakt.")
                return

            orig_size = os.path.getsize(png_path)
            log.info(f"Screenshot opgeslagen: {png_path} ({orig_size} bytes)")

            # Resize naar max 1440px breed (blijft PNG)
            resized_path = png_path + ".resized.png"
            subprocess.run(
                ["sips", "--resampleWidth", "1440", png_path, "--out", resized_path],
                capture_output=True,
            )

            if os.path.exists(resized_path) and os.path.getsize(resized_path) > 0:
                send_path = resized_path
                send_size = os.path.getsize(resized_path)
                log.info(f"Geresized: {orig_size} → {send_size} bytes (PNG 1440px)")
                os.unlink(png_path)
            else:
                send_path = png_path
                send_size = orig_size
                log.warning("Resize mislukt, origineel gebruiken")

            # Focus pakken zodat het dialoogvenster bovenaan komt
            AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(True)

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
                log.info("Gebruiker heeft geannuleerd")
                rumps.notification("Jennifer Eye", "Geannuleerd", "Screenshot niet verstuurd.")
                return

            text = response.text.strip() or "(geen beschrijving)"
            log.info(f"Beschrijving: {text}")

            # Versturen in achtergrond
            threading.Thread(target=self._send, args=(send_path, text), daemon=True).start()

        except Exception as e:
            log.exception(f"Fout bij screenshot: {e}")
            rumps.notification("Jennifer Eye", "Fout", str(e))

    def _send(self, filepath, text):
        """Screenshot naar Jennifer sturen via webhook."""
        try:
            file_size = os.path.getsize(filepath)
            log.info(f"Bezig met versturen... ({file_size} bytes)")

            with open(filepath, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            payload_size = len(image_data)
            log.debug(f"Base64 payload: {payload_size} chars")

            log.info(f"POST naar {HOOK_URL}")
            resp = requests.post(
                HOOK_URL,
                json={"text": text, "image": image_data},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {HOOK_TOKEN}",
                },
                timeout=30,
            )

            log.info(f"Response: HTTP {resp.status_code} — {resp.text[:200]}")

            if resp.ok:
                rumps.notification(
                    "Jennifer Eye 👁️",
                    "Verstuurd!",
                    f"Jennifer kijkt mee: \"{text[:50]}\"",
                )
            else:
                log.error(f"Server error: {resp.status_code} {resp.text}")
                rumps.notification("Jennifer Eye", "Fout", f"HTTP {resp.status_code}: {resp.text[:100]}")

        except requests.exceptions.ConnectionError as e:
            log.error(f"Verbindingsfout (Tailscale aan?): {e}")
            rumps.notification("Jennifer Eye", "Verbindingsfout", "Kan server niet bereiken. Staat Tailscale aan?")
        except requests.exceptions.Timeout:
            log.error("Timeout bij versturen")
            rumps.notification("Jennifer Eye", "Timeout", "Server reageerde niet binnen 30s.")
        except Exception as e:
            log.exception(f"Onverwachte fout bij versturen: {e}")
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
    log.info(f"=== Jennifer Eye start {datetime.now().isoformat()} ===")
    log.info(f"Hook URL: {HOOK_URL}")
    log.info(f"Log file: {LOG_FILE}")
    JenniferEyeApp().run()
