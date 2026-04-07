import requests
import json
import os

API_KEY = os.environ.get("SMARTSHEET_API_KEY", "")
BASE_URL = "https://api.smartsheet.com/2.0"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

WORKSPACE_ID  = "5033698753046404"
SOURCE_SHEET_ID = 4615626883551108

# Source column IDs
COL = {
    "GC Number":        8231505636315012,
    "GC Start Day":     5838968334274436,
    "Graphics Provider":7527818194538372,
    "Ceiling Type":     7809293171249028,
    "Floor Type":       139100055883652,
    "Location Type":    4642699683254148,
    "Ameritech Status": 8110562905640836,
    "Re-Lamp":          5416755869208452,
}

def req(method, path, body=None, params=None):
    url = f"{BASE_URL}{path}"
    r = requests.request(method, url, headers=HEADERS, json=body, params=params)
    if r.status_code not in (200, 201):
        raise Exception(f"{method} {path} → {r.status_code}: {r.text[:300]}")
    return r.json()

# ── 1. Create the sheet ────────────────────────────────────────────────────────
print("Creating Dashboard Metrics sheet...")
sheet_payload = {
    "name": "Dollar Tree - Dashboard Metrics",
    "columns": [
        {"title": "Category",     "type": "TEXT_NUMBER", "primary": True},
        {"title": "Count",        "type": "TEXT_NUMBER"},
        {"title": "Section",      "type": "TEXT_NUMBER"},
        {"title": "Chart Label",  "type": "TEXT_NUMBER"},
        {"title": "Notes",        "type": "TEXT_NUMBER"},
    ]
}
result = req("POST", f"/workspaces/{WORKSPACE_ID}/sheets", sheet_payload)
sheet_id = result["result"]["id"]
print(f"  Sheet created: ID {sheet_id}")

# Get column IDs from the new sheet
sheet_data = req("GET", f"/sheets/{sheet_id}")
cols = {c["title"]: c["id"] for c in sheet_data["columns"]}
print(f"  Columns: {list(cols.keys())}")

# ── 2. Create cross-sheet references ──────────────────────────────────────────
print("\nCreating cross-sheet references...")
ref_ids = {}
for name, col_id in COL.items():
    ref_name = f"DT {name}"
    body = {
        "name": ref_name,
        "sourceSheetId": SOURCE_SHEET_ID,
        "startColumnId": col_id,
        "endColumnId": col_id
    }
    r = req("POST", f"/sheets/{sheet_id}/crosssheetreferences", body)
    ref_ids[name] = r["result"]["name"]
    print(f"  {ref_name} → {r['result']['name']}")

# ── 3. Build rows ──────────────────────────────────────────────────────────────
def cell(col_name, value=None, formula=None):
    c = {"columnId": cols[col_name]}
    if formula:
        c["formula"] = formula
    else:
        c["value"] = value if value is not None else ""
    return c

def row(category, formula, section, label, notes="", to_bottom=True):
    return {
        "toBottom": to_bottom,
        "cells": [
            cell("Category",    value=category),
            cell("Count",       formula=formula),
            cell("Section",     value=section),
            cell("Chart Label", value=label),
            cell("Notes",       value=notes),
        ]
    }

def blank(section_title):
    """Blank separator row that labels the upcoming section."""
    return {
        "toBottom": True,
        "cells": [
            cell("Category",    value=f"── {section_title} ──"),
            cell("Count",       value=None),
            cell("Section",     value=section_title),
            cell("Chart Label", value="HEADER"),
            cell("Notes",       value="Section header — exclude from chart range"),
        ]
    }

rows = []

# ── A: GC Workload ────────────────────────────────────────────────────────────
rows.append(blank("GC Workload"))
rows.append(row("GC 1",
    f'=COUNTIF({{DT GC Number}}, 1)',
    "GC Workload", "GC 1",
    "Stores assigned to General Contractor #1"))
