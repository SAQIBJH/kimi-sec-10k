#!/usr/bin/env python3
"""
Convert Figma CSS export to valid CSS.
Figma exports CSS properties without selectors - this script converts them to proper CSS classes.
"""

import re

def convert_figma_css(input_file, output_file):
    """Convert Figma CSS to valid CSS with proper selectors."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by comment blocks that start with /* and contain Frame, Data Row, etc.
    lines = content.split('\n')
    
    valid_css = []
    current_class = None
    current_properties = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is a main comment (class name)
        if line.startswith('/*') and line.endswith('*/'):
            comment_text = line[2:-2].strip()
            
            # If we have accumulated properties, write them out
            if current_class and current_properties:
                valid_css.append(f'.{current_class} {{')
                valid_css.extend(['  ' + prop for prop in current_properties])
                valid_css.append('}')
                valid_css.append('')
                current_properties = []
            
            # Check if this is a section header (Frame, Data Row, etc.)
            # These become class names
            if any(keyword in comment_text for keyword in ['Frame', 'Data Row', 'Bold Data Row', 'Stroke', 'Arrow', 'Line']):
                # Create a valid CSS class name
                class_name = comment_text.replace(' ', '-').replace('/', '-').replace('.', '-').replace(',', '').replace('(', '').replace(')', '')
                class_name = re.sub(r'[^a-zA-Z0-9_-]', '', class_name)
                current_class = class_name
                valid_css.append(f'/* {comment_text} */')
            else:
                # This is a descriptive comment, keep it
                if current_properties:
                    current_properties.append(f'/* {comment_text} */')
        
        # Check if line is a CSS property
        elif ':' in line and line.endswith(';'):
            if current_class:
                current_properties.append(line)
        
        # Check for standalone properties without semicolon (some Figma exports)
        elif line and not line.startswith('/*') and not line.startswith('//'):
            # Skip empty lines
            if line.strip():
                # This might be a property
                if current_class and ':' in line:
                    # Add semicolon if missing
                    prop = line if line.endswith(';') else line + ';'
                    current_properties.append(prop)
        
        i += 1
    
    # Don't forget the last class
    if current_class and current_properties:
        valid_css.append(f'.{current_class} {{')
        valid_css.extend(['  ' + prop for prop in current_properties])
        valid_css.append('}')
        valid_css.append('')
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(valid_css))
    
    return len([line for line in valid_css if line.startswith('.')])

if __name__ == '__main__':
    input_file = '/Users/mohdsaeedafri/Documents/Documents/Code-Base/kimi-sec-10k-1/wireframes/table.css'
    output_file = '/Users/mohdsaeedafri/Documents/Documents/Code-Base/kimi-sec-10k-1/wireframes/table_fixed.css'
    
    num_classes = convert_figma_css(input_file, output_file)
    print(f"✅ Conversion complete!")
    print(f"📝 Created {num_classes} CSS classes")
    print(f"💾 Output saved to: {output_file}")
