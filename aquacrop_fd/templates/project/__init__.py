from pathlib import Path

TEMPLATEFILE = (Path(__file__).parent / 'Template.PRO').resolve()


def format_aquacrop_project(data_files, aquacrop_data, outfile):
    template = TEMPLATEFILE.read_text()

    paths = {}
    for name, path in data_files.items():
        paths[name] = {
            'parent': path.parent,
            'name': path.name
        }
    paths['DATA'] = aquacrop_data

    fields = {
        'first_day_sim': 100,
        'last_day_sim': 200,
        'first_day_crop': 101,
        'last_day_crop': 199,
        'paths': paths,
        'soil_type': 'SandClayLoam',
        'crop_name': 'Maize'
    }

    template_formatted = template.format(**fields)

    outfile.write_text(template_formatted)
