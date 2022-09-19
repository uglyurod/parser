import PySimpleGUI as gui


class GUI:

    menu_def = [['&File', ['&Save', '---', 'Properties', 'E&xit']],
                ['&Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['&Help', '&About...'], ]
    layout = [
        [gui.Menu(menu_def)],
        [gui.Button("Start"), gui.Cancel()],
        [gui.Input(key='-INPUT-')],
        [gui.Output(size=(88, 20), key='-OUTPUT-')]
    ]

    window = gui.Window('Parser', layout)
    while True:  # The Event Loop
        event, values = window.read()
        print(event, values)
        if event == 'Start':
            window('-OUTPUT-').update()
        if event in ('Exit', 'Cancel'):
            break
