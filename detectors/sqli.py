import re
import yaml
import os

def load_rules():
    """Load SQL injection detection rules from YAML file."""
    rules_path = os.path.join(os.path.dirname(__file__), 'rules.yaml')
    try:
        with open(rules_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Fallback rules if file doesn't exist
        return {
            'rules': [
                {
                    'name': 'union_select',
                    'pattern': r'\\bunion\\b\\s+\\bselect\\b',
                    'description': 'UNION SELECT injection attempt'
                },
                {
                    'name': 'or_condition',
                    'pattern': r"'\\s*or\\s+\\d+\\s*=\\s*\\d+",
                    'description': 'OR condition injection attempt'
                },
                {
                    'name': 'comment_injection',
                    'pattern': r"--|\\#|/\\*",
                    'description': 'SQL comment injection attempt'
                },
                {
                    'name': 'drop_table',
                    'pattern': r'\\bdrop\\b\\s+\\btable\\b',
                    'description': 'DROP TABLE injection attempt'
                }
            ]
        }

def normalize_input(text):
    """Normalize input for consistent pattern matching."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.lower().strip())

def is_malicious(*inputs):
    """Check if any input contains SQL injection patterns."""
    rules_data = load_rules()
    
    for input_text in inputs:
        if not input_text:
            continue
            
        normalized = normalize_input(input_text)
        
        for rule in rules_data.get('rules', []):
            pattern = rule['pattern']
            if re.search(pattern, normalized, re.IGNORECASE):
                return {
                    'rule': rule['name'],
                    'description': rule['description'],
                    'pattern': pattern,
                    'snippet': input_text[:100]  # First 100 chars
                }
    
    return None