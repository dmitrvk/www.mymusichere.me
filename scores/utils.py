from operator import methodcaller

def parse_lilypond_header(filename: str) -> dict:
    """Parse header in LilyPond file and return dict with header fields."""
    with open(filename) as f:
        header = dict()
        reading_header = False
        for line in f:
            line = line.strip()
            if reading_header:
                if '}' in line:
                    reading_header = False
                    break
                elif '=' in line:
                    field, value = map(methodcaller('strip'), line.split('='))
                    if len(field) > 0 and len(value) > 0:
                        if '"' in value:
                            value = value.strip('"')
                        if len(value) > 0:
                            header[field.lower()] = value
            elif '\header' in line:
                reading_header = True
        return header

