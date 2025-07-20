# -*- coding: utf-8 -*-

from bokeh.plotting import figure, output_file, ColumnDataSource, save, show
from bokeh.models import HoverTool, FactorRange, Legend
from bokeh.models.glyphs import Line
import json
import bokeh.palettes
from bokeh.embed import components
from os.path import join
from collections import OrderedDict

aa_dict_F = {'A': 'alanine', 'R': 'arginine', 'N': 'asparagine',
             'D': 'aspartic acid', 'C': 'cysteine', 'E': 'glutamic acid',
             'Q': 'glutamine', 'G': 'glycine', 'H': 'histidine',
             'I': 'isoleucine', 'L': 'leucine', 'K': 'lysine',
             'M': 'methionine', 'F': 'phenylalanine', 'P': 'proline',
             'S': 'serine', 'T': 'threonine', 'W': 'tryptophan',
             'Y': 'tyrosine', 'V': 'valine', 'X': 'unknown'}


def create_mut_plot(data_dir, save_plot=False):
    # This will read a mutant list that is already available to the calling jscript, dunno if its worth to pass it tho
    mutants = [""]      # The first is a fake - it will read the base simulation result and name it Base
    max_mutants, counter = 12, 0  # This is also used somewhere else so maybe should unify it
    p = []  # To create the figure object in a loop
    with open(join(data_dir, "Mutations_summary.csv"), "r") as f:
        f.readline()
        for line in f:
            mutants.append(line.split(",")[0])
            counter += 1
            if counter >= max_mutants:
                break
    counter = 0
    colors = bokeh.palettes.Category10[10]  # This is not enough colors need 13 for 12 mutants and its only 10
    colors.append('#1E1717')    # almost black
    colors.append('#f3ff00')    # strong, flashy yellow
    colors.append('#ce6778')    # kinda pinkish I guess
    legend_items = []
    for mutant in mutants:
        x, y, chain, name, index, status = [], [], [], [], [], []
        mutant = mutant if mutant else "A3D"    # It's a band aid considering file locations and names have changed
                                                # (Base csv is named A3D.csv)
        with open(join(data_dir, mutant + ".csv"), 'r') as f:
            if mutant == "A3D":     # Following the weird convention to get the Base case first with the name Base
                mutant = "Wild type"
            f.readline()    # skip the initial line with labels
            for line in f:
                a = line.strip().split(',')
                # a goes as follows: model name, chain, index, one letter code, aggrescan score
                x.append(("Chain %s" % a[1], a[2]+a[1]))
                y.append(float(a[-1]))
                name.append(aa_dict_F[a[-2]])
                index.append(a[2])
                chain.append(a[1])
                status.append('Soluble' if float(a[-1]) <= 0 else 'Aggregation prone')
        if not p:
            p = figure(plot_width=1150, plot_height=600, tools=['box_zoom,pan,reset,save'],
                       title="Score breakdown for mutants. "
                             "Click on the legend to hide/show the line. Mouse over a point to see details.",
                       x_range=FactorRange(*x), toolbar_location="below")
            p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
            p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
            p.yaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
            p.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels, it keeps the chain names though
            p.xgrid.grid_line_color = None  # turn off the grid
            p.ygrid.grid_line_color = None
        mut_names = [mutant for i in range(len(x))]
        source = ColumnDataSource(data=dict(
            x=x,
            y=y,
            line_y=[0 for i in range(len(x))],
            name=name,
            index=index,
            status=status,
            chain=chain,
            mut_name=mut_names
        ))

        # @ means they will get assigned in order from the data defined above, names means it will only display there
        hover = HoverTool(tooltips=[
            ("Chain", "@chain"),
            ("Residue name", "@name"),
            ("Residue index", "@index"),
            ("Prediction", "@status"),
            ("Mutant", "@mut_name")],
            mode='vline',
            names=[mutant])

        the_line = p.line('x', 'y', source=source, name=mutant,color=colors[counter], line_width=2.5,
                          line_alpha=1.0)  # the main plot
        legend_items.append((mutant, [the_line]))
        if counter not in [0, 1]:
            the_line.visible = False
        p.add_tools(hover)
        counter += 1
    legend = Legend(items=legend_items, click_policy="hide")
    p.add_layout(legend, "left")
    script, div = components(p)
    if save_plot:       # Will not be used for now, could be used by the main program but importing this would be bad
                        # (Due to how the server is started, it would start it on import # TODO provide download button
        save(p, filename="Automated_mutations", title="Mutation analysis")
    else:
        return script, div


