# Corrections

This folder is how listings change. Each night the updater reads every `.json` file here and applies
anything it hasn't applied before (it remembers in `state/applied.json`). Nothing changes just because
a web page changed: a person confirms first, usually by phone.

Make a new file for each batch, e.g. `2026-10-20-chautauqua-calls.json`. It's a list:

```json
[
  {"id": "st-susan-center-jamestown", "checked": "2026-10-20", "how": "called, spoke to the front desk"},

  {"id": "westfield-community-food-pantry", "checked": "2026-10-20", "how": "called",
   "set": {"hours": {"tue": [["13:00","14:30"]], "wed": [["09:00","15:00"]]},
           "hours_text": "Tue 1-2:30pm, Wed 9am-3pm"}},

  {"id": "some-closed-pantry", "remove": true, "how": "church office says it closed in August"},

  {"add": {"id": "new-pantry-sherman", "name": "...", "category": "food", "county": "Chautauqua",
           "tags": ["pantry"], "description": "...", "address": "...", "city": "Sherman", "state": "NY",
           "zip": "14781", "phone": "...", "hours": {}, "hours_text": "...", "source_name": "Phone call",
           "source_url": "", "confidence": "high"}, "how": "found on a call"}
]
```

- A listing with only `id` + `checked` = "confirmed, everything is right". It gets marked checked today and high confidence.
- `set` changes only the fields you list. Hours use 24-hour times.
- Listing ids are in the call vault (`%%id: ...%%` under each heading) and in `data.json`.
- Claude can write these files for you from the call vault.
