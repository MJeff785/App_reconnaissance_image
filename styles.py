from tkinter import ttk

class ModernStyle:
    COLORS = {
        'primary': '#155C32',
        'secondary': '#024F22',
        'background': '#F8F9FA',  # Lighter background
        'surface': '#FFFFFF',     # White surface
        'accent': '#198754',      # Accent color
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'border': '#DEE2E6'
    }
    
    FONTS = {
        'title': ('Segoe UI', 32, 'bold'),
        'subtitle': ('Segoe UI', 24, 'normal'),
        'heading': ('Segoe UI', 20, 'normal'),
        'body': ('Segoe UI', 12),
        'button': ('Segoe UI', 11, 'bold'),
        'label': ('Segoe UI', 12)
    }
    
    @staticmethod
    def apply(root):
        style = ttk.Style(root)
        style.theme_use('clam')
        
        # Window configuration
        root.configure(background=ModernStyle.COLORS['background'])
        
        # Frame styles
        style.configure('Modern.TFrame',
                       background=ModernStyle.COLORS['background'])
        
        style.configure('Surface.TFrame',
                       background=ModernStyle.COLORS['surface'],
                       relief='flat',
                       borderwidth=1)
        
        # Button styles
        style.configure('Modern.TButton',
                       padding=(25, 12),
                       font=ModernStyle.FONTS['button'],
                       background=ModernStyle.COLORS['primary'],
                       foreground='white',
                       borderwidth=0,
                       relief='flat')
        
        style.map('Modern.TButton',
                 background=[('active', ModernStyle.COLORS['secondary'])],
                 foreground=[('active', 'white')])
        
        # Label styles
        style.configure('Title.TLabel',
                       font=ModernStyle.FONTS['title'],
                       background=ModernStyle.COLORS['background'],
                       foreground=ModernStyle.COLORS['text_primary'])
        
        style.configure('Subtitle.TLabel',
                       font=ModernStyle.FONTS['subtitle'],
                       background=ModernStyle.COLORS['background'],
                       foreground=ModernStyle.COLORS['text_secondary'])
        
        style.configure('Modern.TLabel',
                       font=ModernStyle.FONTS['body'],
                       background=ModernStyle.COLORS['surface'],
                       foreground=ModernStyle.COLORS['text_primary'])
        
        # Entry styles
        style.configure('Modern.TEntry',
                       padding=12,
                       font=ModernStyle.FONTS['body'],
                       fieldbackground=ModernStyle.COLORS['surface'],
                       borderwidth=1,
                       relief='solid')
        
        # Combobox styles
        style.configure('Modern.TCombobox',
                       padding=12,
                       font=ModernStyle.FONTS['body'],
                       fieldbackground=ModernStyle.COLORS['surface'],
                       borderwidth=1,
                       arrowsize=15)
        
        # Labelframe styles
        style.configure('Modern.TLabelframe',
                       background=ModernStyle.COLORS['surface'],
                       padding=25,
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Modern.TLabelframe.Label',
                       font=ModernStyle.FONTS['heading'],
                       background=ModernStyle.COLORS['surface'],
                       foreground=ModernStyle.COLORS['text_primary'])