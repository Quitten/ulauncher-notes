from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from os.path import expanduser
import os, json, uuid, pyclip #pyperclip


class NotesExtension(Extension):
    def __init__(self):
        super(NotesExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


home = expanduser("~")
notesFilePath = '%s/.notes' % home
if not os.path.isfile(notesFilePath):
    f = open(notesFilePath, 'w')
    f.close()


def saveNote(note):
    note['id'] = str(uuid.uuid4())
    f = open(notesFilePath, 'a')
    f.write('%s\n' % json.dumps(note))
    f.close()


def deleteNote(deleteNote):
    notes = getNotes()
    f = open(notesFilePath, 'w')
    for note in notes:
        if note['id'] != deleteNote['id']:
            f.write('%s\n' % json.dumps(note))
    f.close()


def copyToClipboard(note):
    pyclip.copy(note['data'])


def getNotes():
    notes = []
    f = open(notesFilePath, 'r')
    lines = f.read().split('\n')
    f.close()

    for data in lines:
        if data == '' or data is None:
            continue
        note = json.loads(data)
        notes.append(note)
    return notes


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        if event.get_keyword() == 'notes':
            resNotes = []
            f = open(notesFilePath, 'r')
            lines = f.read().split('\n')
            f.close()

            notes = getNotes()
            for note in notes:
                note['mode'] = ''
                if event.get_argument() == 'delete' or event.get_argument() == 'del' or event.get_argument() == 'd':
                    note['mode'] = 'deleteNote'
                if event.get_argument() == 'copy' or event.get_argument() == 'c':
                    note['mode'] = 'copyToClipboard'
                resNotes.append(
                    ExtensionResultItem(
                        icon='note.png',
                        name=note['data'],
                        description='',
                        on_enter=ExtensionCustomAction(note, keep_app_open=True)
                    )
                )
            return RenderResultListAction(resNotes)

        if event.get_keyword() == 'note':
            note = {
                'data': event.get_argument(),
                'mode': 'addNewNote'
            }
            return RenderResultListAction(
                [ExtensionResultItem(
                    icon='note.png',
                    name='New Note:',
                    description=note['data'],
                    on_enter=ExtensionCustomAction(note, keep_app_open=True)
                )]
            )


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        note = event.get_data()
        if note['mode'] == 'addNewNote':
            saveNote(note)
        if note['mode'] == 'deleteNote':
            deleteNote(note)
        if note['mode'] == 'copyToClipboard':
            copyToClipboard(note)

        return HideWindowAction()


if __name__ == '__main__':
    NotesExtension().run()
