"""
  //.  ...   ..      ///.     //.
 ///\\\ \\\   \\    ///\\\   ///
///  \\  \\\   \\  ///  \\  /// //
\\\  //   \\\  //  \\\  //  \\\//  ./
 \\\//     \\\//    \\\//    \\\' //
  \\\         \\\    \\\      \\\//
   '''         '''    '''      '''
  ..---===[[ PyP3 Setup ]]===---...
"""
import re
import os
noColorama = False
try:
    from colorama import Fore, Style, init
except ImportError:
    noColorama = True


class Terminal:
    """ Class formatting messages using colorama to specific visual tokens

        dependency: Colorama
        using: PYPE_LOG_NO_COLORS environment variable
    """

    # shortcuts for colorama codes
    if noColorama:
        SB = RST = LR = LG = LB = LM = R = G = B = C = Y = W = ""
    else:
        SB = Style.BRIGHT
        RST = Style.RESET_ALL
        LR = Fore.LIGHTRED_EX
        LG = Fore.LIGHTGREEN_EX
        LB = Fore.LIGHTBLUE_EX
        LM = Fore.LIGHTMAGENTA_EX
        R = Fore.RED
        G = Fore.GREEN
        B = Fore.BLUE
        C = Fore.CYAN
        Y = Fore.YELLOW
        W = Fore.WHITE

    # dictionary replacing string sequences with colorized one
    sdict = {

        r">>> ":
            SB + G + r">>> " + RST,
        r"!!! ":
            SB + R + r"!!! " + RST,
        r"--- ": SB + C + r"--- " + RST,
        r"*** ": SB + LM + r"*** " + RST,
        r"  - ": SB + Y + r"  - " + RST,
        r" [ ": SB + LG + r" [ " + RST,
        r" ]": SB + LG + r" ]" + RST,
        r"{ %(name)s }": SB + LB + r"{ %(name)s }" + RST,
        r"!!! ERR: %(asctime)s >>> { %(name)s }: ":
            SB + LR + r"!!! ERR: %(asctime)s >>> { %(name)s }: " + RST,
        r"!!! CRI: %(asctime)s >>> { %(name)s }: ":
            SB + R + r"!!! CRI: %(asctime)s >>> { %(name)s }: " + RST
    }

    def __init__(self):
        if not noColorama:
            init()

    def _multiple_replace(self, text, adict):
        """Replace multiple tokens defined in dict """
        # type: (str, dict) -> str
        rx = re.compile('|'.join(map(re.escape, adict)))

        def one_xlat(match):
            return adict[match.group(0)]

        return rx.sub(one_xlat, text)

    def echo(self, message, debug=False):
        # type (str, bool) -> None
        print(self.log(message, debug))

        return message

    def log(self, message, debug=False):
        """Return color formatted message"""
        # if we dont want colors, just print raw message
        if os.environ.get('PYPE_LOG_NO_COLORS', None) is not None:
            message = re.sub(r'\[(.*)\]', '[ ' + self.SB + self.W +
                             r'\1' + self.RST + ' ]', message)
        message = self._multiple_replace(message + self.RST, self.sdict)

        return message
