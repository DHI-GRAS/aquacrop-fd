from pathlib import Path

IRRIGATIONFILE = (Path(__file__).parent / 'Irrigation.IRR').resolve()


def format_irrigation_file(outfile, depletion_of_raw=100):
    template = IRRIGATIONFILE.read_text()
    template_formatted = template.format(depletion_of_raw=depletion_of_raw)
    outfile.write_text(template_formatted)
