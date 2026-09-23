# captures — raw captures

## Naming scheme

```
YYYY-MM-DD_<tag-id>_<purpose>_<rate>.<ext>
```

Examples:

```
2026-09-25_tag03_boot-refresh_20MHz.csv
2026-09-25_tag03_boot-refresh_20MHz.sr
2026-09-25_tag03_overview_2MHz.sr
```

`<tag-id>` is the running number of the test object. **Tag 01 is the
reference unit** and never appears here.

---

## What goes into git

| Type | Git | Reason |
|---|---|---|
| `.sr` (sigrok native) | ✅ if < 20 MB | lossless and compact |
| raw `.csv` | ❌ | several hundred MB, reproducible from `.sr` |
| `*_transactions.txt` | ✅ | the actual result, small |
| `*_init_sequence.py` | ✅ | the actual result |
| `*_blocks.csv` | ✅ | small |

The `.gitignore` already implements this. Large CSVs stay local.

---

## Every capture needs an entry in `../HISTORY.md`

At least:

- date, tag number, sample rate, channel assignment
- how the refresh was triggered (battery / NFC / other)
- whether anything came at all
- what the decoder made of it

**An empty capture is a result too** and gets documented.

---

## Procedure

See `../docs/capture-protocol.md`.
