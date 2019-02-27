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
noColorama = False
try:
    from colorama import Fore, Style, init
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
    else:
        _SB = Style.BRIGHT
        _RST = Style.RESET_ALL
        _LR = Fore.LIGHTRED_EX
        _LG = Fore.LIGHTGREEN_EX
        _LB = Fore.LIGHTBLUE_EX
        _LM = Fore.LIGHTMAGENTA_EX
        _R = Fore.RED
        _G = Fore.GREEN
        _B = Fore.BLUE
        _C = Fore.CYAN
        _Y = Fore.YELLOW
        _W = Fore.WHITE

    # dictionary replacing string sequences with colorized one
    _sdict = {

        r">>> ":
            _SB + _G + r">>> " + _RST,
        r"!!! ":
            _SB + _R + r"!!! " + _RST,
        r"--- ": _SB + _C + r"--- " + _RST,
        r"*** ": _SB + _LM + r"*** " + _RST,
        r"  - ": _SB + _Y + r"  - " + _RST,
        r" [ ": _SB + _LG + r" [ " + _RST,
        r" ]": _SB + _LG + r" ]" + _RST,
        r"{ %(name)s }": _SB + _LG + r"{ %(name)s }" + _RST,
        r"!!! ERR: %(asctime)s >>> { %(name)s }: ":
            _SB + _LR + r"!!! ERR: %(asctime)s >>> { %(name)s }: " + _RST,
        r"!!! CRI: %(asctime)s >>> { %(name)s }: ":
            _SB + _R + r"!!! CRI: %(asctime)s >>> { %(name)s }: " + _RST
    }

    def __init__(self):
        if not noColorama:
            init()

    def _multiple_replace(self, text, adict):
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
        # type: (str, dict) -> str
        rx = re.compile('|'.join(map(re.escape, adict)))

        def one_xlat(match):
            return adict[match.group(0)]

        return rx.sub(one_xlat, text)

    def echo(self, message, debug=False):
        """ Print colorized message to stdout.

            :param message: message to be colorized
            :type message: string
            :return: colorized message
            :rtype: string

        """
        colorized = self.log(message)
        print(colorized)

        return colorized

    def log(self, message):
        """ Return color formatted message.

            If environment variable ``PYPE_LOG_NO_COLORS`` is set to
            whatever value, message will be formatted but not colorized.

            :param message: message to be colorized
            :type message: string
            :return: colorized message
            :rtype: string

        """
        # if we dont want colors, just print raw message
        if os.environ.get('PYPE_LOG_NO_COLORS', None) is not None:
            message = re.sub(r'\[(.*)\]', '[ ' + self._SB + self._W +
                             r'\1' + self._RST + ' ]', message)
        message = self._multiple_replace(message + self._RST, self._sdict)

        return message
