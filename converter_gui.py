"""Tkinter interface for the Image to ICO Converter."""

from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ico_converter import convert_image


FILE_TYPES = [
    ("Supported images", "*.png *.jpg *.jpeg"),
    ("PNG images", "*.png"),
    ("JPEG images", "*.jpg *.jpeg"),
    ("All files", "*.*"),
]


class ConverterApp:
    """GUI for selecting and converting multiple images."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Image to ICO Converter")
        self.root.geometry("720x520")
        self.root.minsize(560, 420)

        self.image_paths: list[Path] = []
        self.path_keys: set[str] = set()
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.output_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Select one or more images to begin.")

        self._build_ui()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        ttk.Label(outer, text="Images", font=("TkDefaultFont", 11, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        list_frame = ttk.Frame(outer)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.image_list = tk.Listbox(
            list_frame, selectmode=tk.EXTENDED, activestyle="dotbox"
        )
        self.image_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.image_list.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.image_list.configure(yscrollcommand=scrollbar.set)

        list_buttons = ttk.Frame(outer)
        list_buttons.grid(row=2, column=0, sticky="w", pady=(8, 16))
        self.add_button = ttk.Button(
            list_buttons, text="Select images...", command=self.select_images
        )
        self.add_button.pack(side="left")
        self.remove_button = ttk.Button(
            list_buttons, text="Remove selected", command=self.remove_selected
        )
        self.remove_button.pack(side="left", padx=(8, 0))
        self.clear_button = ttk.Button(
            list_buttons, text="Clear", command=self.clear_images
        )
        self.clear_button.pack(side="left", padx=(8, 0))

        ttk.Label(
            outer, text="Output folder", font=("TkDefaultFont", 11, "bold")
        ).grid(row=3, column=0, sticky="w", pady=(0, 8))

        output_frame = ttk.Frame(outer)
        output_frame.grid(row=4, column=0, sticky="ew")
        output_frame.columnconfigure(0, weight=1)
        self.output_entry = ttk.Entry(
            output_frame, textvariable=self.output_var, state="readonly"
        )
        self.output_entry.grid(row=0, column=0, sticky="ew")
        self.output_button = ttk.Button(
            output_frame, text="Browse...", command=self.select_output_folder
        )
        self.output_button.grid(row=0, column=1, padx=(8, 0))

        self.progress = ttk.Progressbar(outer, mode="determinate")
        self.progress.grid(row=5, column=0, sticky="ew", pady=(20, 6))
        ttk.Label(outer, textvariable=self.status_var).grid(
            row=6, column=0, sticky="w"
        )

        self.convert_button = ttk.Button(
            outer, text="Convert to ICO", command=self.start_conversion
        )
        self.convert_button.grid(row=7, column=0, sticky="e", pady=(16, 0))

        self.controls = (
            self.add_button,
            self.remove_button,
            self.clear_button,
            self.output_button,
            self.convert_button,
        )

    @staticmethod
    def _path_key(path: Path) -> str:
        return os.path.normcase(str(path.resolve()))

    def select_images(self) -> None:
        initial_dir = (
            self.image_paths[0].parent if self.image_paths else Path.cwd()
        )
        selected = filedialog.askopenfilenames(
            parent=self.root,
            title="Select images",
            initialdir=initial_dir,
            filetypes=FILE_TYPES,
        )
        if not selected:
            return

        added: list[Path] = []
        for filename in selected:
            path = Path(filename).resolve()
            key = self._path_key(path)
            if key in self.path_keys:
                continue
            self.image_paths.append(path)
            self.path_keys.add(key)
            self.image_list.insert(tk.END, str(path))
            added.append(path)

        if added and not self.output_var.get():
            self.output_var.set(str(added[0].parent))
        self._update_selection_status()

    def select_output_folder(self) -> None:
        initial_dir = self.output_var.get() or str(Path.cwd())
        selected = filedialog.askdirectory(
            parent=self.root,
            title="Select output folder",
            initialdir=initial_dir,
            mustexist=True,
        )
        if selected:
            self.output_var.set(str(Path(selected).resolve()))

    def remove_selected(self) -> None:
        for index in reversed(self.image_list.curselection()):
            path = self.image_paths.pop(index)
            self.path_keys.discard(self._path_key(path))
            self.image_list.delete(index)
        self._update_selection_status()

    def clear_images(self) -> None:
        self.image_paths.clear()
        self.path_keys.clear()
        self.image_list.delete(0, tk.END)
        self._update_selection_status()

    def _update_selection_status(self) -> None:
        self.status_var.set(
            f"{len(self.image_paths)} image(s) selected."
            if self.image_paths
            else "Select one or more images to begin."
        )

    def start_conversion(self) -> None:
        if not self.image_paths:
            messagebox.showwarning(
                "No images", "Select at least one image first.", parent=self.root
            )
            return

        output_dir = Path(self.output_var.get())
        if not output_dir.is_dir():
            messagebox.showwarning(
                "Invalid output folder",
                "Select an existing output folder.",
                parent=self.root,
            )
            return
        if not os.access(output_dir, os.W_OK):
            messagebox.showerror(
                "Output folder unavailable",
                "The selected output folder is not writable.",
                parent=self.root,
            )
            return

        if any(not path.is_file() for path in self.image_paths):
            messagebox.showerror(
                "Missing images",
                "One or more selected images no longer exist. Remove them and try again.",
                parent=self.root,
            )
            return

        images = tuple(self.image_paths)
        self.progress.configure(maximum=len(images), value=0)
        self.status_var.set(f"Converting 0 of {len(images)}...")
        self._set_controls_enabled(False)

        worker = threading.Thread(
            target=self._convert_worker,
            args=(images, output_dir),
            daemon=True,
        )
        worker.start()
        self.root.after(50, self._process_events)

    def _convert_worker(self, images: tuple[Path, ...], output_dir: Path) -> None:
        failures: list[tuple[Path, str]] = []
        created: list[Path] = []
        for index, image_path in enumerate(images, start=1):
            try:
                created.append(convert_image(image_path, output_dir))
            except (OSError, ValueError) as error:
                failures.append((image_path, str(error)))
            self.events.put(("progress", (index, len(images), image_path.name)))
        self.events.put(("done", (created, failures)))

    def _process_events(self) -> None:
        finished = False
        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break

            if event == "progress":
                current, total, filename = payload  # type: ignore[misc]
                self.progress.configure(value=current)
                self.status_var.set(
                    f"Converting {current} of {total}: {filename}"
                )
            elif event == "done":
                created, failures = payload  # type: ignore[misc]
                self._finish_conversion(created, failures)
                finished = True

        if not finished:
            self.root.after(50, self._process_events)

    def _finish_conversion(
        self, created: list[Path], failures: list[tuple[Path, str]]
    ) -> None:
        self._set_controls_enabled(True)
        self.status_var.set(
            f"Finished: {len(created)} created, {len(failures)} failed."
        )

        if failures:
            details = "\n".join(f"{path.name}: {error}" for path, error in failures)
            messagebox.showwarning(
                "Conversion complete",
                f"Created: {len(created)}\nFailed: {len(failures)}\n\n{details}",
                parent=self.root,
            )
        else:
            messagebox.showinfo(
                "Conversion complete",
                f"Successfully created {len(created)} icon(s).",
                parent=self.root,
            )

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for control in self.controls:
            control.configure(state=state)


def run_app() -> None:
    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()
