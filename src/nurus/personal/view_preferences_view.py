"""View customization, independent of case edits and RUS connectivity."""
from copy import deepcopy
import re
import tkinter as tk
from tkinter import filedialog, simpledialog, ttk

from . import ui
from .view_preferences import Preferences, TABLES, FILTERS, validate_state, fit_geometry
from .widgets import ScrollPane


class Controller:
    def __init__(self, app):
        self.app = app
        self.store = Preferences(app.cfg.directory)
        self.font_size = 13
        if self.store.data['current'] is not None:
            self.apply(self.store.data['current'], remember=False)
        else:
            self._set_font(self.font_size)

    def capture(self):
        app = self.app
        app.update_idletasks()
        tables = {}
        for name, columns in TABLES.items():
            tree = getattr(app, name)
            visible = tree.cget('displaycolumns')
            if visible == ('#all',) or visible == '#all':
                visible = columns
            tables[name] = dict(visible=list(visible), widths={col: int(tree.column(col, 'width')) for col in columns})
        page = next((key for key, widget in app.pages.items() if str(widget) == app.tabs.select()), 'Trabajo')
        dimensions = re.match(r'(\d+)x(\d+)', app.geometry())
        width, height = (int(part) for part in dimensions.groups())
        geometry = dict(width=max(400, width), height=max(300, height),
                        x=app.winfo_x(), y=app.winfo_y(), maximized=app.state() == 'zoomed')
        return validate_state(dict(filters={key: getattr(app, key).get() for key in FILTERS}, tables=tables,
                                   font_size=self.font_size, geometry=geometry, page=page,
                                   split={key: min(.9, max(.1, getattr(app, key, .4))) for key in
                                          ('work_sash_ratio', 'resolution_sash_ratio')}))

    def _set_font(self, size):
        app = self.app
        style = ttk.Style(app)
        style.configure('Treeview', font=('Segoe UI', size), rowheight=max(29, size * 2 + 8))
        style.configure('Treeview.Heading', font=('Segoe UI', size, 'bold'))
        for name in ('observation_editor', 'project_editor', 'body', 'text_editor', 'tpl_body'):
            if hasattr(app, name):
                getattr(app, name).configure(font=('Segoe UI', size))
        self.font_size = size

    def _apply_widgets(self, state):
        app = self.app
        selected = {name: tuple(getattr(app, name).selection()) for name in TABLES}
        selected['records'] = app._selected_work_ids()
        # Validate current widgets before changing any of them.
        for name, columns in TABLES.items():
            if tuple(getattr(app, name).cget('columns')) != columns:
                raise ValueError('La tabla cambió; no se aplicó la vista: ' + name)
        for name, settings in state['tables'].items():
            tree = getattr(app, name)
            tree.configure(displaycolumns=settings['visible'])
            for column, width in settings['widths'].items():
                tree.column(column, width=width, stretch=False)
        for key, value in state['filters'].items():
            getattr(app, key).set(value)
        app._apply_work_filter()
        app._apply_resolution_filter()
        for name, selection in selected.items():
            tree = getattr(app, name)
            tree.selection_set([rid for rid in selection if tree.exists(rid)])
        for key, ratio in state['split'].items():
            setattr(app, key, ratio)
        for key in ('work', 'resolution'):
            pane = getattr(app, key + '_split', None)
            if pane is not None and len(pane.panes()) == 2:
                pane.sashpos(0, int(pane.winfo_height() * state['split'][key + '_sash_ratio']))
        self._set_font(state['font_size'])
        app.state('normal')
        # CTk geometry uses logical pixels; Tk reports physical pixels on Windows.
        screen = tuple(app._reverse_window_scaling(size) for size in (app.winfo_screenwidth(), app.winfo_screenheight()))
        minimum = tuple(app._reverse_window_scaling(size) for size in tk.Wm.minsize(app))
        app.geometry(fit_geometry(state['geometry'], *screen, minimum))
        if state['geometry']['maximized']:
            app.state('zoomed')
        app.tabs.select(app.pages[state['page']])

    def apply(self, state, *, remember=True):
        state = validate_state(state)
        old = self.capture() if remember else None
        try:
            self._apply_widgets(state)
            if remember:
                # Preserve the actual view before this explicit change.
                data = deepcopy(self.store.data)
                data.update(previous=old, current=state)
                self.store._commit(data)
        except Exception:
            if old is not None:
                self._apply_widgets(old)
            raise

    def save_current(self):
        self.store.remember(self.capture(), keep_previous=self.store.data['previous'] is not None)

    def restore_previous(self):
        previous = self.store.data['previous']
        if previous is None:
            raise ValueError('Todavía no hay una vista anterior para restaurar.')
        self.apply(previous)


