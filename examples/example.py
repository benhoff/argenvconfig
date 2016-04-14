from argenvconfig import ConfigInterface

c = ConfigInterface()
c.add_argument('--test')
c.add_argument('--test2')
c.add_settings_file('/test/path')

settings_kwargs = c.get_kwargs()
print(settings_kwargs)
