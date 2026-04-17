import os
import re

# Read base.html to extract the correct blocks
with open('templates/base.html', 'r', encoding='utf-8') as f:
    base_html = f.read()

# 1. Extract Profile Dropdown CSS
# Find "/* ── Profile Dropdown ── */" or similar.
# In base.html it is "/* ══════════════════════════════════════════════\n           PROFILE DROPDOWN\n        ══════════════════════════════════════════════ */"
css_start = base_html.find('/* ══════════════════════════════════════════════\n           PROFILE DROPDOWN')
css_end = base_html.find('/* ══════════════════════════════════════════════\n           TOAST SYSTEM')
profile_css = base_html[css_start:css_end].strip()

# 2. Extract Profile Dropdown HTML
# We can find `<div class="profile-menu-wrap" id="profileMenuWrap">`
html_start = base_html.find('<div class="profile-menu-wrap" id="profileMenuWrap">')
# To find the end, we count divs.
def get_balanced_block(text, start_idx):
    if start_idx == -1: return ""
    count = 0
    i = start_idx
    while i < len(text):
        if text.startswith('<div', i):
            count += 1
        elif text.startswith('</div', i):
            count -= 1
            if count == 0:
                end_idx = text.find('>', i) + 1
                return text[start_idx:end_idx]
        i += 1
    return ""

profile_html_full = get_balanced_block(base_html, html_start)
# Remove the exact block: <div class="dropdown-user-info">...</div>
dui_start = profile_html_full.find('<div class="dropdown-user-info">')
dui_end = profile_html_full.find('</div>', profile_html_full.find('</div>', dui_start) + 1) + 6 # Since it contains two child divs, the third </div> closes it
# Let's just use regex for this inner part since it's simple
profile_html = re.sub(r'<div class="dropdown-user-info">.*?</div>\s*</div>', '', profile_html_full, flags=re.DOTALL)
# Actually, the user-info element has two divs inside:
# <div class="dropdown-user-info">
#     <div class="dui-name">{{ session.get('user_name', '') }}</div>
#     <div class="dui-type">{{ session.get('user_type', 'User') }}</div>
# </div>
profile_html = re.sub(r'\s*<div class="dropdown-user-info">.*?</div\s*>\s*</div\s*>', '', profile_html_full, flags=re.DOTALL)


# 3. Extract Profile JS
js_start = base_html.find('// ── Profile dropdown ──────────────────────────────────────────────')
js_end = base_html.find('// ── Convert Flask flash messages', js_start)
profile_js = base_html[js_start:js_end].strip()

new_logo = """<a href="{{ url_for('index') }}" style="display:flex;align-items:center;gap:8px;text-decoration:none;">
                <span class="material-symbols-outlined" style="font-size:28px;color:#113819;font-variation-settings:'FILL' 1;">eco</span>
                <span style="font-family:'Outfit',sans-serif;font-weight:900;font-size:1.4rem;color:#113819;">ArdenLeaf</span>
            </a>"""

templates_to_update = ['index.html', 'book_detail.html', 'search.html', 'dashboard.html', 'profile.html', 'bookmarks.html', 'locations.html', 'libraries.html', 'auth.html', 'error.html']

for filename in templates_to_update:
    path = os.path.join('templates', filename)
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip files without a header/navbar
    if '<header' not in content and 'nav-link-standard' not in content:
        continue
        
    # Replace Logo
    # Look for the logo anchor tag usually within <header> or specific inline styles
    content = re.sub(r'<a href="\{\{\s*url_for\(\'index\'\)\s*\}\}"\s*style="display:flex;\s*align-items:center;\s*gap:8px;\s*text-decoration:none;">.*?</a>', new_logo, content, flags=re.DOTALL)
    content = re.sub(r'<a href="\{\{\s*url_for\(\'index\'\)\s*\}\}"\s*style="text-decoration:none;\s*display:flex;\s*align-items:center;\s*gap:8px;">.*?</a>', new_logo, content, flags=re.DOTALL)
    
    # Replace Profile HTML
    current_html_start = content.find('<div class="profile-menu-wrap"')
    if current_html_start != -1:
        current_html_full = get_balanced_block(content, current_html_start)
        if current_html_full:
            content = content.replace(current_html_full, profile_html)
            
    # Replace CSS (search for .profile-menu-wrap CSS rules)
    css_start_idx = content.find('/* ── Profile Dropdown ── */')
    if css_start_idx != -1:
        css_end_idx = content.find('</style>', css_start_idx)
        if css_end_idx != -1:
            current_css = content[css_start_idx:css_end_idx].strip()
            content = content.replace(current_css, profile_css)

    # Note: What if CSS is not commented with '/* ── Profile Dropdown ── */'?
    
    # Replace JS
    js_start_idx = content.find('(function() {\n            const wrap = document.getElementById(\'profileMenuWrap\');')
    if js_start_idx == -1:
        js_start_idx = content.find('// Profile dropdown toggle')
    
    if js_start_idx != -1:
        # Simple extraction for JS replacement. Find the ending `})();`
        js_end_idx = content.find('})();', js_start_idx)
        if js_end_idx != -1:
            current_js = content[js_start_idx:js_end_idx+5]
            content = content.replace(current_js, profile_js)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done updating templates.")
