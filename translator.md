You are a senior Python developer.

Build a complete desktop tool that can automatically translate files into a selected language.

The application must include a modern graphical user interface and be easy to use.

------------------------------------------------

PROJECT GOAL

Create a Python application that:

• Allows users to upload a file
• Automatically detects text inside the file
• Translates the content into a chosen language
• Saves the translated file
• Displays results in the UI

------------------------------------------------

TECH STACK

Use Python.

Preferred libraries:

GUI
- Tkinter or PyQt6

Translation
- deep-translator OR googletrans

File handling
- python-docx
- PyPDF2
- pandas (for Excel)

------------------------------------------------

SUPPORTED FILE TYPES

The tool must support translating:

- .txt
- .docx
- .pdf
- .csv
- .xlsx

------------------------------------------------

USER INTERFACE REQUIREMENTS

The UI should include:

1. File upload button
2. Dropdown to choose target language
3. Button: "Translate File"
4. Output preview area
5. Progress indicator
6. Button to download translated file

------------------------------------------------

LANGUAGE OPTIONS

Allow users to select languages such as:

English
Vietnamese
Japanese
Chinese
Korean
French
German
Spanish

------------------------------------------------

WORKFLOW

1. User selects a file
2. User selects target language
3. Application reads the file content
4. Text is sent to translation API
5. Translated text is displayed
6. User can save translated version

------------------------------------------------

UI LAYOUT

-----------------------------------------
| File Translator Tool                  |
-----------------------------------------

Select File: [Browse]

Target Language:
[Dropdown]

[Translate File]

-----------------------------------------
Preview Window
-----------------------------------------

Translated Text Displayed Here

-----------------------------------------

[Download Translated File]

-----------------------------------------

------------------------------------------------

FEATURES

The tool should include:

• Clean modern UI
• Error handling
• File format detection
• Progress feedback
• Save translated file

------------------------------------------------

OUTPUT

Generate:

1. Full Python source code
2. Requirements.txt
3. Instructions to run the application
4. Example UI layout
5. Well-commented code

------------------------------------------------

EXTRA (OPTIONAL)

If possible also implement:

• Auto language detection
• Drag and drop file support
• Dark mode UI
• Batch translation (multiple files)