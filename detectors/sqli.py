import re
import yaml
import os

def load_rules():
    """Load SQL injection detection rules from YAML file with fallback."""
    rules_path = os.path.join(os.path.dirname(__file__), 'rules.yaml')
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Warning: Could not load rules.yaml ({e}), using fallback rules")
        # Comprehensive fallback rules if YAML fails
        return {
            'rules': [
                {
                    'name': 'union_select',
                    'pattern': r'(?i)\bunion\b\s+\bselect\b',
                    'description': 'UNION SELECT injection attempt'
                },
                {
                    'name': 'or_condition',
                    'pattern': r"(?i)'\s*or\s+\d+\s*=\s*\d+",
                    'description': 'OR condition injection attempt'
                },
                {
                    'name': 'comment_injection',
                    'pattern': r'(?i)--|#|/\*',
                    'description': 'SQL comment injection attempt'
                },
                {
                    'name': 'drop_table',
                    'pattern': r'(?i)\bdrop\b\s+\btable\b',
                    'description': 'DROP TABLE injection attempt'
                },
                {
                    'name': 'insert_injection',
                    'pattern': r'(?i)\binsert\b\s+\binto\b',
                    'description': 'INSERT injection attempt'
                },
                {
                    'name': 'delete_injection',
                    'pattern': r'(?i)\bdelete\b\s+\bfrom\b',
                    'description': 'DELETE injection attempt'
                },
                {
                    'name': 'update_injection',
                    'pattern': r'(?i)\bupdate\b\s+\w+\s+\bset\b',
                    'description': 'UPDATE injection attempt'
                },
                {
                    'name': 'always_true',
                    'pattern': r"(?i)'\s*or\s+'1'\s*=\s*'1",
                    'description': 'Always true condition injection'
                },
                {
                    'name': 'or_true_bypass',
                    'pattern': r"(?i)'\s*or\s+'.*'\s*=\s*'.*'",
                    'description': 'OR true bypass attempt'
                },
                {
                    'name': 'sleep_function',
                    'pattern': r'(?i)\bsleep\s*\(',
                    'description': 'SLEEP function time-based injection'
                },
                {
                    'name': 'waitfor_delay',
                    'pattern': r'(?i)\bwaitfor\s+delay\b',
                    'description': 'WAITFOR DELAY time-based injection'
                },
                {
                    'name': 'information_schema',
                    'pattern': r'(?i)\binformation_schema\b',
                    'description': 'Information schema access attempt'
                },
                {
                    'name': 'version_function',
                    'pattern': r'(?i)@@version|\bversion\s*\(',
                    'description': 'Database version disclosure attempt'
                },
                {
                    'name': 'user_function',
                    'pattern': r'(?i)@@user|\buser\s*\(',
                    'description': 'Database user disclosure attempt'
                },
                {
                    'name': 'hex_encoding',
                    'pattern': r'(?i)0x[0-9a-fA-F]+',
                    'description': 'Hexadecimal encoding injection'
                }
            ]
        }

def normalize_input(text):
    """Normalize input for consistent pattern matching."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())

def is_malicious(*inputs):
    """Check if any input contains SQL injection patterns."""
    try:
        rules_data = load_rules()
        
        for input_text in inputs:
            if not input_text:
                continue
                
            # Keep original case for pattern matching
            original_text = str(input_text)
            normalized = normalize_input(original_text)
            
            for rule in rules_data.get('rules', []):
                pattern = rule['pattern']
                try:
                    # Use re.search with the pattern (case-insensitive flag is in pattern)
                    if re.search(pattern, normalized) or re.search(pattern, original_text):
                        return {
                            'rule': rule['name'],
                            'description': rule['description'],
                            'pattern': pattern,
                            'snippet': original_text[:100]  # First 100 chars
                        }
                except re.error as e:
                    print(f"Regex error in rule {rule['name']}: {e}")
                    continue
        
        return None
        
    except Exception as e:
        print(f"Error in is_malicious: {e}")
        # Emergency fallback - basic pattern matching
        for input_text in inputs:
            if not input_text:
                continue
            text_lower = str(input_text).lower()
            if any(keyword in text_lower for keyword in ['union select', 'drop table', "' or '1'='1", '--', '/*']):
                return {
                    'rule': 'emergency_fallback',
                    'description': 'Basic SQL injection pattern detected',
                    'pattern': 'emergency_pattern',
                    'snippet': str(input_text)[:100]
                }
        return None