# Jennifer Eye 👁️

Menubar app voor macOS — stuur screenshots naar Jennifer met een beschrijving.

## Snel starten

```bash
./run.sh
```

Dit maakt automatisch een venv aan, installeert dependencies, en start de app.

Het 👁️ icoontje verschijnt in je menubar. Klik erop voor:
- **Screenshot naar Jennifer** — volledig scherm
- **Selectie naar Jennifer** — selecteer een gebied

Je krijgt een tekstveld waar je beschrijft wat je wilt weten. Jennifer analyseert het screenshot en stuurt haar reactie via Telegram.

## Als .app bouwen (optioneel)

```bash
source .venv/bin/activate
pip install py2app
python setup.py py2app
```

De app verschijnt in `dist/Jennifer Eye.app`. Sleep naar Applications en voeg toe aan Login Items voor auto-start.

## Vereisten

- macOS
- Python 3 (via Homebrew of system)
- Tailscale (verbinding met openclaw-vm)
- Screen Recording permissie (macOS vraagt dit automatisch)
