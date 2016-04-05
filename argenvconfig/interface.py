# command line, env, config, default
class ArgEnvConfig:
    """
    Interface class which presents a unified API to user
    """
    def __init__(self):
        pass

    def add_argument(self, *args, **kwargs):
        pass

    def parser_args(self, *args, **kwargs):
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