def attach(app):
    try:
        app.view_preferences = Controller(app)
    except (ValueError, OSError) as exc:
        app.view_preferences = None
        app.view_preferences_error = str(exc)
        app.status.set('No se restauró la vista guardada: ' + str(exc))


def build(app, notebook):
    pane = ScrollPane(notebook)
    notebook.add(pane, text='Vista')
    page = pane.body
    ui.Label(page, text='Guardar y restaurar la vista', font=('Segoe UI', 19, 'bold')).pack(anchor='w', pady=8)
    ui.Label(page, text='La vista guarda filtros, columnas, anchos, fuente de tablas y editores y tamaño de ventana. '
             'Los registros y sus observaciones siguen en el trabajo.', wraplength=720, text_color=ui.MUTED).pack(fill='x', pady=8)
    name = tk.StringVar()
    choice = ui.Combobox(page, textvariable=name, values=[], state='readonly', width=35)
    choice.pack(anchor='w', pady=6)
    def controller():
        current = getattr(app, 'view_preferences', None)
        if current is None:
            raise ValueError('No se pudieron cargar las preferencias: ' + getattr(app, 'view_preferences_error', 'vista no disponible'))
        return current
    def refresh():
        current = getattr(app, 'view_preferences', None)
        names = sorted(current.store.data['presets']) if current else []
        if current:
            font.set(str(current.font_size))
        choice.configure(values=names)
        if name.get() not in names:
            name.set(names[0] if names else '')
    def save():
        current = controller()
        label = simpledialog.askstring('Guardar vista', 'Nombre de esta vista:', initialvalue=name.get(), parent=app)
        if label is None:
            return
        label = label.strip()
        if label in current.store.data['presets']:
            from tkinter import messagebox
            if not messagebox.askyesno('Sustituir vista', '¿Sustituir la vista «' + label + '»?', parent=app):
                return
        current.store.save_preset(label, current.capture())
        refresh()
        name.set(label)
        app.status.set('Vista guardada: ' + label)
    def apply():
        current = controller()
        if name.get() not in current.store.data['presets']:
            raise ValueError('Selecciona una vista guardada.')
        current.apply(current.store.data['presets'][name.get()])
        app.status.set('Vista aplicada. Restaurar anterior permite deshacerla.')
    def previous():
        controller().restore_previous()
        app.status.set('Vista anterior restaurada.')
    def export():
        current = controller()
        label = name.get() or 'Vista actual'
        state = current.store.data['presets'].get(name.get()) or current.capture()
        path = filedialog.asksaveasfilename(title='Exportar vista local', defaultextension='.json', initialfile='Vista_CSMP.json',
                                          filetypes=[('Vista CSMP', '*.json')])
        if path:
            current.store.export_preset(path, label, state)
            app.status.set('Vista exportada: ' + path)
    def import_view():
        path = filedialog.askopenfilename(title='Importar vista local', filetypes=[('Vista CSMP', '*.json')])
        if path:
            label = controller().store.import_preset(path)
            refresh()
            name.set(label)
            app.status.set('Vista importada; pulsa Aplicar vista para usarla.')
    buttons = ui.Frame(page)
    buttons.pack(fill='x', pady=5)
    for index, (label, command) in enumerate((('Guardar vista', save), ('Aplicar vista', apply), ('Restaurar anterior', previous),
                                             ('Exportar JSON', export), ('Importar JSON', import_view))):
        ui.Button(buttons, text=label, width=145, command=lambda fn=command: app._guard(fn)).grid(row=index // 3, column=index % 3, padx=4, pady=4)
    controls = ui.Frame(page)
    controls.pack(fill='x', pady=12)
    ui.Label(controls, text='Fuente de tablas y editores (puntos)').pack(side='left', padx=5)
    font = tk.StringVar(value='13')
    ui.Combobox(controls, textvariable=font, values=[str(n) for n in range(10, 23)], state='readonly', width=8).pack(side='left')
    def change_font():
        current = controller()
        state = current.capture()
        state['font_size'] = int(font.get())
        current.apply(state)
        app.status.set('Tamaño de fuente aplicado.')
    ui.Button(controls, text='Aplicar fuente', command=lambda: app._guard(change_font)).pack(side='left', padx=8)
    ui.Label(page, text='Columnas visibles, orden y ancho', font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(8, 4))
    table_name = tk.StringVar(value='Trabajo')
    table_keys = {'Trabajo': 'records', 'Resoluciones': 'words', 'Historial': 'sent'}
    ui.Combobox(page, textvariable=table_name, values=list(table_keys), state='readonly', width=25).pack(anchor='w')
    list_frame = ui.Frame(page)
    list_frame.pack(fill='x', pady=6)
    column_list = tk.Listbox(list_frame, height=6, exportselection=False, font=('Segoe UI', 12))
    column_list.pack(side='left', fill='both', expand=True)
    editor = ui.Frame(list_frame)
    editor.pack(side='left', fill='y', padx=10)
    visible = tk.BooleanVar(value=True)
    width = tk.StringVar(value='140')
    ui.Checkbutton(editor, text='Visible', variable=visible).pack(anchor='w', pady=4)
    ui.Label(editor, text='Ancho (65–2000 px)').pack(anchor='w')
    ui.Entry(editor, textvariable=width, width=10).pack(anchor='w', pady=4)
    working = {'order': [], 'settings': None, 'table': None}
    def selected(_event=None):
        indexes = column_list.curselection()
        if not indexes or working['settings'] is None:
            return
        col = working['order'][indexes[0]]
        settings = working['settings']
        visible.set(col in settings['visible'])
        width.set(str(settings['widths'][col]))
    column_list.bind('<<ListboxSelect>>', selected)
    def populate(index=0):
        column_list.delete(0, 'end')
        for col in working['order']:
            column_list.insert('end', col)
        column_list.selection_set(index)
        selected()
    def load_columns():
        current = controller()
        key = table_keys[table_name.get()]
        settings = current.capture()['tables'][key]
        working.update(table=key, settings=deepcopy(settings), order=settings['visible'] + [col for col in TABLES[key] if col not in settings['visible']])
        populate()
    def change_column():
        if not column_list.curselection():
            raise ValueError('Carga y selecciona una columna.')
        col = working['order'][column_list.curselection()[0]]
        size = int(width.get())
        if not 65 <= size <= 2000:
            raise ValueError('El ancho debe estar entre 65 y 2000 píxeles.')
        settings = working['settings']
        shown = set(settings['visible'])
        if visible.get():
            shown.add(col)
        else:
            shown.discard(col)
        if not shown:
            raise ValueError('Conserva al menos una columna visible.')
        settings['visible'] = [col for col in working['order'] if col in shown]
        settings['widths'][col] = size
        app.status.set('Columna ajustada. Aplicar columnas confirma la distribución completa.')
    def move(delta):
        indexes = column_list.curselection()
        if not indexes:
            return
        old = indexes[0]
        new = old + delta
        order = working['order']
        if 0 <= new < len(order):
            order[old], order[new] = order[new], order[old]
            shown = working['settings']['visible']
            working['settings']['visible'] = [col for col in order if col in shown]
            populate(new)
    def apply_columns():
        if working['table'] is None:
            raise ValueError('Carga las columnas de una tabla primero.')
        if working['table'] != table_keys[table_name.get()]:
            raise ValueError('Cambiaste de tabla; carga sus columnas antes de aplicar.')
        change_column()
        current = controller()
        state = current.capture()
        state['tables'][working['table']] = deepcopy(working['settings'])
        current.apply(state)
        app.status.set('Columnas aplicadas. Puedes restaurar la vista anterior.')
    for label, command in (('Ajustar columna', change_column), ('Subir', lambda: move(-1)), ('Bajar', lambda: move(1))):
        ui.Button(editor, text=label, width=130, command=lambda fn=command: app._guard(fn)).pack(anchor='w', pady=3)
    row = ui.Frame(page)
    row.pack(fill='x', pady=5)
    for label, command in (('Cargar columnas', load_columns), ('Aplicar columnas', apply_columns)):
        ui.Button(row, text=label, width=160, command=lambda fn=command: app._guard(fn)).pack(side='left', padx=5)
    ui.Label(page, text='Al cerrar se recuerda la vista actual. Las vistas JSON solo contienen preferencias de presentación y filtros.',
             wraplength=720, text_color=ui.MUTED).pack(fill='x', pady=8)
    app.after(50, refresh)
