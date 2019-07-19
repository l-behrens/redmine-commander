#!/usr/bin/env python
import rofi
import sys

class rofi_redmine(rofi.Rofi):

    def custom_select(self, prompt, options, *fns, message="", select=None):
        # Replace newlines and turn the options into a single string.
        optionstr = '\n'.join(option.replace('\n', ' ') for option in options)

        # Set up arguments.
        args = ['rofi', '-dmenu', '-p', prompt, '-format', 'i']
        if select is not None:
            args.extend(['-selected-row', str(select)])

        # Key bindings to display.
        display_bindings = []

        # Configure the key bindings.
        user_keys = set()
        kwargs={'key%i' % (index+1): value for index, value in enumerate(fns)}
        for k, v in kwargs.items():
            # See if the keyword name matches the needed format.
            if not k.startswith('key'):
                continue
            try:
                keynum = int(k[3:])
            except ValueError:
                continue

            # Add it to the set.
            key, action = v
            user_keys.add(keynum)
            args.extend(['-kb-custom-{0:s}'.format(k[3:]), key])
            if action:
                display_bindings.append("<b>{0:s}</b>: {1:s}".format(key, action))

        # And the global exit bindings.
        exit_keys = set()
        next_key = 10
        for key in self.exit_hotkeys:
            while next_key in user_keys:
                next_key += 1
            exit_keys.add(next_key)
            args.extend(['-kb-custom-{0:d}'.format(next_key), key])
            next_key += 1

        # Add any displayed key bindings to the message.
        message = message or ""
        if display_bindings:
            message += "\n" + "  ".join(display_bindings)
        message = message.strip()

        # If we have a message, add it to the arguments.
        if message:
            args.extend(['-mesg', message])

        # Add in common arguments.
        args.extend(self._common_args(**kwargs))

        # Run the dialog.
        returncode, stdout = self._run_blocking(args, input=optionstr)

        # Figure out which option was selected.
        stdout = stdout.strip()
        index = int(stdout) if stdout else -1

        # And map the return code to a key.
        if returncode == 0:
            key = 0
        elif returncode == 1:
            key = -1
        elif returncode > 9:
            key = returncode - 9
            if key in exit_keys:
                raise SystemExit()
        else:
            self.exit_with_error("Unexpected rofi returncode {0:d}.".format(results.returncode))

        # And return.
        return index, key



if __name__ == "__main__":
    pass
#    global r
#    r=rofi_redmine()
#




