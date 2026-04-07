import requests
import json
import sys
import os

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("SMARTSHEET_API_KEY", "")
if not API_KEY:
    print("ERROR: Set SMARTSHEET_API_KEY environment variable before running.")
    sys.exit(1)

SHEET_ID = "4615626883551108"
BASE_URL = "https://api.smartsheet.com/2.0"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ── Summary Field Definitions ─────────────────────────────────────────────────
SUMMARY_FIELDS = [

    # ── Program Scale ──────────────────────────────────────────────────────────
    {
        "title": "Total Stores",
        "type": "TEXT_NUMBER",
        "formula": '=COUNT([Store #]:[Store #])'
    },
    {
        "title": "Total Contract Value",
        "type": "TEXT_NUMBER",
        "formula": '=SUM([Approved Bid Price]:[Approved Bid Price])'
    },
    {
        "title": "Total Re-Lamp Value",
        "type": "TEXT_NUMBER",
        "formula": '=SUM([Approved Re-Lamp Pricing]:[Approved Re-Lamp Pricing])'
    },
    {
        "title": "Avg Bid Per Store",
        "type": "TEXT_NUMBER",
        "formula": '=AVG([Approved Bid Price]:[Approved Bid Price])'
    },
    {
        "title": "Avg Gross Sq Ft",
        "type": "TEXT_NUMBER",
        "formula": '=AVG([Gross Sq Ft]:[Gross Sq Ft])'
    },
    {
        "title": "Stores w/ Re-Lamp",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Re-Lamp]:[Re-Lamp], "YES")'
    },

    # ── Scheduling ─────────────────────────────────────────────────────────────
    {
        "title": "Stores Scheduled",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([GC Project Start Date]:[GC Project Start Date], ISDATE(@cell))'
    },
    {
        "title": "Stores Not Yet Scheduled",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([GC Project Start Date]:[GC Project Start Date], NOT(ISDATE(@cell)))'
    },
    {
        "title": "Earliest Start Date",
        "type": "DATE",
        "formula": '=MIN([GC Project Start Date]:[GC Project Start Date])'
    },
    {
        "title": "Latest Start Date",
        "type": "DATE",
        "formula": '=MAX([GC Project Start Date]:[GC Project Start Date])'
    },
    {
        "title": "Sunday Night Starts",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([GC Start Day]:[GC Start Day], "Sunday Night")'
    },
    {
        "title": "Tuesday Night Starts",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([GC Start Day]:[GC Start Day], "Tuesday Night")'
    },
    {
        "title": "Monday Night Starts",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([GC Start Day]:[GC Start Day], "Monday Night")'
    },

    # ── Completion Status ──────────────────────────────────────────────────────
    {
        "title": "Installs Completed",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Install Completed]:[Install Completed], 1)'
    },
    {
        "title": "Installs Billed",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Install Billed]:[Install Billed], 1)'
    },
    {
        "title": "Pct Complete",
        "type": "TEXT_NUMBER",
        "formula": '=IFERROR(COUNTIF([Install Completed]:[Install Completed], 1) / COUNT([Store #]:[Store #]) * 100, 0)'
    },
    {
        "title": "Pct Billed",
        "type": "TEXT_NUMBER",
        "formula": '=IFERROR(COUNTIF([Install Billed]:[Install Billed], 1) / COUNT([Store #]:[Store #]) * 100, 0)'
    },

    # ── Ameritech Status Breakdown ─────────────────────────────────────────────
    {
        "title": "Status: New Project",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Ameritech Status]:[Ameritech Status], "NEWPROJECT")'
    },
    {
        "title": "Status: Scheduled",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Ameritech Status]:[Ameritech Status], "SCHEDULED")'
    },
    {
        "title": "Status: In Progress",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Ameritech Status]:[Ameritech Status], "INPROGRESS")'
    },
    {
        "title": "Status: Tech Complete",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Ameritech Status]:[Ameritech Status], "TECHCOMPL")'
    },
    {
        "title": "Status: Billing",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Ameritech Status]:[Ameritech Status], "BILLING")'
    },
    {
        "title": "Status: Invoiced",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Ameritech Status]:[Ameritech Status], "INVOICED")'
    },
    {
        "title": "Status: Cancelled",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Ameritech Status]:[Ameritech Status], "CANCELLED")'
    },

    # ── GC & Crew Breakdown ────────────────────────────────────────────────────
    {
        "title": "GC 1 Stores",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([GC Number]:[GC Number], 1)'
    },
    {
        "title": "GC 2 Stores",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([GC Number]:[GC Number], 2)'
    },
    {
        "title": "GC 3 Stores",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([GC Number]:[GC Number], 3)'
    },
    {
        "title": "ARG Stores",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Graphics Provider]:[Graphics Provider], "ARG")'
    },
    {
        "title": "Clarity Stores",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Graphics Provider]:[Graphics Provider], "Clarity")'
    },

    # ── Physical Attributes ────────────────────────────────────────────────────
    {
        "title": "Drop Suspended Ceilings",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Ceiling Type]:[Ceiling Type], "Drop / Suspended")'
    },
    {
        "title": "Drop Tile Ceilings",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Ceiling Type]:[Ceiling Type], "DROP CEILING WITH TILES")'
    },
    {
        "title": "Open Ceilings",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIFS([Ceiling Type]:[Ceiling Type], CONTAINS("Open", @cell)) + COUNTIFS([Ceiling Type]:[Ceiling Type], CONTAINS("OPEN", @cell))'
    },
    {
        "title": "Scissor Lift Required",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Scisssor Left Required]:[Scisssor Left Required], "YES")'
    },
    {
        "title": "Free Standing Locations",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Location Type]:[Location Type], "Free Standing")'
    },
    {
        "title": "Strip Locations",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Location Type]:[Location Type], "Strip")'
    },
    {
        "title": "Mall Locations",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Location Type]:[Location Type], "Mall")'
    },
    {
        "title": "Floor LVT 1st Gen",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Floor Type]:[Floor Type], "LVT 1st Gen")'
    },
    {
        "title": "Floor LVT 2nd Gen",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Floor Type]:[Floor Type], "LVT 2nd Gen")'
    },
    {
        "title": "Floor LVT 3rd Gen",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Floor Type]:[Floor Type], "LVT 3rd Gen")'
    },
    {
        "title": "Floor PC",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Floor Type]:[Floor Type], "PC")'
    },

    # ── Logistics ─────────────────────────────────────────────────────────────
    {
        "title": "Materials Delivered",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Dollar Tree Order items Delivery Date]:[Dollar Tree Order items Delivery Date], ISDATE(@cell))'
    },
    {
        "title": "Materials Not Yet Delivered",
        "type": "TEXT_NUMBER",
        "formula": '=COUNTIF([Dollar Tree Order items Delivery Date]:[Dollar Tree Order items Delivery Date], NOT(ISDATE(@cell)))'
    },

]

# ── Create Fields ─────────────────────────────────────────────────────────────
def create_summary_fields():
    url = f"{BASE_URL}/sheets/{SHEET_ID}/summary/fields"

    success_count = 0
    fail_count = 0

    for field in SUMMARY_FIELDS:
        payload = [field]
        response = requests.post(url, headers=HEADERS, json=payload)

        if response.status_code == 200:
            result = response.json()
            created = result.get("result", [{}])
            title = created[0].get("title", field["title"]) if created else field["title"]
            print(f"  OK  {title}")
            success_count += 1
        else:
            print(f"  FAIL  {field['title']} -- {response.status_code}: {response.text[:120]}")
            fail_count += 1

    print(f"\nDone. {success_count} fields created, {fail_count} failed.")

if __name__ == "__main__":
    print(f"Creating {len(SUMMARY_FIELDS)} Sheet Summary fields on sheet {SHEET_ID}...\n")
    create_summary_fields()
