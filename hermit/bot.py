import re
import textwrap

from rivescript import RiveScript
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile


class ShellObject(object):
    """A Bourne Shell object handler for RiveScript."""
    _objects = {}

    def __init__(self, debug=False):
        self.debug = debug

    def shellcheck(self, source):
        source = textwrap.dedent(source)
        # create a named tmp file
        tmp = NamedTemporaryFile()
        # write source to tmp file
        tmp.write('#!/bin/sh\n'.encode('utf-8'))
        tmp.write(source.encode('utf-8'))
        tmp.flush()
        # shellcheck tmp file
        proc = Popen(["/usr/local/bin/shellcheck", tmp.name], stdout=PIPE)
        result = proc.stdout.read().decode('utf-8')
        tmp.close()
        if result.strip():
            # raise exception if errors found
            raise Exception(result +
                            '\n----------\n\n' +
                            source.replace('\n\n', '\n'))
        # return source if tests passed.
        return source

    def load(self, name, code):
        source = "\n".join(code)
        source = self.shellcheck(source)
        self._objects[name] = source

    def call(self, rs, name, user, fields):
        if not name in self._objects:
            return "[ERR: Object Not Found]"
        script = b'# User Variables\n'
        script += b'PATH=/usr/sbin:/usr/local/sbin:/usr/bin:/usr/local/bin\n'
        vars = rs.get_uservars(user)
        for key, value in vars.items():
            if type(value) != str:
                continue
            elif key.startswith('__'):
                continue
            script += f'{key}="{value}"\n'.encode('utf-8')
        script += b'\n# Script\n'
        script += textwrap.dedent(self._objects[name]).encode('utf-8')
        if not self.debug:
            proc = Popen(["sh"], stdin=PIPE, stdout=PIPE)
            proc.stdin.write(script)
            proc.stdin.close()
            result = proc.stdout.read().decode('utf-8')
            if proc.stderr:
                error = proc.stderr.read().decode('utf-8')
            else:
                error = ''
            if not error.strip():
                return result.strip()
            else:
                if not result.strip():
                    return error
            return result + '\n' + error
        return '```\n' + script.decode('utf-8').strip() + '\n```'


class HermitBot(object):
    def __init__(self, data_path, debug=False):
        self._bot = None
        self._debug = debug
        self._data_path = data_path
        self.reload()

    def reload(self):
        self._bot = RiveScript(utf8=True)
        self._bot.unicode_punctuation = re.compile(r'[.!?;:]')
        self._bot.set_handler("sh", ShellObject(debug=self._debug))
        self._bot.load_directory(self._data_path)
        self._bot.sort_replies()

    def set_debug(self, state):
        self._debug = state
        self._bot.set_handler("sh", ShellObject(debug=state))

    def process_interrupts(self, message):
        message = message.lower()
        if message == 'reload':
            self.reload()
            raise Exception('reloaded')
        elif message == 'debug on':
            self.set_debug(True)
            raise Exception('debug is on')
        elif message == 'debug off':
            self.set_debug(False)
            raise Exception('debug is off')
        return None

    def reply(self, message):
        try:
            self.process_interrupts(message)
        except Exception as e:
            return ''.join(e.args)
        return self._bot.reply('user', message)
