# ::
#   //.  ...   ..      ///.     //.
#  ///\\\ \\\   \\    ///\\\   ///
# ///  \\  \\\   \\  ///  \\  /// //
# \\\  //   \\\  //  \\\  //  \\\//  ./
#  \\\//     \\\//    \\\//    \\\' //
#   \\\         \\\    \\\      \\\//
#    '''         '''    '''      '''
#   ..---===[[ PyP3 Setup ]]===---...
#
import re
import os
import sys
noColorama = False
try:
    from colorama import Fore, Style, init, ansitowin32
except ImportError:
    noColorama = True


class Terminal:
    """ Class formatting messages using colorama to specific visual tokens.

        If :mod:`Colorama` is not found, it will still work, but without
        colors.

        - dependency: :mod:`Colorama`
        - using: **PYPE_LOG_NO_COLORS** environment variable
    """

    # shortcuts for colorama codes
    if noColorama:
        _SB = _RST = _LR = _LG = _LB = _LM = _R = _G = _B = _C = _Y = _W = ""
        _LY = ""
    else:
        _SB = Style.BRIGHT
        _RST = Style.RESET_ALL
        _LR = Fore.LIGHTRED_EX
        _LG = Fore.LIGHTGREEN_EX
        _LB = Fore.LIGHTBLUE_EX
        _LM = Fore.LIGHTMAGENTA_EX
        _LY = Fore.LIGHTYELLOW_EX
        _R = Fore.RED
        _G = Fore.GREEN
        _B = Fore.BLUE
        _C = Fore.CYAN
        _Y = Fore.YELLOW
        _W = Fore.WHITE

    # dictionary replacing string sequences with colorized one
    _sdict = {

        r">>> ": _SB + _G + r">>> " + _RST,
        r"!!!(?!\sCRI|\sERR)": _SB + _R + r"!!! " + _RST,
        r"\-\-\- ": _SB + _C + r"--- " + _RST,
        r"\*\*\*(?!\sWRN)": _SB + _LM + r"***" + _RST,
        r"\*\*\* WRN": _SB + _LY + r"*** WRN" + _RST,
        r"  \- ": _SB + _Y + r"  - " + _RST,
        r"\[ ": _SB + _LG + r"[ " + _RST,
        r"\]": _SB + _LG + r"]" + _RST,
        r"{":  _LG + r"{",
        r"}":  r"}" + _RST,
        r"\(": _LY + r"(",
        r"\)": r")" + _RST,
        r"!!! ERR: ":
            _SB + _LR + r"!!! ERR: " + _RST,
        r"!!! CRI: ":
            _SB + _R + r"!!! CRI: " + _RST,
        r"(?i)failed": _SB + _LR + "FAILED" + _RST,
        r"(?i)error": _SB + _LR + "ERROR" + _RST
    }

    def __init__(self):
        if not noColorama:
            init()

    @staticmethod
    def _multiple_replace(text, adict):
        """ Replace multiple tokens defined in dict

            Find and replace all occurances of strings defined in dict is
            supplied string.

            :param text: string to be searched
            :type text: string
            :param adict: dictionary with ``{'search': 'replace'}``
            :type adict: dict
            :return: string with replaced tokens
            :rtype: string

        """
        for r, v in adict.items():
            text = re.sub(r, v, text)

        return text

    @staticmethod
    def echo(message, debug=False):
        """ Print colorized message to stdout.

            :param message: message to be colorized
            :type message: string
            :return: colorized message
            :rtype: string

        """
        if noColorama:
            print(message)
            return message
        if not isinstance(sys.stdout, ansitowin32.StreamWrapper):
            init()
        colorized = Terminal.log(message)
        print(colorized)

        return colorized

    @staticmethod
    def log(message):
        """ Return color formatted message.

            If environment variable ``PYPE_LOG_NO_COLORS`` is set to
            whatever value, message will be formatted but not colorized.

            :param message: message to be colorized
            :type message: string
            :return: colorized message
            :rtype: string

        """
        T = Terminal
        # if we dont want colors, just print raw message
        if os.environ.get('PYPE_LOG_NO_COLORS', None) is not None:
            message = re.sub(r'\[(.*)\]', '[ ' + T._SB + T._W +
                             r'\1' + T._RST + ' ]', message)
        message = T._multiple_replace(message + T._RST, T._sdict)

        return message
