import taipy as tp

options = [str(i) for i in range(1, 6)]

selected_option1 = None
selected_option2 = None

def on_change(state, var_name, var_value):
    global options, selected_option1, selected_option2
    if var_name == 'selected_option1':
        options = [str(i) for i in range(1, 6)]
        options.remove(var_value)
        selected_option2 = None
    elif var_name == 'selected_option2':
        options = [str(i) for i in range(1, 6)]
        options.remove(var_value)
        selected_option1 = None

page = """
<|layout|columns=1 2|
<|{selected_option1}|selector|label=Option 1|on_change=on_change|lov={options}|>
<|{selected_option2}|selector|label=Option 2|on_change=on_change|lov={options}|>
|>
"""

tp.Gui(page).run()
