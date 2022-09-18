import PySimpleGUI as gui


class GUI:
    layout = [
        [gui.Button("Start"), gui.Cancel()],
        [gui.Input(key='-INPUT-')],
        [gui.Output(size=(88, 20))]
    ]
    window = gui.Window('Parser', layout)
    while True:  # The Event Loop
        event, values = window.read()
        # print(event, values) #debug
        if event == 'Start':
            gui.Output.update(values['-IN-'])
        if event in (None, 'Exit', 'Cancel'):
            break
