# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/11/07
# ~

from prompt_toolkit.application import get_app
from prompt_toolkit.layout import HSplit
from prompt_toolkit.widgets import Button, TextArea, Dialog, Label
from prompt_toolkit.key_binding.key_bindings import KeyBindings, \
    merge_key_bindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, \
    focus_previous
from prompt_toolkit.shortcuts.dialogs import _return_none
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout import Layout
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.defaults import load_key_bindings


def close(event):
    event.app.exit()


def yes_no_dialog(title='', text='', yes_text='Yes', no_text='No', style=None,
                  async_=False):
    def yes_handler():
        get_app().exit(result=True)

    def no_handler():
        get_app().exit(result=False)

    dialog = Dialog(
        title=title,
        body=Label(text=text, dont_extend_height=True),
        buttons=[
            Button(text=yes_text, handler=yes_handler),
            Button(text=no_text, handler=no_handler),
        ], with_background=True)

    return _run_dialog(dialog, style, async_=async_)


def input_dialog(title='', text='', ok_text='OK', cancel_text='Cancel',
                 completer=None, password=False, style=None, async_=False):
    def accept(buf):
        get_app().layout.focus(ok_button)
        return True  # Keep text.

    def ok_handler():
        get_app().exit(result=textfield.text)

    ok_button = Button(text=ok_text, handler=ok_handler)
    cancel_button = Button(text=cancel_text, handler=_return_none)

    textfield = TextArea(
        multiline=False,
        password=password,
        completer=completer,
        accept_handler=accept)

    dialog = Dialog(
        title=title,
        body=HSplit([
            Label(text=text, dont_extend_height=True),
            textfield,
        ], padding=D(preferred=1, max=1)),
        buttons=[ok_button, cancel_button],
        with_background=True)

    return _run_dialog(dialog, style, async_=async_)


def _run_dialog(dialog, style, async_=False):
    application = _create_app(dialog, style)
    if async_:
        return application.run_async()
    else:
        return application.run()


def _create_app(dialog, style):
    bindings = KeyBindings()
    bindings.add('tab')(focus_next)
    bindings.add('s-tab')(focus_previous)
    bindings.add('escape')(close)

    return Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([
            load_key_bindings(),
            bindings,
        ]),
        mouse_support=True,
        style=style,
        full_screen=True)
