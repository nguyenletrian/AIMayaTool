from __future__ import absolute_import
import os
import xml.etree.ElementTree as ET

def normalize_names(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        values = value
    else:
        values = str(value).splitlines()
    return [str(item).strip() for item in values if str(item).strip()]

def pair_names(sources, targets):
    source_names, target_names = normalize_names(sources), normalize_names(targets)
    if len(source_names) != len(target_names):
        raise ValueError("Sources and targets must have the same number of entries.")
    return list(zip(source_names, target_names))

def replacement_map(sources, targets):
    return dict(pair_names(sources, targets))

def transfer_xml_names(source_path, target_path, sources, targets):
    source_path, target_path = os.path.abspath(source_path), os.path.abspath(target_path)
    replacements = replacement_map(sources, targets)
    tree = ET.parse(source_path)
    root = tree.getroot()
    for elem in root.iter():
        for attr, value in list(elem.attrib.items()):
            if value in replacements:
                elem.set(attr, replacements[value])
        if elem.text:
            stripped = elem.text.strip()
            if stripped in replacements:
                prefix = elem.text[:len(elem.text)-len(elem.text.lstrip())]
                suffix = elem.text[len(elem.text.rstrip()):]
                elem.text = prefix + replacements[stripped] + suffix
    tree.write(target_path, encoding="utf-8", xml_declaration=True)
    return target_path
