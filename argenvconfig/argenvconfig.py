import argparse
from argparse import HelpFormatter
from gettext import gettext as _


# command line, env, config, default
class ArgEnvConfig:
    """
    Interface class which presents a unified API to user
    """
    def __init__(self,
                 prog=None,
                 usage=None,
                 description=None,
                 epilog=None,
                 parents=[],
                 formatter_class=HelpFormatter,
                 prefix_chars='-',
                 fromfile_prefix_chars=None,
                 argument_default=None,
                 conflic_handler='error',
                 add_help=True,
                 allow_abbrev=True):

        # prefer composition over inheritance
        self._arg_parser = argparse.ArgumentParser(prog=prog
                                                   usage=usage,
                                                   description=description,
                                                   epilog=epilog,
                                                   parents=parents,
                                                   formatter_class=formatter_class,
                                                   prefix_chars=prefix_chars,
                                                   fromfile_prefix_chars=fromfile_prefix_chars,
                                                   argument_default=argument,
                                                   conflict_handler=conflic_handler,
                                                   add_help=add_help,
                                                   allow_abbrev=allow_abbrev)

        """
        if action.help is not SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            for subaction in self._iter_indented_subactions(action):
                invocations.append(get_invocation(subaction))

            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length,
                                          action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])
            """
    def add_argument(self, *args, **kwargs):
        chars = self.prefix_chars
        if not args or len(args) == 1 and args[0][0] not in chars:
            if args and 'dest' in kwargs:
                raise ValueError('dest supplied twice for positional argument')
            kwargs = self._get_positional_kwargs(*args, **kwargs)

        # otherwise, we're adding an optional argument
        else:
            kwargs = self._get_optional_kwargs(*args, **kwargs)

        # if no default was supplied, use the parser-level default
        if 'default' not in kwargs:
            dest = kwargs['dest']
            if dest in self._defaults:
                kwargs['default'] = self._defaults[dest]
            elif self.argument_default is not None:
                kwargs['default'] = self.argument_default

        # create the action object, and add it to the parser
        action_class = self._pop_action_class(kwargs)
        if not callable(action_class):
            raise ValueError('unknown action "%s"' % (action_class,))
        action = action_class(**kwargs)

        # raise an error if the action type is not callable
        type_func = self._registry_get('type', action.type, action.type)
        if not callable(type_func):
            raise ValueError('%r is not callable' % (type_func,))

        # raise an error if the metavar does not match the type
        if hasattr(self, "_get_formatter"):
            try:
                self._get_formatter()._format_args(action, None)
            except TypeError:
                raise ValueError("length of metavar tuple does not match nargs")

        return self._add_action(action)
        pass

    def convert_arg_line_to_args(self, arg_line):
        pass

    def parse_args(self, *args, **kwargs):
        pass

    def parse_known_args(self, args=None, namespace=None):
        pass


class ArgumentConfigEnvParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        """
        Added 2 new keyword arguments to the ArgumentParser constructor:

           config --> List of filenames to parse for config goodness
           default_section --> name of the default section in the config file
        """
        self.config_files = kwargs.pop('config',[])  #Must be a list
        self.default_section = kwargs.pop('default_section', 'MAIN')
        self._action_defaults = {}
        super(ArgumentConfigEnvParser, self).__init__(*args, **kwargs)


    def parse_known_args(self, args=None, namespace=None):
        ns, argv = super(ArgumentConfigEnvParser, self).parse_known_args(
            args=args, namespace=namespace)
        config_parser = ConfigParser.SafeConfigParser()
        config_files = [os.path.expanduser(os.path.expandvars(x))
                        for x in self.config_files]
        config_parser.read(config_files)

        for dest, (args, init_dict) in self._action_defaults.items():
            type_converter = init_dict['type']
            default = init_dict['default']
            obj = default

            if getattr(ns, dest, _SENTINEL) is not _SENTINEL: # command line
                obj = getattr(ns, dest)
            else: # not on commandline
                try:  # get from config file
                    obj = config_parser.get(init_dict['section'], dest)
                except _CONFIG_MISSING_OPT_ERRORS: # Nope, not in config file
                    try: # get from environment
                        obj = os.environ[dest.upper()]
                    except KeyError:
                        pass

            if obj is _SENTINEL:
                setattr(ns, dest, None)
            elif obj is argparse.SUPPRESS:
                pass
            else:
                setattr(ns, dest, type_converter(obj))

        return ns, argv

    def parse_args(self, args=None, namespace=None):
        # Blantantly copy argparse.ArgumentParser.parse_args
        #
        # This isn't strictly necessary, but argparse doesn't guarantee
        # that parse_args is implemented on top of parse_known_args
        # so this makes sure of that fact.
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            msg = _('unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))
        return args