def create_dyn_plot(data_dir):
    # copy paste of the above the models are still literally called mutants so yeah
    # This will read a mutant list that is already available to the calling jscript, dunno if its worth to pass it tho
    mutants = []
    with open(join(data_dir, "averages"), "r") as f:
        data = f.read()
    data = json.loads(data)
    data = _sort_dict(data)
    # make sure the ordering is the same as in the table
    for key, value in data.items():
        mutants.append(key.split(".")[0])
    p = []  # To create the figure object in a loop
    counter = 0
    colors = bokeh.palettes.Category10[10]  # This is not enough colors need 14 for 12 models, input and average
    colors.append('#1E1717')    # almost black
    colors.append('#f3ff00')    # strong, flashy yellow
    colors.append('#ce6778')    # kinda pinkish I guess
    colors.append('#161664')    # Dark blue
    legend_items = []
    for mutant in mutants:
        x, y, chain, name, index, status = [], [], [], [], [], []
        with open(join(data_dir, mutant + ".csv"), 'r') as f:
            if mutant == "input":     # Following the weird convention to get the Base case first with the name Base
                mutant = "Input"
            f.readline()    # skip the initial line with labels
            for line in f:
                a = line.strip().split(',')
                # a goes as follows: model name, chain, index, one letter code, aggrescan score
                x.append(("Chain %s" % a[1], a[2]+a[1]))
                y.append(float(a[-1]))
                name.append(aa_dict_F[a[-2]])
                index.append(a[2])
                chain.append(a[1])
                status.append('Soluble' if float(a[-1]) <= 0 else 'Aggregation prone')
        if not p:
            p = figure(plot_width=1150, plot_height=600, tools=['pan,wheel_zoom,box_zoom,reset,save'],
                       active_drag="auto", active_scroll="wheel_zoom",
                       title="Click on the legend to hide/show the line. Scroll to zoom in/out and drag with the mouse"
                             " to pan the plot. Mouse over to see the details.",
                       x_range=FactorRange(*x), toolbar_location="below")
            p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
            p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
            p.yaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
            p.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels, it keeps the chain names though
            p.xgrid.grid_line_color = None  # turn off the grid
            p.ygrid.grid_line_color = None
        mut_names = [mutant for i in range(len(x))]
        source = ColumnDataSource(data=dict(
            x=x,
            y=y,
            line_y=[0 for i in range(len(x))],
            name=name,
            index=index,
            status=status,
            chain=chain,
            mut_name=mut_names
        ))

        # @ means they will get assigned in order from the data defined above, names means it will only display there
        hover = HoverTool(tooltips=[
            ("Chain", "@chain"),
            ("Residue name", "@name"),
            ("Residue index", "@index"),
            ("Prediction", "@status"),
            ("Model", "@mut_name")],
            mode='vline',
            names=[mutant])

        the_line = p.line('x', 'y', source=source, name=mutant,color=colors[counter], line_width=2.5,
                          line_alpha=1.0)  # the main plot
        legend_items.append((mutant, [the_line]))
        if counter not in [0, 1]:
            the_line.visible = False
        p.add_tools(hover)
        counter += 1
    legend = Legend(items=legend_items, click_policy="hide")
    p.add_layout(legend, "left")
    script, div = components(p)
    return script, div


def create_plot(csv_address, model):
    x, y, chain, name, index, status = [], [], [], [], [], []
    with open(csv_address, 'r') as f:
        f.readline()    # skip the initial line with labels
        for line in f:
            a = line.strip().split(',')
            # a goes as follows: model name, chain, index, one letter code, aggrescan score
            x.append(("Chain %s" % a[1], a[2]+a[1]))
            y.append(float(a[-1]))
            name.append(aa_dict_F[a[-2]])
            index.append(a[2])
            chain.append(a[1])
            status.append('Soluble' if float(a[-1]) <= 0 else 'Aggregation prone')
    source = ColumnDataSource(data=dict(
        x=x,
        y=y,
        line_y=[0 for i in range(len(x))],
        name=name,
        index=index,
        status=status,
        chain=chain
    ))

    # @ means they will get assigned in order from the data defined above, names means it will only display there
    hover = HoverTool(tooltips=[
        ("Chain", "@chain"),
        ("Residue name", "@name"),
        ("Residue index", "@index"),
        ("Prediction", "@status")],
        mode='vline',
        names=["line"])

    # TODO maybe get the underlying DOM in job_info and adjust the size to that, rather than keeping it static but it wouldnt be perfect either
    # Creeates the plot, adds the tools, and creates the x axis with major tick names, and then chain names below
    p = figure(plot_width=1150, plot_height=600, tools=[hover, 'box_zoom,pan,reset,save'],
               title="Aggrescan3D score based on residue for %s. Mouse over the plot to see residue's details" % model,
               x_range=FactorRange(*x), toolbar_location="below")

    p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p.yaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels, it keeps the chain names though
    p.xgrid.grid_line_color = None  # turn off the grid
    p.ygrid.grid_line_color = None
    p.line('x', 'y', source=source, name="line")    # the main plot
    glyph = Line(x="x", y="line_y", line_color="#f46d43", line_width=2, line_alpha=0.3)  # small line to help find aggregation prone residues
    p.add_glyph(source, glyph)  # actually draw the line on the figure
    script, div = components(p)

    return script, div


def _sort_dict(my_dict):
    """Return a reverse-sorted by value, OrderedDict of a regular dictionary with number values"""
    new_dict = OrderedDict()
    for key, value in sorted(my_dict.iteritems(), key=lambda (k, v): (v, k), reverse=True):
        new_dict[key] = value
    return new_dict