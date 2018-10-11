import re
import os
import platform
'''
TODO: function for reading from toml
TODO: function for writing to toml
TODO: check if shema validate can be used
TODO: check if precaching function can be used
TODO: cached versions of software tomls to ~/.pype/software
'''
platform = platform.system().lower()


class _Dict_to_obj_with_range(dict):
    """ Hiden class

    Converts `dict` dot string object with optional slicing metod

    Output:
        nested dotstring object for example: root.item.subitem.subitem_item
        also nested dict() for example: root["item"].subitem["subitem_item"]

    Arguments:
        dct (dictionary): nested dictionary
        range (list): list of list pairs example:
        (key, list of two int())
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct, range=None):
        for key, value in dct.items():
            if isinstance(value, dict):
                value = _Dict_to_obj_with_range(value, range)

            try:
                cut_from, cut_to = [found[1]
                                    for found in range
                                    if key in found[0]][0]
                self[key] = value[cut_from:cut_to]
            except Exception:
                self[key] = value


def _solve_optional(template, data):
    """ Hiden metod

    Solving optional elements in template string regarding to available
    keys in used data object

    Arguments:
        template (string): value from toml templates
        data (obj): containing keys to be filled into template
    """
    # Remove optional missing keys
    pattern = re.compile(r"<.*?>")
    invalid_optionals = []
    for group in pattern.findall(template):
        try:
            group.format(**data)
        except KeyError:
            invalid_optionals.append(group)
    for group in invalid_optionals:
        template = template.replace(group, "")

    try:
        solved = template.format(platform=platform, **data)

        # Remove optional symbols
        solved = solved.replace("<", "")
        solved = solved.replace(">", "")

        return solved
    except KeyError:
        print("--locals: ", platform)
        print("--template:", template)
        return template


def _slicing(template):
    """ Hiden metod

    finds slicing string in `template` and remove it and returns pair list
    with found 'key' and [range]

    Arguments:
        template (string): value from toml templates
        data (directory): containing keys to be filled into template
    """
    pairs = []
    # patterns
    sliced_key = re.compile(r"^.*{(.*\[.*?\])}")
    slice_only = re.compile(r"\[.*?\]")

    # procedure
    find_sliced = sliced_key.findall(template)
    for i, sliced in enumerate(find_sliced):
        slicing = slice_only.findall(sliced)
        try:
            numbers_get = [
                int(n) for n in slicing[i].replace(
                    "[", ""
                ).replace(
                    "]", ""
                ).split(":")
            ]
            clean_key = sliced.replace(slicing[i], "")
            template = template.replace(slicing[i], "")
            pairs.append((clean_key, numbers_get))
        except ValueError:
            pairs.append(None)
    return template, pairs


def format(template="{template_string}", data=dict()):
    """ Public metod

    Converts `template` string and returns corected string

    Arguments:
        template (string): value from toml templates
        data (directory): containing keys to be filled into template
    """
    template, range = _slicing(template)
    converted = _solve_optional(
        template,
        _Dict_to_obj_with_range(
            dict(data, **os.environ),
            range
        )
    )

    return converted
