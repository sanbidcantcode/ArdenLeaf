import os
import ast
import re

def generate_tree(startpath, exclude_dirs):
    tree_lines = []
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree_lines.append(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree_lines.append(f'{subindent}{f}')
    return '\n'.join(tree_lines)

def analyze_flask_app(root_dir):
    blueprints = []
    routes = []
    templates = []
    navbar_links = []
    
    # Exclude logic
    exclude = {'__pycache__', '.git', 'venv', 'env', 'node_modules'}
    
    for subdir, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude]
        
        for file in files:
            filepath = os.path.join(subdir, file)
            if file.endswith('.py'):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Find Blueprint definitions
                    bp_matches = re.finditer(r"(\w+)\s*=\s*Blueprint\(\s*['\"]([^'\"]+)['\"]\s*,\s*__name__", content)
                    bps_in_file = {}
                    for m in bp_matches:
                        bp_var = m.group(1)
                        bp_name = m.group(2)
                        blueprints.append({'file': os.path.relpath(filepath, root_dir), 'name': bp_name, 'var': bp_var})
                        bps_in_file[bp_var] = bp_name
                        
                    # Find Blueprint registrations in app.py to get prefix
                    if 'app.py' in file or 'main.py' in file:
                        reg_matches = re.finditer(r"app\.register_blueprint\(([^,]+)(?:\s*,\s*url_prefix\s*=\s*['\"]([^'\"]+)['\"])?\)", content)
                        for m in reg_matches:
                            bp_ref_name = m.group(1).split('.')[-1]
                            prefix = m.group(2) if m.group(2) else '/'
                            for bp in blueprints:
                                if bp['name'] == bp_ref_name or bp['var'] == bp_ref_name:
                                    bp['prefix'] = prefix
                                    break
                    
                    # Find routes using regex
                    route_matches = re.finditer(r'@(\w+)\.(route|get|post)\([\'"]([^\'"]+)[\'"](?:[^)]*methods\s*=\s*\[([^\]]+)\])?', content)
                    
                    # Instead of precise AST matching, try to find the def function immediately after the decorator
                    # Split by @ route decorator and check next function definition
                    parts = re.split(r'@\w+\.(?:route|get|post)\([^\)]+\)', content)
                    matches_list = list(route_matches)
                    
                    for i, m in enumerate(matches_list):
                        decorator_var = m.group(1) # app or bp_var
                        url = m.group(3)
                        methods = m.group(4)
                        if not methods:
                            if m.group(2) == 'get': methods = "['GET']"
                            elif m.group(2) == 'post': methods = "['POST']"
                            else: methods = "['GET']"
                        else:
                            methods = methods.replace("'", "").replace('"', '').replace(" ", "")
                            
                        # Find the next 'def ' in the remaining text
                        func_match = re.search(r'def\s+(\w+)\s*\(', parts[i+1])
                        func_name = func_match.group(1) if func_match else "unknown"
                        
                        # Check if render_template is called
                        render_match = re.search(r'render_template\s*\(\s*[\'"]([^\'"]+)[\'"]', parts[i+1])
                        template = render_match.group(1) if render_match else "None"
                        
                        routes.append({
                            'url': url,
                            'methods': methods,
                            'function': func_name,
                            'template': template,
                            'file': os.path.relpath(filepath, root_dir)
                        })
                        
                except Exception as e:
                    pass
                    
            elif 'templates' in subdir.split(os.sep) and file.endswith('.html'):
                templates.append(os.path.relpath(filepath, root_dir))
                
                # Check for navbar links
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        in_nav = False
                        for line in lines:
                            if '<nav' in line or 'navbar' in line.lower():
                                in_nav = True
                            if '</nav>' in line:
                                in_nav = False
                                
                            if in_nav and 'href=' in line:
                                href_match = re.search(r'href=[\'"]([^\'"]+)[\'"]', line)
                                if href_match:
                                    link = href_match.group(1)
                                    text_match = re.search(r'>([^<]+)</a>', line)
                                    text = text_match.group(1).strip() if text_match else "icon/unknown"
                                    if link != '#' and text:
                                        navbar_links.append((os.path.basename(filepath), text, link))
                except:
                    pass

    return blueprints, routes, templates, navbar_links

def main():
    root_dir = r"d:\Projects of Coding\Database Project\ArdenLeaf"
    
    with open("project_report.txt", "w", encoding='utf-8') as out:
        out.write("================ PROJECT REPORT ================\n\n")
        
        blueprints, routes, templates, nav_links = analyze_flask_app(root_dir)
        
        out.write("### 1. ROUTES\n")
        for r in sorted(routes, key=lambda x: x['url']):
            out.write(f"- HTTP Method(s): {r['methods']}\n")
            out.write(f"  URL Rule: {r['url']}\n")
            out.write(f"  Function Name: {r['function']} (in {r['file']})\n")
            out.write(f"  Renders Template: {r['template']}\n\n")
            
        out.write("### 2. TEMPLATES\n")
        for t in sorted(templates):
            out.write(f"- {t}\n")
        out.write("\n")
        
        out.write("### 3. BLUEPRINTS\n")
        for bp in blueprints:
            prefix = bp.get('prefix', 'Not registered/Unknown')
            out.write(f"- Name: {bp['name']}\n")
            out.write(f"  Prefix: {prefix}\n")
            out.write(f"  File: {bp['file']}\n\n")
            
        out.write("### 4. NAVBAR LINKS\n")
        seen = set()
        for file, text, link in nav_links:
            if (file, link) not in seen:
                out.write(f"- {file}: '{text}' pointing to -> {link}\n")
                seen.add((file, link))
        out.write("\n")
        
        out.write("### 5. FILE STRUCTURE\n")
        tree_str = generate_tree(root_dir, ['__pycache__', '.git', 'venv', 'env', 'node_modules'])
        out.write(tree_str)
        out.write("\n")

if __name__ == '__main__':
    main()
