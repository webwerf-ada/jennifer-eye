# Jennifer Eye 👁️

Menubar app voor macOS — stuur screenshots naar Jennifer met een beschrijving.

## Snel starten

```bash
pip3 install rumps requests
python3 jennifer_eye.py
```

Het 👁️ icoontje verschijnt in je menubar. Klik erop voor:
- **Screenshot naar Jennifer** — volledig scherm
- **Selectie naar Jennifer** — selecteer een gebied

Je krijgt een tekstveld waar je beschrijft wat je wilt weten. Jennifer analyseert het screenshot en stuurt haar reactie via Telegram.

## Als .app bouwen (optioneel)

```bash
pip3 install py2app
python3 setup.py py2app
```

De app verschijnt in `dist/Jennifer Eye.app`. Sleep naar Applications en voeg toe aan Login Items voor auto-start.

## Vereisten

- macOS
- Python 3
- Tailscale (verbinding met openclaw-vm)
- Screen Recording permissie (macOS vraagt dit automatisch)
