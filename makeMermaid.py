import json
import os

def load_table_of_contents(file_path):
    """Load the table of contents JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_mermaid_diagram(data):
    """Generate a Mermaid diagram from the table of contents data."""
    mermaid_lines = ["graph TD"]
    
    # Add project node
    project_id = "Project"
    project_desc = data.get('project', 'NexusMind Project')
    mermaid_lines.append(f"    {project_id}[\"{project_desc}\"]")
    
    # Add file nodes and connections
    for file_path, file_info in data.get('files', {}).items():
        file_id = file_path.replace('/', '_').replace('.', '_').replace('-', '_')
        file_desc = file_info.get('description', file_path)
        mermaid_lines.append(f"    {file_id}[\"{file_path}\"]")
        mermaid_lines.append(f"    {project_id} --> {file_id}")
        
        # Add function nodes for each file
        for func_name, func_info in file_info.get('functions', {}).items():
            if func_name != 'none':
                func_id = f"{file_id}_{func_name}".replace('-', '_')
                func_desc = func_info.get('purpose', func_name)
                mermaid_lines.append(f"    {func_id}[\"{func_name}\"]")
                mermaid_lines.append(f"    {file_id} --> {func_id}")
                
                # Add dependencies if available
                for dep in func_info.get('dependencies', []):
                    dep_id = dep.replace('/', '_').replace('.', '_').replace('-', '_').replace(' ', '_')
                    mermaid_lines.append(f"    {func_id} -.-> {dep_id}[\"{dep}\"]")
    
    # Add dependency nodes
    for dep_type, deps in data.get('dependencies', {}).items():
        for dep in deps:
            dep_id = dep.replace('/', '_').replace('.', '_').replace('-', '_').replace(' ', '_')
            mermaid_lines.append(f"    {dep_id}[\"{dep}\"]")
            mermaid_lines.append(f"    {project_id} -.-> {dep_id}")
    
    return '\n'.join(mermaid_lines)

def save_mermaid_file(content, output_file):
    """Save the Mermaid diagram content to a file."""
    with open(output_file, 'w') as f:
        f.write(content)

def main():
    input_file = 'table_of_contents.json'
    output_file = 'codebase_structure.mmd'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return
    
    data = load_table_of_contents(input_file)
    mermaid_content = generate_mermaid_diagram(data)
    save_mermaid_file(mermaid_content, output_file)
    print(f"Mermaid diagram generated successfully as {output_file}")

if __name__ == '__main__':
    main() 