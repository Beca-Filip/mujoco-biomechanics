"""Regenerate README Table 2 from the model's male site-position CSV."""

import argparse
import csv
from pathlib import Path


DESCRIPTIONS = {
    'seventh_cervicale': 'Seventh cervical vertebra (C7)',
    'suprasternale': 'Suprasternal notch',
    'acromion': 'Acromion',
    'shoulder_joint_centre': 'Shoulder joint centre',
    'thoracic_joint_centre': 'Thoracic joint centre',
    'midspine_at_tenth_rib_level': 'Midline of the spine at the tenth-rib level',
    'tenth_rib': 'Tenth rib',
    'iliocristale': 'Iliac crest',
    'lumbar_joint_centre': 'Lumbar joint centre',
    'midpoint_between_postero_superior_iliac_spines': 'Midpoint between the posterior superior iliac spines',
    'anterior_superior_iliac_spine': 'Anterior superior iliac spine (ASIS)',
    'symphision': 'Pubic symphysis',
    'hip_joint_centre': 'Hip joint centre',
    'head_vertex': 'Vertex of the head',
    'sellion': 'Sellion (nasal-root landmark)',
    'occiput': 'Occiput (back of the head)',
    'lateral_humeral_epicondyle': 'Lateral humeral epicondyle',
    'medial_humeral_epicondyle': 'Medial humeral epicondyle',
    'olecranion': 'Olecranon',
    'ulnar_styloid': 'Ulnar styloid process',
    'radial_styloid': 'Radial styloid process',
    'second_metacarpal_head': 'Head of the second metacarpal',
    'fifth_metacarpal_head': 'Head of the fifth metacarpal',
    'third_finger_tip': 'Tip of the third (middle) finger',
    'greater_trochanter': 'Greater trochanter of the femur',
    'lateral_femoral_epicondyle': 'Lateral femoral epicondyle',
    'medial_femoral_epicondyle': 'Medial femoral epicondyle',
    'tibiale_head': 'Tibial-head landmark',
    'fibula_head': 'Head of the fibula',
    'sphyrion': 'Sphyrion (medial malleolar landmark)',
    'lateral_malleolus': 'Lateral malleolus',
    'calcaneus': 'Calcaneus (heel)',
    'first_metatarsal_head': 'Head of the first metatarsal',
    'fifth_metatarsal_head': 'Head of the fifth metatarsal',
    'second_toe_tip': 'Tip of the second toe',
    'metatarsal_midpoint': 'Metatarsal midpoint reference site',
}

START = '<!-- BEGIN GENERATED SITE TABLE -->'
END = '<!-- END GENERATED SITE TABLE -->'


def describe(name):
    side = ''
    for prefix in ('left_', 'right_'):
        if name.startswith(prefix):
            side = prefix[:-1].capitalize() + ' '
            name = name[len(prefix):]
            break
    if name.startswith('centre_of_mass_'):
        label = side + name[len('centre_of_mass_'):].replace('_', ' ') + ' centre of mass (reference site)'
        return label[0].upper() + label[1:]
    if name not in DESCRIPTIONS:
        raise ValueError(f'Add a reviewed description for the new site: {name}')
    label = DESCRIPTIONS[name]
    return side + label[0].lower() + label[1:] if side else label


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, help='Write an updated README copy instead of updating the repository README')
    args = parser.parse_args()
    data = args.repo / 'src/mujoco_biomechanics/data'
    with (data / 'site_positions_male.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    names = [row['site name'] for row in rows]
    if not rows or len(names) != len(set(names)):
        raise ValueError('The male site CSV must contain nonempty, unique site names')
    with (data / 'site_positions_female.csv').open(encoding='utf-8-sig', newline='') as stream:
        female = list(csv.DictReader(stream))
    if {(r['site name'], r['segment left/right']) for r in rows} != {(r['site name'], r['segment left/right']) for r in female}:
        raise ValueError('Male and female site names or parent segments differ; review the table scope')
    lines = [
        START,
        '## Anatomical sites',
        '',
        f'The current generator defines {len(rows)} sites, including anatomical landmarks, joint centres, and centre-of-mass reference sites. Table 2 lists their exact model identifiers and parent segments. Numbers follow the row order in `src/mujoco_biomechanics/data/site_positions_male.csv`; they are documentation labels, not MuJoCo site IDs. The female CSV defines the same site names and parent segments.',
        '',
        '**Table 2. Complete site inventory of the generated model.** Existing identifiers, including `symphision` and `olecranion`, are preserved exactly as stored in the CSV.',
        '',
        '| # | Site name | Segment | Anatomical landmark / reference point |',
        '| ---: | --- | --- | --- |',
    ]
    for number, row in enumerate(rows, 1):
        name, segment = row['site name'], row['segment left/right']
        lines.append(f'| {number} | `{name}` | `{segment}` | {describe(name)} |')
    lines.extend([
        '',
        'Regenerate this section from the repository root after changing the site CSV:',
        '',
        '```bash',
        'python scripts/generate_readme_sites.py',
        '```',
        END,
    ])
    readme = args.repo / 'README.md'
    original = readme.read_bytes()
    newline = '\r\n' if b'\r\n' in original else '\n'
    section = newline.join(lines).encode('utf-8')
    if START.encode() in original:
        if original.count(START.encode()) != 1 or original.count(END.encode()) != 1:
            raise ValueError('Ambiguous generated-section markers')
        begin = original.index(START.encode())
        end = original.index(END.encode(), begin) + len(END)
        result = original[:begin] + section + original[end:]
    else:
        anchor = b'## Requirements'
        if original.count(anchor) != 1:
            raise ValueError('Expected exactly one Requirements heading')
        insertion = section + (newline * 2).encode()
        result = original.replace(anchor, insertion + anchor, 1)
        assert result.replace(insertion, b'', 1) == original
    output = args.output or readme
    output.write_bytes(result)
    print(f'Generated {len(rows)} numbered rows; male/female names and segments agree. Updated {output}')


if __name__ == '__main__':
    main()
