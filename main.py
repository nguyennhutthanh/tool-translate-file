"""
main.py – File Translator Tool
================================
Features:
  • Single file translation with structure preservation
  • Paste-text mode (no file needed)
  • Batch translation (multiple files → ZIP download)
  • Custom glossary (term replacement before/after translation)
  • Translation history log
  • Source + target language selectors
  • Provider selector: Google Translate / MyMemory
  • Cancel in-progress translation
  • Editable translated preview
  • Split view (side-by-side)
"""

import os, shutil, sys, tempfile, zipfile
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit, QFileDialog,
    QProgressBar, QFrame, QMessageBox, QTabWidget, QStatusBar,
    QSplitter, QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QListWidget, QListWidgetItem, QScrollArea,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent, QColor

from file_handler import FileHandler, SUPPORTED_EXTENSIONS
from translator_module import TranslatorModule, LANGUAGES, SOURCE_LANGUAGES, PROVIDERS
from glossary_manager import GlossaryManager
from history_manager import HistoryManager

# ── Stylesheet ─────────────────────────────────────────────────────────────────
DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    font-size: 13px;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 7px;
    padding: 9px 18px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover   { background-color: #b4cefb; }
QPushButton:pressed { background-color: #6d9ef7; }
QPushButton:disabled { background-color: #313244; color: #585b70; }
QPushButton#secondary {
    background-color: #313244; color: #cdd6f4;
    border: 1px solid #45475a; font-weight: 600;
}
QPushButton#secondary:hover { background-color: #45475a; }
QPushButton#cancel_btn { background-color: #f38ba8; color: #1e1e2e; font-weight: 700; }
QPushButton#cancel_btn:hover  { background-color: #f5a0b5; }
QPushButton#cancel_btn:disabled { background-color: #313244; color: #585b70; }
QPushButton#small_btn {
    background-color: #313244; color: #cdd6f4;
    border: 1px solid #45475a; padding: 5px 10px;
    font-size: 12px; font-weight: 600; border-radius: 6px;
}
QPushButton#small_btn:hover   { background-color: #45475a; }
QPushButton#small_btn:checked { background-color: #a6e3a1; color: #1e1e2e; border-color: #a6e3a1; }
QPushButton#batch_add  { background-color: #a6e3a1; color: #1e1e2e; padding: 6px 12px; font-size: 12px; font-weight: 700; border-radius: 6px; }
QPushButton#batch_add:hover { background-color: #b8edb4; }
QComboBox {
    background-color: #313244; color: #cdd6f4;
    border: 1px solid #45475a; border-radius: 7px; padding: 7px 12px;
}
QComboBox::drop-down { border: none; width: 28px; }
QComboBox QAbstractItemView {
    background-color: #313244; color: #cdd6f4;
    selection-background-color: #89b4fa; selection-color: #1e1e2e;
    border: 1px solid #45475a;
}
QTextEdit {
    background-color: #181825; color: #cdd6f4;
    border: 1px solid #45475a; border-radius: 7px; padding: 10px;
    font-family: 'Consolas', 'Cascadia Code', 'Courier New', monospace;
    font-size: 13px;
    selection-background-color: #89b4fa; selection-color: #1e1e2e;
}
QListWidget {
    background-color: #181825; color: #cdd6f4;
    border: 1px solid #45475a; border-radius: 7px;
    font-size: 12px;
}
QListWidget::item:selected { background-color: #313244; }
QTableWidget {
    background-color: #181825; color: #cdd6f4;
    border: 1px solid #45475a; gridline-color: #313244;
}
QTableWidget QHeaderView::section {
    background-color: #313244; color: #a6e3a1;
    border: none; padding: 6px; font-weight: 700;
}
QTableWidget::item:selected { background-color: #313244; }
QLabel#title    { font-size: 21px; font-weight: 800; color: #89b4fa; }
QLabel#subtitle { font-size: 11px; color: #6c7086; }
QLabel#section  { font-size: 12px; font-weight: 700; color: #a6e3a1; text-transform: uppercase; letter-spacing: 1px; }
QLabel#panel_title { font-size: 11px; font-weight: 700; color: #89b4fa; padding: 2px 6px; }
QProgressBar { background-color: #313244; border: none; border-radius: 4px; height: 6px; }
QProgressBar::chunk { background-color: #89b4fa; border-radius: 4px; }
QFrame#drop_area { background-color: #181825; border: 2px dashed #45475a; border-radius: 10px; }
QFrame#drop_area[drag_active="true"] { border-color: #89b4fa; background-color: #1e2340; }
QFrame#batch_frame { background-color: #181825; border: 1px solid #313244; border-radius: 8px; padding: 4px; }
QTabWidget::pane { border: 1px solid #45475a; border-radius: 7px; background-color: #181825; }
QTabBar::tab { background-color: #313244; color: #6c7086; padding: 8px 18px; border-top-left-radius: 7px; border-top-right-radius: 7px; margin-right: 3px; font-weight: 600; }
QTabBar::tab:selected { background-color: #181825; color: #cdd6f4; border-top: 2px solid #89b4fa; }
QTabBar::tab:hover:!selected { background-color: #3c3f55; }
QSplitter::handle { background-color: #313244; width: 3px; }
QStatusBar { background-color: #181825; color: #585b70; font-size: 11px; border-top: 1px solid #313244; }
QScrollBar:vertical { background: #1e1e2e; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #45475a; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 8px; }
QScrollBar::handle:horizontal { background: #45475a; border-radius: 4px; }
QDialog { background-color: #1e1e2e; }
"""


# ══════════════════════════════════════════════════════════════════════════════
# Internal cancellation exception
# ══════════════════════════════════════════════════════════════════════════════
class _Cancelled(Exception):
    pass


# ══════════════════════════════════════════════════════════════════════════════
# Dialogs
# ══════════════════════════════════════════════════════════════════════════════

class GlossaryDialog(QDialog):
    def __init__(self, glossary: GlossaryManager, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Custom Glossary")
        self.resize(520, 420)
        self._glossary = glossary
        self._build_ui()
        self._load_terms()

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        info = QLabel(
            "Define terms that must always be translated a specific way.\n"
            "These are applied before sending text to the translation API."
        )
        info.setObjectName("subtitle")
        info.setWordWrap(True)
        lay.addWidget(info)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Source Term", "Target Translation"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lay.addWidget(self._table)

        row_btns = QHBoxLayout()
        add_btn = QPushButton("+ Add Row")
        add_btn.setObjectName("secondary")
        add_btn.clicked.connect(self._add_row)
        del_btn = QPushButton("− Remove Row")
        del_btn.setObjectName("secondary")
        del_btn.clicked.connect(self._remove_row)
        row_btns.addWidget(add_btn)
        row_btns.addWidget(del_btn)
        row_btns.addStretch()
        lay.addLayout(row_btns)

        bottom = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Glossary")
        save_btn.clicked.connect(self._save)
        bottom.addStretch()
        bottom.addWidget(cancel_btn)
        bottom.addWidget(save_btn)
        lay.addLayout(bottom)

    def _load_terms(self) -> None:
        for src, tgt in self._glossary.terms.items():
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(src))
            self._table.setItem(r, 1, QTableWidgetItem(tgt))

    def _add_row(self) -> None:
        self._table.insertRow(self._table.rowCount())

    def _remove_row(self) -> None:
        r = self._table.currentRow()
        if r >= 0:
            self._table.removeRow(r)

    def _save(self) -> None:
        terms: dict[str, str] = {}
        for r in range(self._table.rowCount()):
            si = self._table.item(r, 0)
            ti = self._table.item(r, 1)
            if si and ti and si.text().strip() and ti.text().strip():
                terms[si.text().strip()] = ti.text().strip()
        self._glossary.set_terms(terms)
        self._glossary.save()
        self.accept()


class HistoryDialog(QDialog):
    def __init__(self, history: HistoryManager, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Translation History")
        self.resize(720, 480)
        self._history = history
        self._build_ui()

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)

        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["Time", "File", "Source", "Target", "Provider", "Chars"]
        )
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in (0, 2, 3, 4, 5):
            hdr.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._refresh_table()
        lay.addWidget(self._table)

        bottom = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        clear_btn.setObjectName("secondary")
        clear_btn.clicked.connect(self._clear)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        bottom.addWidget(clear_btn)
        bottom.addStretch()
        bottom.addWidget(close_btn)
        lay.addLayout(bottom)

    def _refresh_table(self) -> None:
        entries = self._history.load()
        self._table.setRowCount(len(entries))
        for i, e in enumerate(entries):
            self._table.setItem(i, 0, QTableWidgetItem(e.get("timestamp", "")))
            self._table.setItem(i, 1, QTableWidgetItem(e.get("filename", "")))
            self._table.setItem(i, 2, QTableWidgetItem(e.get("source_lang", "")))
            self._table.setItem(i, 3, QTableWidgetItem(e.get("target_lang", "")))
            self._table.setItem(i, 4, QTableWidgetItem(e.get("provider", "")))
            self._table.setItem(i, 5, QTableWidgetItem(str(e.get("char_count", ""))))

    def _clear(self) -> None:
        if QMessageBox.question(self, "Clear History", "Clear all translation history?") \
                == QMessageBox.StandardButton.Yes:
            self._history.clear()
            self._table.setRowCount(0)


# ══════════════════════════════════════════════════════════════════════════════
# Workers
# ══════════════════════════════════════════════════════════════════════════════

class TranslateWorker(QThread):
    progress  = pyqtSignal(int)
    result    = pyqtSignal(str)
    error     = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, source, target_lang: str, source_lang: str = "auto",
                 provider: str = "google", glossary: GlossaryManager | None = None,
                 is_text_mode: bool = False) -> None:
        super().__init__()
        # source = file path (str) OR raw text (str, is_text_mode=True)
        self._source      = source
        self._target_lang = target_lang
        self._source_lang = source_lang
        self._provider    = provider
        self._glossary    = glossary
        self._is_text_mode = is_text_mode
        self._translator  = TranslatorModule()
        self._stop        = False
        self._temp_output = ""

    def cancel(self) -> None:
        self._stop = True

    def get_temp_output(self) -> str:
        return self._temp_output

    def _check(self) -> None:
        if self._stop:
            raise _Cancelled()

    def _translate(self, text: str) -> str:
        self._check()
        if self._glossary and not self._glossary.is_empty():
            processed, pm = self._glossary.apply(text)
            translated = self._translator.translate_text(
                processed, self._target_lang, self._source_lang, self._provider
            )
            return self._glossary.restore(translated, pm)
        return self._translator.translate_text(
            text, self._target_lang, self._source_lang, self._provider
        )

    def run(self) -> None:
        temp_path = ""
        try:
            handler = FileHandler()

            if self._is_text_mode:
                fd, temp_path = tempfile.mkstemp(suffix=".txt")
                os.close(fd)

                def progress_cb(v: int) -> None:
                    self._check()
                    self.progress.emit(v)

                preview = self._translator.translate_text(
                    self._source, self._target_lang, self._source_lang,
                    self._provider, progress_callback=progress_cb,
                )
                Path(temp_path).write_text(preview, encoding="utf-8")
            else:
                out_ext = handler.get_output_extension(self._source)
                ext     = Path(self._source).suffix.lower()
                fd, temp_path = tempfile.mkstemp(suffix=out_ext)
                os.close(fd)

                if ext in (".xlsx", ".csv", ".docx"):
                    preview = handler.translate_file_structured(
                        self._source, temp_path,
                        self._translate,
                        progress_callback=self.progress.emit,
                    )
                else:
                    content = handler.read_file(self._source)

                    def progress_cb(v: int) -> None:
                        self._check()
                        self.progress.emit(v)

                    preview = self._translator.translate_text(
                        content, self._target_lang, self._source_lang,
                        self._provider, progress_callback=progress_cb,
                    )
                    handler.write_file(temp_path, preview, self._source)

            self._temp_output = temp_path
            self.result.emit(preview)

        except _Cancelled:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)
            self.cancelled.emit()
        except Exception as exc:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)
            self.error.emit(str(exc))


class BatchWorker(QThread):
    file_started = pyqtSignal(int)            # file index
    file_done    = pyqtSignal(int, str)       # index, temp_path
    file_error   = pyqtSignal(int, str)       # index, error_msg
    overall      = pyqtSignal(int)            # overall progress 0-100
    all_done     = pyqtSignal()
    cancelled    = pyqtSignal()

    def __init__(self, files: list[str], target_lang: str, source_lang: str = "auto",
                 provider: str = "google", glossary: GlossaryManager | None = None) -> None:
        super().__init__()
        self._files       = files
        self._target_lang = target_lang
        self._source_lang = source_lang
        self._provider    = provider
        self._glossary    = glossary
        self._translator  = TranslatorModule()
        self._stop        = False
        self._outputs: dict[int, str] = {}   # index → temp_path

    def cancel(self) -> None:
        self._stop = True

    def get_outputs(self) -> dict[int, str]:
        return dict(self._outputs)

    def _check(self) -> None:
        if self._stop:
            raise _Cancelled()

    def _translate(self, text: str) -> str:
        self._check()
        if self._glossary and not self._glossary.is_empty():
            processed, pm = self._glossary.apply(text)
            translated = self._translator.translate_text(
                processed, self._target_lang, self._source_lang, self._provider
            )
            return self._glossary.restore(translated, pm)
        return self._translator.translate_text(
            text, self._target_lang, self._source_lang, self._provider
        )

    def run(self) -> None:
        try:
            handler = FileHandler()
            for i, fp in enumerate(self._files):
                self._check()
                self.file_started.emit(i)
                try:
                    out_ext = handler.get_output_extension(fp)
                    ext     = Path(fp).suffix.lower()
                    fd, tmp = tempfile.mkstemp(suffix=out_ext)
                    os.close(fd)

                    if ext in (".xlsx", ".csv", ".docx"):
                        handler.translate_file_structured(fp, tmp, self._translate)
                    else:
                        content  = handler.read_file(fp)
                        preview  = self._translate(content)
                        handler.write_file(tmp, preview, fp)

                    self._outputs[i] = tmp
                    self.file_done.emit(i, tmp)
                except _Cancelled:
                    raise
                except Exception as exc:
                    self.file_error.emit(i, str(exc))

                self.overall.emit(int((i + 1) / len(self._files) * 100))

            self.all_done.emit()
        except _Cancelled:
            self.cancelled.emit()


# ══════════════════════════════════════════════════════════════════════════════
# Drop area widget
# ══════════════════════════════════════════════════════════════════════════════

class DropArea(QFrame):
    file_selected = pyqtSignal(str)
    clicked       = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("drop_area")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(90)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(3)

        icon = QLabel("📂")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 24))
        hint = QLabel("Drag & drop or click to browse")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setObjectName("subtitle")
        self.file_label = QLabel("No file selected")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setObjectName("subtitle")
        lay.addWidget(icon); lay.addWidget(hint); lay.addWidget(self.file_label)

    def set_file(self, path: str) -> None:
        self.file_label.setText(f"📄  {Path(path).name}")
        self.file_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")

    def mousePressEvent(self, _) -> None:
        self.clicked.emit()

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self.setProperty("drag_active", "true")
            self.style().polish(self)

    def dragLeaveEvent(self, _) -> None:
        self.setProperty("drag_active", "false")
        self.style().polish(self)

    def dropEvent(self, e: QDropEvent) -> None:
        self.setProperty("drag_active", "false")
        self.style().polish(self)
        urls = e.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if Path(path).suffix.lower() in SUPPORTED_EXTENSIONS:
            self.file_selected.emit(path)
        else:
            QMessageBox.warning(self, "Unsupported File",
                f"Please use: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")


# ══════════════════════════════════════════════════════════════════════════════
# Main window
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._file_handler    = FileHandler()
        self._glossary        = GlossaryManager()
        self._history         = HistoryManager()
        self._current_file    = ""
        self._original_text   = ""
        self._translated_text = ""
        self._temp_translated = ""
        self._split_mode      = False
        self._batch_files: list[str] = []
        self._batch_outputs: dict[int, str] = {}
        self._worker: QThread | None = None

        self.setWindowTitle("File Translator Tool")
        self.setMinimumSize(1020, 700)
        self.resize(1280, 750)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self._build_header())
        lay.addWidget(self._build_body(), stretch=1)
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Ready — select a file or paste text to get started.")

    def _build_header(self) -> QWidget:
        hdr = QWidget()
        hdr.setFixedHeight(62)
        hdr.setStyleSheet("background-color:#181825;border-bottom:1px solid #313244;")
        lay = QHBoxLayout(hdr)
        lay.setContentsMargins(24, 0, 16, 0)

        title = QLabel("🌐  File Translator")
        title.setObjectName("title")
        lay.addWidget(title)
        lay.addStretch()

        for label, slot in [("📋  History", self._show_history),
                             ("🔤  Glossary", self._show_glossary)]:
            btn = QPushButton(label)
            btn.setObjectName("small_btn")
            btn.clicked.connect(slot)
            lay.addWidget(btn)

        fmt = QLabel("  .txt · .docx · .pdf · .csv · .xlsx  ")
        fmt.setObjectName("subtitle")
        lay.addWidget(fmt)
        return hdr

    def _build_body(self) -> QWidget:
        body = QWidget()
        lay  = QHBoxLayout(body)
        lay.setContentsMargins(18, 18, 18, 18)
        lay.setSpacing(18)
        left = self._build_left_panel()
        left.setFixedWidth(330)
        lay.addWidget(left)
        lay.addWidget(self._build_right_panel(), stretch=1)
        return body

    # ── Left panel ────────────────────────────────────────────────────────────

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        lay   = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        # 1 · Upload (single file)
        lay.addWidget(self._sl("1  ·  Upload File"))
        self._drop_area = DropArea(self)
        self._drop_area.file_selected.connect(self._load_file)
        self._drop_area.clicked.connect(self._browse_file)
        lay.addWidget(self._drop_area)

        browse_row = QHBoxLayout()
        br = QPushButton("Browse File…")
        br.setObjectName("secondary")
        br.clicked.connect(self._browse_file)
        browse_row.addWidget(br, stretch=1)
        batch_add = QPushButton("+ Batch")
        batch_add.setObjectName("batch_add")
        batch_add.setToolTip("Add files to batch translation queue")
        batch_add.clicked.connect(self._batch_add_files)
        browse_row.addWidget(batch_add)
        lay.addLayout(browse_row)

        # Batch queue (hidden until files added)
        self._batch_frame = QFrame()
        self._batch_frame.setObjectName("batch_frame")
        blay = QVBoxLayout(self._batch_frame)
        blay.setContentsMargins(6, 6, 6, 6)
        blay.setSpacing(4)
        batch_hdr = QHBoxLayout()
        batch_hdr.addWidget(QLabel("📦  Batch Queue"))
        batch_hdr.addStretch()
        clr = QPushButton("Clear")
        clr.setObjectName("secondary")
        clr.setFixedHeight(24)
        clr.clicked.connect(self._batch_clear)
        batch_hdr.addWidget(clr)
        blay.addLayout(batch_hdr)
        self._batch_list = QListWidget()
        self._batch_list.setMaximumHeight(110)
        blay.addWidget(self._batch_list)
        self._batch_frame.setVisible(False)
        lay.addWidget(self._batch_frame)

        # 2 · Languages
        lay.addSpacing(2)
        lay.addWidget(self._sl("2  ·  Languages"))

        for label, attr, items, default in [
            ("Source:", "_src_combo",      SOURCE_LANGUAGES, "Auto-detect"),
            ("Target:", "_lang_combo",     LANGUAGES,        "Vietnamese"),
            ("Provider:", "_prov_combo",   PROVIDERS,        "Google Translate (Free)"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(58)
            cb = QComboBox()
            for k in items:
                cb.addItem(k)
            cb.setCurrentText(default)
            setattr(self, attr, cb)
            row.addWidget(lbl)
            row.addWidget(cb, stretch=1)
            lay.addLayout(row)

        self._detected_label = QLabel("Detected source: —")
        self._detected_label.setObjectName("subtitle")
        lay.addWidget(self._detected_label)

        # 3 · Translate
        lay.addSpacing(2)
        lay.addWidget(self._sl("3  ·  Translate"))

        btn_row = QHBoxLayout()
        self._translate_btn = QPushButton("⚡  Translate File")
        self._translate_btn.setEnabled(False)
        self._translate_btn.clicked.connect(self._start_translation)
        btn_row.addWidget(self._translate_btn, stretch=1)

        self._cancel_btn = QPushButton("✕")
        self._cancel_btn.setObjectName("cancel_btn")
        self._cancel_btn.setFixedWidth(42)
        self._cancel_btn.setVisible(False)
        self._cancel_btn.clicked.connect(self._cancel_translation)
        btn_row.addWidget(self._cancel_btn)
        lay.addLayout(btn_row)

        self._progress_bar = QProgressBar()
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(6)
        lay.addWidget(self._progress_bar)

        self._progress_label = QLabel("")
        self._progress_label.setObjectName("subtitle")
        lay.addWidget(self._progress_label)

        # 4 · Export
        lay.addSpacing(2)
        lay.addWidget(self._sl("4  ·  Export"))

        self._export_btn = QPushButton("💾  Download Translated File")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._export_file)
        lay.addWidget(self._export_btn)

        self._batch_dl_btn = QPushButton("📦  Download All as ZIP")
        self._batch_dl_btn.setEnabled(False)
        self._batch_dl_btn.clicked.connect(self._export_batch_zip)
        lay.addWidget(self._batch_dl_btn)

        lay.addStretch()
        return panel

    # ── Right panel ───────────────────────────────────────────────────────────

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        lay   = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        hdr = QHBoxLayout()
        hdr.addWidget(self._sl("Preview"))
        hdr.addStretch()
        self._split_btn = QPushButton("⇔  Split View")
        self._split_btn.setObjectName("small_btn")
        self._split_btn.setCheckable(True)
        self._split_btn.clicked.connect(self._toggle_split)
        hdr.addWidget(self._split_btn)
        lay.addLayout(hdr)

        # Shared editors
        self._original_view = QTextEdit()
        self._original_view.setReadOnly(True)
        self._original_view.setPlaceholderText("File content will appear here…")

        self._paste_view = QTextEdit()
        self._paste_view.setPlaceholderText(
            "Paste text here and click ⚡ Translate Text…"
        )
        self._paste_view.textChanged.connect(self._on_paste_text_changed)

        self._translated_view = QTextEdit()
        self._translated_view.setPlaceholderText(
            "Translated text will appear here — you can edit before downloading."
        )

        # Tab mode
        self._tab_widget = QTabWidget()
        self._tab_widget.addTab(self._original_view,   "  📄 Original  ")
        self._tab_widget.addTab(self._paste_view,      "  📝 Paste Text  ")
        self._tab_widget.addTab(self._translated_view, "  🔤 Translated ✏️  ")
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

        # Split mode — wrapper panes (text views added only when toggled on)
        self._split_widget = QSplitter(Qt.Orientation.Horizontal)

        orig_w = QWidget(); ol = QVBoxLayout(orig_w); ol.setContentsMargins(0,0,0,0); ol.setSpacing(2)
        ol.addWidget(QLabel("Original", objectName="panel_title"))
        # _original_view is NOT added here; it lives in _tab_widget by default

        tran_w = QWidget(); tl = QVBoxLayout(tran_w); tl.setContentsMargins(0,0,0,0); tl.setSpacing(2)
        tl.addWidget(QLabel("Translated  ✏️", objectName="panel_title"))
        # _translated_view is NOT added here; it lives in _tab_widget by default

        self._split_widget.addWidget(orig_w)
        self._split_widget.addWidget(tran_w)
        self._split_widget.setSizes([500, 500])
        self._split_widget.setVisible(False)

        lay.addWidget(self._tab_widget)
        lay.addWidget(self._split_widget)
        return panel

    @staticmethod
    def _sl(text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setObjectName("section")
        return lbl

    # ── Split view ────────────────────────────────────────────────────────────

    def _toggle_split(self) -> None:
        self._split_mode = self._split_btn.isChecked()
        if self._split_mode:
            # Remove original & translated from tab widget, move to splitter panes
            # (paste_view stays in the hidden tab_widget)
            idx_orig = self._tab_widget.indexOf(self._original_view)
            if idx_orig != -1:
                self._tab_widget.removeTab(idx_orig)
            idx_tran = self._tab_widget.indexOf(self._translated_view)
            if idx_tran != -1:
                self._tab_widget.removeTab(idx_tran)

            self._split_widget.widget(0).layout().addWidget(self._original_view)
            self._split_widget.widget(1).layout().addWidget(self._translated_view)
            self._tab_widget.setVisible(False)
            self._split_widget.setVisible(True)
        else:
            # Move them back into the tab widget at the correct positions
            # paste_view is already at some index; insert original before it
            self._tab_widget.insertTab(0, self._original_view, "  📄 Original  ")
            # paste_view is now at index 1 — add translated at the end
            self._tab_widget.addTab(self._translated_view, "  🔤 Translated ✏️  ")
            self._split_widget.setVisible(False)
            self._tab_widget.setVisible(True)
            if self._translated_text:
                self._tab_widget.setCurrentIndex(2)

    # ── Tab / paste-text state ────────────────────────────────────────────────

    def _on_tab_changed(self, index: int) -> None:
        self._update_translate_btn()

    def _on_paste_text_changed(self) -> None:
        self._update_translate_btn()

    def _update_translate_btn(self) -> None:
        n_batch = len(self._batch_files)
        if n_batch > 0:
            self._translate_btn.setText(f"📦  Translate All  ({n_batch} files)")
            self._translate_btn.setEnabled(True)
        elif not self._split_mode and self._tab_widget.currentIndex() == 1:
            has_text = bool(self._paste_view.toPlainText().strip())
            self._translate_btn.setText("⚡  Translate Text")
            self._translate_btn.setEnabled(has_text)
        elif self._current_file:
            self._translate_btn.setText("⚡  Translate File")
            self._translate_btn.setEnabled(True)
        else:
            self._translate_btn.setText("⚡  Translate File")
            self._translate_btn.setEnabled(False)

    # ── File loading ──────────────────────────────────────────────────────────

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select a File to Translate", "",
            "Supported Files (*.txt *.docx *.pdf *.csv *.xlsx);;"
            "All Files (*)",
        )
        if path:
            self._load_file(path)

    def _load_file(self, path: str) -> None:
        try:
            self._status.showMessage(f"Reading  {Path(path).name} …")
            content = self._file_handler.read_file(path)

            self._current_file    = path
            self._original_text   = content
            self._translated_text = ""
            self._cleanup_temp()

            self._original_view.setPlainText(content)
            self._translated_view.setPlainText("")
            self._translated_view.document().setModified(False)
            self._drop_area.set_file(path)

            if not self._split_mode:
                self._tab_widget.setCurrentIndex(0)

            # Auto-detect source language
            detected = TranslatorModule().detect_language(content)
            if detected != "unknown":
                self._detected_label.setText(f"Detected source: {detected.upper()}")
                for name, code in SOURCE_LANGUAGES.items():
                    if code == detected:
                        self._src_combo.setCurrentText(name)
                        break
            else:
                self._detected_label.setText("Detected source: —")

            self._export_btn.setEnabled(False)
            self._progress_bar.setValue(0)
            self._progress_label.setText("")
            self._update_translate_btn()
            self._status.showMessage(
                f"Loaded  {Path(path).name}  —  {len(content):,} characters"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Error Reading File", str(exc))

    # ── Batch queue ───────────────────────────────────────────────────────────

    def _batch_add_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add Files to Batch", "",
            "Supported Files (*.txt *.docx *.pdf *.csv *.xlsx)",
        )
        for p in paths:
            if p not in self._batch_files:
                self._batch_files.append(p)
                self._batch_list.addItem(f"⏳  {Path(p).name}")

        self._batch_frame.setVisible(bool(self._batch_files))
        self._update_translate_btn()

    def _batch_clear(self) -> None:
        self._batch_files.clear()
        self._batch_outputs.clear()
        self._batch_list.clear()
        self._batch_frame.setVisible(False)
        self._batch_dl_btn.setEnabled(False)
        self._update_translate_btn()

    def _batch_set_item_status(self, index: int, text: str) -> None:
        item = self._batch_list.item(index)
        if item:
            item.setText(text)

    # ── Translation ───────────────────────────────────────────────────────────

    def _get_lang_params(self) -> tuple[str, str, str]:
        target_code = LANGUAGES[self._lang_combo.currentText()]
        source_code = SOURCE_LANGUAGES[self._src_combo.currentText()]
        provider    = PROVIDERS[self._prov_combo.currentText()]
        return target_code, source_code, provider

    def _start_translation(self) -> None:
        target_code, source_code, provider = self._get_lang_params()

        self._translate_btn.setVisible(False)
        self._cancel_btn.setVisible(True)
        self._cancel_btn.setEnabled(True)
        self._export_btn.setEnabled(False)
        self._batch_dl_btn.setEnabled(False)
        self._progress_bar.setValue(0)

        if self._batch_files:
            self._start_batch(target_code, source_code, provider)
        elif not self._split_mode and self._tab_widget.currentIndex() == 1:
            self._start_text(target_code, source_code, provider)
        else:
            self._start_file(target_code, source_code, provider)

    def _start_file(self, target_code, source_code, provider) -> None:
        self._progress_label.setText("Starting translation…")
        self._status.showMessage(f"Translating  {Path(self._current_file).name} …")
        w = TranslateWorker(
            self._current_file, target_code, source_code, provider, self._glossary
        )
        w.progress.connect(self._on_progress)
        w.result.connect(self._on_result)
        w.error.connect(self._on_error)
        w.cancelled.connect(self._on_cancelled)
        self._worker = w
        w.start()

    def _start_text(self, target_code, source_code, provider) -> None:
        text = self._paste_view.toPlainText().strip()
        self._progress_label.setText("Translating text…")
        self._status.showMessage("Translating pasted text…")
        w = TranslateWorker(
            text, target_code, source_code, provider, self._glossary,
            is_text_mode=True,
        )
        w.progress.connect(self._on_progress)
        w.result.connect(self._on_result)
        w.error.connect(self._on_error)
        w.cancelled.connect(self._on_cancelled)
        self._worker = w
        w.start()

    def _start_batch(self, target_code, source_code, provider) -> None:
        self._batch_outputs.clear()
        for i in range(self._batch_list.count()):
            name = Path(self._batch_files[i]).name
            self._batch_set_item_status(i, f"⏳  {name}")
        self._progress_label.setText(f"Batch: 0 / {len(self._batch_files)}")
        self._status.showMessage(f"Translating {len(self._batch_files)} files…")

        w = BatchWorker(self._batch_files, target_code, source_code, provider, self._glossary)
        w.file_started.connect(self._on_batch_file_started)
        w.file_done.connect(self._on_batch_file_done)
        w.file_error.connect(self._on_batch_file_error)
        w.overall.connect(self._on_batch_overall)
        w.all_done.connect(self._on_batch_all_done)
        w.cancelled.connect(self._on_cancelled)
        self._worker = w
        w.start()

    def _cancel_translation(self) -> None:
        if self._worker and self._worker.isRunning():
            if hasattr(self._worker, "cancel"):
                self._worker.cancel()
            self._cancel_btn.setEnabled(False)
            self._progress_label.setText("Cancelling…")

    # ── Worker callbacks: single file / text ──────────────────────────────────

    def _on_progress(self, value: int) -> None:
        self._progress_bar.setValue(value)
        self._progress_label.setText(f"Translating…  {value}%")

    def _on_result(self, text: str) -> None:
        self._translated_text = text
        self._temp_translated = (
            self._worker.get_temp_output() if hasattr(self._worker, "get_temp_output") else ""
        )
        self._translated_view.setPlainText(text)
        self._translated_view.document().setModified(False)

        if not self._split_mode:
            self._tab_widget.setCurrentIndex(2)

        self._done_ui()
        self._export_btn.setEnabled(True)
        self._progress_bar.setValue(100)
        self._progress_label.setText("Translation complete ✓")
        self._status.showMessage(
            f"Done — translated to {self._lang_combo.currentText()}"
        )
        # Save to history
        filename = Path(self._current_file).name if self._current_file else "Pasted text"
        self._history.add(
            filename    = filename,
            source_lang = self._src_combo.currentText(),
            target_lang = self._lang_combo.currentText(),
            provider    = self._prov_combo.currentText(),
            char_count  = len(self._original_text or self._paste_view.toPlainText()),
        )

    def _on_error(self, msg: str) -> None:
        self._done_ui()
        self._progress_label.setText("Translation failed.")
        self._status.showMessage("Error — see dialog.")
        QMessageBox.critical(self, "Translation Error",
            f"Could not translate:\n\n{msg}\n\nCheck your internet connection.")

    def _on_cancelled(self) -> None:
        self._done_ui()
        self._progress_bar.setValue(0)
        self._progress_label.setText("Cancelled.")
        self._status.showMessage("Translation cancelled.")

    def _done_ui(self) -> None:
        self._translate_btn.setVisible(True)
        self._cancel_btn.setVisible(False)
        self._cancel_btn.setEnabled(True)
        self._update_translate_btn()

    # ── Worker callbacks: batch ───────────────────────────────────────────────

    def _on_batch_file_started(self, i: int) -> None:
        name = Path(self._batch_files[i]).name
        self._batch_set_item_status(i, f"🔄  {name}")

    def _on_batch_file_done(self, i: int, tmp: str) -> None:
        name = Path(self._batch_files[i]).name
        self._batch_outputs[i] = tmp
        self._batch_set_item_status(i, f"✅  {name}")

    def _on_batch_file_error(self, i: int, msg: str) -> None:
        name = Path(self._batch_files[i]).name
        self._batch_set_item_status(i, f"❌  {name}")

    def _on_batch_overall(self, value: int) -> None:
        self._progress_bar.setValue(value)
        done = len(self._batch_outputs)
        self._progress_label.setText(
            f"Batch: {done} / {len(self._batch_files)}  ({value}%)"
        )

    def _on_batch_all_done(self) -> None:
        self._done_ui()
        self._progress_bar.setValue(100)
        n = len(self._batch_outputs)
        self._progress_label.setText(f"Batch done ✓  ({n} files translated)")
        self._status.showMessage(f"Batch complete — {n} files translated.")
        self._batch_dl_btn.setEnabled(True)
        self._history.add(
            filename    = f"Batch ({n} files)",
            source_lang = self._src_combo.currentText(),
            target_lang = self._lang_combo.currentText(),
            provider    = self._prov_combo.currentText(),
            char_count  = 0,
        )

    # ── Export ────────────────────────────────────────────────────────────────

    def _export_file(self) -> None:
        if not self._current_file and not self._paste_view.toPlainText():
            return
        orig_path = Path(self._current_file) if self._current_file else Path("translated_text")
        out_ext   = (self._file_handler.get_output_extension(self._current_file)
                     if self._current_file else ".txt")
        lang_slug = self._lang_combo.currentText().replace(" ", "_")
        suggested = orig_path.parent / f"{orig_path.stem}_{lang_slug}{out_ext}"

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Translated File", str(suggested), f"Files (*{out_ext})"
        )
        if not save_path:
            return

        try:
            edited_text   = self._translated_view.toPlainText()
            user_edited   = self._translated_view.document().isModified()
            ext           = Path(self._current_file).suffix.lower() if self._current_file else ".txt"
            is_structured = ext in (".xlsx", ".csv", ".docx")

            if self._temp_translated and Path(self._temp_translated).exists():
                if is_structured and user_edited:
                    reply = QMessageBox.question(
                        self, "Manual Edits Detected",
                        "You edited the preview.\n\n"
                        "• Yes  → Download structured file (edits ignored)\n"
                        "• No   → Download your edited text as plain .txt",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        | QMessageBox.StandardButton.Cancel,
                    )
                    if reply == QMessageBox.StandardButton.Cancel:
                        return
                    if reply == QMessageBox.StandardButton.No:
                        txt_path = str(Path(save_path).with_suffix(".txt"))
                        Path(txt_path).write_text(edited_text, encoding="utf-8")
                        self._status.showMessage(f"Saved  {Path(txt_path).name}")
                        QMessageBox.information(self, "Saved", f"Saved as plain text:\n{txt_path}")
                        return
                shutil.copy2(self._temp_translated, save_path)
            else:
                self._file_handler.write_file(save_path, edited_text,
                                              self._current_file or save_path)

            self._status.showMessage(f"Saved  {Path(save_path).name}")
            QMessageBox.information(self, "File Saved",
                f"Translated file saved successfully:\n\n{save_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", str(exc))

    def _export_batch_zip(self) -> None:
        if not self._batch_outputs:
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Batch as ZIP", "translated_files.zip", "ZIP (*.zip)"
        )
        if not save_path:
            return
        try:
            with zipfile.ZipFile(save_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, tmp in self._batch_outputs.items():
                    if Path(tmp).exists():
                        orig = Path(self._batch_files[i])
                        out_ext = self._file_handler.get_output_extension(str(orig))
                        lang_slug = self._lang_combo.currentText().replace(" ", "_")
                        arcname = f"{orig.stem}_{lang_slug}{out_ext}"
                        zf.write(tmp, arcname)
            self._status.showMessage(f"ZIP saved:  {Path(save_path).name}")
            QMessageBox.information(self, "Batch Saved",
                f"All translated files saved to:\n\n{save_path}")
        except Exception as exc:
            QMessageBox.critical(self, "ZIP Error", str(exc))

    # ── Dialogs ───────────────────────────────────────────────────────────────

    def _show_glossary(self) -> None:
        dlg = GlossaryDialog(self._glossary, self)
        dlg.setStyleSheet(DARK_STYLE)
        dlg.exec()

    def _show_history(self) -> None:
        dlg = HistoryDialog(self._history, self)
        dlg.setStyleSheet(DARK_STYLE)
        dlg.exec()

    # ── Temp cleanup ──────────────────────────────────────────────────────────

    def _cleanup_temp(self) -> None:
        if self._temp_translated:
            Path(self._temp_translated).unlink(missing_ok=True)
            self._temp_translated = ""
        for tmp in self._batch_outputs.values():
            Path(tmp).unlink(missing_ok=True)
        self._batch_outputs.clear()

    def closeEvent(self, event) -> None:
        if self._worker and self._worker.isRunning():
            if hasattr(self._worker, "cancel"):
                self._worker.cancel()
            self._worker.wait(2000)
        self._cleanup_temp()
        super().closeEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
