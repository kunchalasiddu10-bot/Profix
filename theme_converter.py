import os
import re

directory = '.'

css_replacements = {
    '--bg-color: #0f172a;': '--bg-color: #FAFAFA;',
    '--text-primary: #f8fafc;': '--text-primary: #1A1A1A;',
    '--text-secondary: #94a3b8;': '--text-secondary: #737373;',
    '--accent-primary: #3b82f6;': '--accent-primary: #4A5D4E;',
    '--accent-hover: #2563eb;': '--accent-hover: #3E4D41;',
    '--accent-secondary: #8b5cf6;': '--accent-secondary: #E8EDE6;',
    '--card-bg: rgba(30, 41, 59, 0.7);': '--card-bg: #FFFFFF;',
    '--border-color: rgba(255, 255, 255, 0.1);': '--border-color: #E5E7EB;',
    '--glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);': '--glass-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);',
    'backdrop-filter: blur(12px);': '/* backdrop-filter removed */',
    '-webkit-backdrop-filter: blur(12px);': '/* webkit-backdrop-filter removed */',
    'background: linear-gradient(135deg, #fff, #94a3b8);': 'background: var(--text-primary);',
    '-webkit-background-clip: text;': '/* webkit-background-clip removed */',
    '-webkit-text-fill-color: transparent;': '/* webkit-text-fill-color removed */',
    'background: rgba(15, 23, 42, 0.8);': 'background: #FFFFFF;',
    'background: rgba(15, 23, 42, 0.9);': 'background: #FFFFFF;',
    'background: rgba(15, 23, 42, 0.95);': 'background: #FFFFFF;',
    'background: rgba(30, 41, 59, 0.8)': 'background: #FFFFFF',
    'background: rgba(30, 41, 59, 0.9)': 'background: #FFFFFF',
    'box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);': 'box-shadow: 0 4px 12px rgba(74, 93, 78, 0.2);',
    'color: white;': 'color: var(--text-primary);',
    'background: rgba(0, 0, 0, 0.6);': 'background: rgba(0, 0, 0, 0.2);',
    'background: rgba(0, 0, 0, 0.2);': 'background: #FFFFFF;',
    'background: rgba(255, 255, 255, 0.05);': 'background: #F3F4F6;',
    'background: rgba(255, 255, 255, 0.1);': 'background: #E5E7EB;',
    'background: rgba(255, 255, 255, 0.02);': 'background: #FFFFFF;',
    'background: rgba(255, 255, 255, 0.03);': 'background: #FFFFFF;',
    'background: rgba(255, 255, 255, 0.2);': 'background: #E5E7EB;',
    'color: #fff;': 'color: var(--text-primary);',
    'border: 1px solid rgba(255,255,255,0.1);': 'border: 1px solid var(--border-color);'
}

html_replacements = {
    'color:white': 'color:var(--text-primary)',
    'color: white': 'color: var(--text-primary)',
    'color:#fff': 'color:var(--text-primary)',
    'background:rgba(15,23,42,0.95)': 'background:#FFFFFF',
    'background:rgba(15,23,42,.8)': 'background:#FFFFFF',
    'background:rgba(15,23,42,.7)': 'background:#FFFFFF',
    'background:rgba(0,0,0,.2)': 'background:#FFFFFF',
    'background:rgba(0,0,0,.6)': 'background:rgba(0,0,0,.2)',
    'background:rgba(255,255,255,.05)': 'background:#F3F4F6',
    'class="mesh-background"': 'class="mesh-background" style="display:none;"',
    'color:var(--text-secondary)': 'color:var(--text-secondary)' # No change, but maybe keep this to allow some contrast
}

def process_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    # Regex for inline colors
    content = re.sub(r'color:\s*white;?', 'color:var(--text-primary);', content)
    content = re.sub(r'color:\s*#fff;?', 'color:var(--text-primary);', content)
    content = re.sub(r'background:\s*rgba\(15,\s*23,\s*42,\s*[^)]+\);?', 'background:#FFFFFF;', content)
    content = re.sub(r'background:\s*rgba\(30,\s*41,\s*59,\s*[^)]+\);?', 'background:#FFFFFF;', content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, _, files in os.walk(directory):
    for file in files:
        if file == 'styles.css':
            process_file(os.path.join(root, file), css_replacements)
        elif file.endswith('.html'):
            process_file(os.path.join(root, file), html_replacements)

print("Theme conversion complete.")
