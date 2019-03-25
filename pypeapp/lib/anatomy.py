import re


class Anatomy(object):
    '''
    Needs docstring
    '''

    def _discover(self):
        '''
        arg:

        find and load anatomy templates
        '''

        return anatomy

    def _solve_optional(self, template, data):
        """
        Solving optional elements in template string regarding to available
        keys in used data object

        Arguments:
            template (string): value from toml templates
            data (obj): containing keys to be filled into template
        """
        # print(template)
        # Remove optional missing keys
        pattern = re.compile(r"(<.*?[^{0]*>)[^0-9]*?")
        invalid_optionals = []
        for group in pattern.findall(template):
            try:
                group.format(**data)
            except KeyError:
                invalid_optionals.append(group)
        for group in invalid_optionals:
            template = template.replace(group, "")

        try:
            solved = template.format(**data)

            # solving after format optional in second round
            for catch in re.compile(r"(<.*?[^{0]*>)[^0-9]*?").findall(solved):
                if "{" in catch:
                    # remove all optional
                    solved = solved.replace(catch, "")
                else:
                    # Remove optional symbols
                    solved = solved.replace(catch, catch[1:-1])

            return solved
        except KeyError as e:
            print("_solve_optional: {},"
                  "`template`: {}".format(e, template))
            return template
        except ValueError as e:
            print("Error in _solve_optional: {},"
                  "`template`: {}".format(e, template))

    def _format(self, template, data):
        '''

        return solved, unsolved, partial
        '''

        solved = self._solve_optional(template, data)

        return solved
