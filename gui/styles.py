
# Color Palette
COLORS = {
    "bg_main": "#F1F5F9",  # Light blue-gray background
    "bg_panel": "#FFFFFF",  # White for sidebars/panels
    "accent": "#2563EB",  # Corporate blue for buttons
    "accent_hover": "#1D4ED8",
    "text_main": "#1E293B",  # Dark slate for text
    "text_muted": "#64748B",  # Gray for hints
    "success": "#059669",  # Emerald green for status
    "error": "#DC2626",  # Red for errors
    "border": "#E2E8F0",  # Soft gray for dividers
    "error_bg": "#ffcccc",  # light red
    "entry_bg": "#ffffff",  # white
}

FONTS = {
    "title": ("Segoe UI", 14, "bold"),
    "header": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "mono": ("Consolas", 10),
    "button": ("Segoe UI", 11, "bold")
}


def configure_styles():
    """Configures the global ttk styles."""
    import tkinter.ttk as ttk
    style = ttk.Style()

    # Notebook/Tabs styling
    style.configure("TNotebook", background=COLORS["bg_main"], padding=5)
    style.configure("TNotebook.Tab", padding=[15, 5], font=FONTS["body"])

    # Progressbar styling
    style.configure("SGA.Horizontal.TProgressbar",
                    thickness=8,
                    troughcolor=COLORS["border"],
                    background=COLORS["accent"])

    # Custom Combobox
    style.configure("TCombobox", padding=5)
