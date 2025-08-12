import io, csv, datetime as dt

def parse_patrot_csv(file_storage):
    # Very lightweight parser; expects columns like: Date, Employee, Hours (decimal)
    data = {}
    stream = io.StringIO(file_storage.stream.read().decode('utf-8-sig'))
    reader = csv.DictReader(stream)
    for row in reader:
        date_str = (row.get('Date') or row.get('date') or '').strip()
        hours = float((row.get('Hours') or row.get('hours') or '0').strip() or 0)
        try:
            d = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                d = dt.datetime.strptime(date_str, "%m/%d/%Y").date()
            except ValueError:
                continue
        data[d] = data.get(d, 0.0) + hours
    return data  # {date: total_hours}
