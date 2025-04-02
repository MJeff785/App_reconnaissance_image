from tkinter import ttk

class ModernStyle:
    COLORS = {
        'primary': '#2962ff',
        'secondary': '#455a64',
        'background': '#ffffff',
        'surface': '#f5f5f5',
        'success': '#00c853',
        'error': '#d50000',
        'text': '#263238'
    }
    
    FONTS = {
        'title': ('Segoe UI', 24, 'bold'),
        'subtitle': ('Segoe UI', 18),
        'body': ('Segoe UI', 11),
        'button': ('Segoe UI', 10),
        'label': ('Segoe UI', 11)
    }
    
    @staticmethod
    def apply(root):
        style = ttk.Style(root)
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('Modern.TFrame', 
                       background=ModernStyle.COLORS['background'])
        
        style.configure('Surface.TFrame',
                       background=ModernStyle.COLORS['surface'])
        
        # Configure button styles
        style.configure('Modern.TButton',
                       padding=(20, 10),
                       font=ModernStyle.FONTS['button'],
                       background=ModernStyle.COLORS['primary'])
        
        style.map('Modern.TButton',
                 background=[('active', ModernStyle.COLORS['secondary'])])
        
        # Configure label styles
        style.configure('Modern.TLabel',
                       font=ModernStyle.FONTS['body'],
                       background=ModernStyle.COLORS['background'])
        
        style.configure('Title.TLabel',
                       font=ModernStyle.FONTS['title'],
                       background=ModernStyle.COLORS['background'])
        
        style.configure('Subtitle.TLabel',
                       font=ModernStyle.FONTS['subtitle'],
                       background=ModernStyle.COLORS['background'])
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                       padding=10,
                       font=ModernStyle.FONTS['body'])
        
        # Configure combobox styles
        style.configure('Modern.TCombobox',
                       padding=10,
                       font=ModernStyle.FONTS['body'])
        
        # Configure labelframe styles
        style.configure('Modern.TLabelframe',
                       background=ModernStyle.COLORS['surface'],
                       padding=20)
        
        style.configure('Modern.TLabelframe.Label',
                       font=ModernStyle.FONTS['subtitle'],
                       background=ModernStyle.COLORS['surface'])