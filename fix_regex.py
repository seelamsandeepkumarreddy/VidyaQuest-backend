filepath = r'c:\Users\sande\AndroidStudioProjects\ruralquest_backend\routes\admin.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Show what we're looking for
idx = content.find('String0-9')
if idx >= 0:
    print(f"Found 'String0-9' at position {idx}")
    print(f"Context: ...{content[idx-30:idx+40]}...")
    # Simple string replace
    content = content.replace('0-String0-9', '0-9')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed!")
else:
    print("Pattern 'String0-9' not found in file")
    # Try other encodings
    for enc in ['latin-1', 'cp1252', 'utf-8-sig']:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                content = f.read()
            idx = content.find('String0-9')
            if idx >= 0:
                print(f"Found with encoding {enc}")
                content = content.replace('0-String0-9', '0-9')
                with open(filepath, 'w', encoding=enc) as f:
                    f.write(content)
                print("Fixed!")
                break
        except:
            pass
