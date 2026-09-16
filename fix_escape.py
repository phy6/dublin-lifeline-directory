with open('.scratch/wayfinder-map/research/prototype-ui.html', 'r') as f:
    content = f.read()

# The problematic line has: "'": ''' 
# This is invalid JS. Need to fix to proper HTML entity
old = 'const map = { \'&\': \'&\', \'<\': \'<\', \'>\': \'>\', \'"\': \'"\', "\'": \'\'\' };'
new = 'const map = { \'&\': \'&\', \'<\': \'<\', \'>\': \'>\', \'"\': \'"\', "\'": "&apos;" };'

if old in content:
    content = content.replace(old, new)
    with open('.scratch/wayfinder-map/research/prototype-ui.html', 'w') as f:
        f.write(content)
    print('Fixed!')
else:
    print('Pattern not found')
    # Debug: show the actual line
    for i, line in enumerate(content.split('\n'), 1):
        if 'const map' in line:
            print('Line {}: {}'.format(i, repr(line)))