rows.append(row("GC 2",
    f'=COUNTIF({{DT GC Number}}, 2)',
    "GC Workload", "GC 2",
    "Stores assigned to General Contractor #2"))
rows.append(row("GC 3",
    f'=COUNTIF({{DT GC Number}}, 3)',
    "GC Workload", "GC 3",
    "Stores assigned to General Contractor #3"))

# ── B: Graphics Provider ──────────────────────────────────────────────────────
rows.append(blank("Graphics Provider"))
rows.append(row("ARG",
    '=COUNTIF({DT Graphics Provider}, "ARG")',
    "Graphics Provider", "ARG",
    "Stores using ARG graphics"))
rows.append(row("Clarity",
    '=COUNTIF({DT Graphics Provider}, "Clarity")',
    "Graphics Provider", "Clarity",
    "Stores using Clarity graphics"))

# ── C: Start Night ────────────────────────────────────────────────────────────
rows.append(blank("Start Night"))
rows.append(row("Sunday Night",
    '=COUNTIF({DT GC Start Day}, "Sunday Night")',
    "Start Night", "Sunday",
    "Installs starting Sunday night"))
rows.append(row("Tuesday Night",
    '=COUNTIF({DT GC Start Day}, "Tuesday Night")',
    "Start Night", "Tuesday",
    "Installs starting Tuesday night"))
rows.append(row("Monday Night",
    '=COUNTIF({DT GC Start Day}, "Monday Night")',
    "Start Night", "Monday",
    "Installs starting Monday night"))

# ── D: Location Type ──────────────────────────────────────────────────────────
rows.append(blank("Location Type"))
rows.append(row("Strip",
    '=COUNTIF({DT Location Type}, "Strip")',
    "Location Type", "Strip",
    "Strip mall locations"))
rows.append(row("Free Standing",
    '=COUNTIF({DT Location Type}, "Free Standing")',
    "Location Type", "Free Standing",
    "Free-standing store locations"))
rows.append(row("Mall",
    '=COUNTIF({DT Location Type}, "Mall")',
    "Location Type", "Mall",
    "Mall-based locations"))

# ── E: Ceiling Type ───────────────────────────────────────────────────────────
rows.append(blank("Ceiling Type"))
rows.append(row("Drop / Suspended",
    '=COUNTIF({DT Ceiling Type}, "Drop / Suspended")',
    "Ceiling Type", "Drop/Suspended",
    "Drop or suspended ceilings"))
rows.append(row("Open",
    '=COUNTIFS({DT Ceiling Type}, CONTAINS("Open", @cell)) + COUNTIFS({DT Ceiling Type}, CONTAINS("OPEN", @cell))',
    "Ceiling Type", "Open",
    "Open ceilings (any case)"))
rows.append(row("Drop Tile",
    '=COUNTIF({DT Ceiling Type}, "DROP CEILING WITH TILES")',
    "Ceiling Type", "Drop Tile",
    "Drop ceiling with tiles"))

# ── F: Floor Type ─────────────────────────────────────────────────────────────
rows.append(blank("Floor Type"))
rows.append(row("PC",
    '=COUNTIF({DT Floor Type}, "PC")',
    "Floor Type", "PC",
    "Polished concrete floors"))
rows.append(row("LVT 2nd Gen",
    '=COUNTIF({DT Floor Type}, "LVT 2nd Gen")',
    "Floor Type", "LVT 2nd Gen",
    "Luxury vinyl tile 2nd generation"))
rows.append(row("LVT 1st Gen",
    '=COUNTIF({DT Floor Type}, "LVT 1st Gen")',
    "Floor Type", "LVT 1st Gen",
    "Luxury vinyl tile 1st generation"))
rows.append(row("LVT 3rd Gen",
    '=COUNTIF({DT Floor Type}, "LVT 3rd Gen")',
    "Floor Type", "LVT 3rd Gen",
    "Luxury vinyl tile 3rd generation"))

