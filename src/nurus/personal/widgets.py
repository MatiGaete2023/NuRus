"""Controles pequeños para el escritorio Windows del Asistente."""
import tkinter as tk
from tkinter import ttk
from collections import Counter


class ScrollPane(ttk.Frame):
    """Panel desplazable: no oculta acciones cuando hay poca altura disponible."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, width=315, height=260)
        bar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        bar.pack(side='right', fill='y')
        self.body = ttk.Frame(self.canvas, padding=4)
        item = self.canvas.create_window((0, 0), window=self.body, anchor='nw')
        self.body.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(item, width=e.width))
        self.canvas.bind('<MouseWheel>', self._wheel)
        self.body.bind('<MouseWheel>', self._wheel)

    def _wheel(self, event):
        if self.body.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')
            return 'break'


class NamedChoice(ttk.Combobox):
    """Muestra nombres editables conservando IDs estables para reglas y plantillas."""
    def __init__(self, parent, *, keyvariable, names, **kwargs):
        self.keyvariable = keyvariable
        self.names = names
        self.label = tk.StringVar(parent)
        super().__init__(parent, textvariable=self.label, **kwargs)
        self.keyvariable.trace_add('write', self._sync_label)
        super().bind('<<ComboboxSelected>>', self._selected)
        self.set_keys(list(names()))

    def bind(self, sequence=None, func=None, add=None):
        # El llamador recibe el ID actualizado antes de cargar el formulario.
        return super().bind(sequence, func, '+' if sequence == '<<ComboboxSelected>>' else add)

    def set_keys(self, keys):
        names = self.names()
        titles = [names.get(key, key) for key in keys]
        counts = Counter(titles)
        self.keys = list(keys)
        self.labels = [title if counts[title] == 1 else f'{title} [{key}]' for key, title in zip(keys, titles)]
        super().configure(values=self.labels)
        self._sync_label()

    def configure(self, cnf=None, **kwargs):
        if 'values' in kwargs:
            self.set_keys(kwargs.pop('values'))
        return super().configure(cnf, **kwargs)

    def _sync_label(self, *args):
        key = self.keyvariable.get()
        self.label.set(self.labels[self.keys.index(key)] if key in self.keys else key)

    def _selected(self, event=None):
        index = self.current()
        if index >= 0:
            self.keyvariable.set(self.keys[index])