# ── G: Ameritech Status Pipeline ──────────────────────────────────────────────
rows.append(blank("Status Pipeline"))
rows.append(row("New Project",
    '=COUNTIF({DT Ameritech Status}, "NEWPROJECT")',
    "Status Pipeline", "New Project",
    "Stores in NEWPROJECT status"))
rows.append(row("Scheduled",
    '=COUNTIF({DT Ameritech Status}, "SCHEDULED")',
    "Status Pipeline", "Scheduled",
    "Stores in SCHEDULED status"))
rows.append(row("In Progress",
    '=COUNTIF({DT Ameritech Status}, "INPROGRESS")',
    "Status Pipeline", "In Progress",
    "Stores actively being worked"))
rows.append(row("Tech Complete",
    '=COUNTIF({DT Ameritech Status}, "TECHCOMPL")',
    "Status Pipeline", "Tech Complete",
    "Stores where tech work is done"))
rows.append(row("Billing",
    '=COUNTIF({DT Ameritech Status}, "BILLING")',
    "Status Pipeline", "Billing",
    "Stores in billing process"))
rows.append(row("Invoiced",
    '=COUNTIF({DT Ameritech Status}, "INVOICED")',
    "Status Pipeline", "Invoiced",
    "Stores fully invoiced"))
rows.append(row("Cancelled",
    '=COUNTIF({DT Ameritech Status}, "CANCELLED")',
    "Status Pipeline", "Cancelled",
    "Stores cancelled"))

# ── H: Re-Lamp ────────────────────────────────────────────────────────────────
rows.append(blank("Re-Lamp"))
rows.append(row("Yes",
    '=COUNTIF({DT Re-Lamp}, "YES")',
    "Re-Lamp", "Re-Lamp: Yes",
    "Stores requiring re-lamp work"))
rows.append(row("No",
    f'=COUNT({{DT Re-Lamp}}) - COUNTIF({{DT Re-Lamp}}, "YES")',
    "Re-Lamp", "Re-Lamp: No",
    "Stores not requiring re-lamp"))

# ── 4. Add rows in batches of 10 ──────────────────────────────────────────────
print(f"\nAdding {len(rows)} rows in batches...")
BATCH = 10
for i in range(0, len(rows), BATCH):
    batch = rows[i:i+BATCH]
    result = req("POST", f"/sheets/{sheet_id}/rows", batch)
    added = len(result.get("result", []))
    print(f"  Rows {i+1}–{i+len(batch)}: {added} added")

# ── 5. Print chart range reference ────────────────────────────────────────────
sheet_url = f"https://app.smartsheet.com/sheets/{sheet_id}"
print(f"""
Done!

  Sheet: Dollar Tree - Dashboard Metrics
  ID:    {sheet_id}
  URL:   {sheet_url}

  Chart ranges to use in dashboard widget:
  ┌─────────────────────┬──────────────────────────────────┬─────────────────┐
  │ Chart               │ Chart Type                       │ Row range       │
  ├─────────────────────┼──────────────────────────────────┼─────────────────┤
  │ GC Workload         │ Donut / Pie                      │ rows 2–4        │
  │ Graphics Provider   │ Donut                            │ rows 6–7        │
  │ Start Night         │ Bar (horizontal)                 │ rows 9–11       │
  │ Location Type       │ Pie                              │ rows 13–15      │
  │ Ceiling Type        │ Pie                              │ rows 17–19      │
  │ Floor Type          │ Pie                              │ rows 21–24      │
  │ Status Pipeline     │ Bar (horizontal) / Stacked bar   │ rows 26–32      │
  │ Re-Lamp             │ Donut                            │ rows 34–35      │
  └─────────────────────┴──────────────────────────────────┴─────────────────┘

  For each chart widget in the dashboard:
    1. Click + > Chart
    2. Select Data > choose "Dollar Tree - Dashboard Metrics"
    3. Columns: Category (col 1) + Count (col 2)
    4. Rows: use the range above (skip header rows labeled "── Section ──")
""")
