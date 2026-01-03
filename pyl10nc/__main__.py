import argparse
import os
import tomllib
import re
import json
from pathlib import Path

# Try to import YAML for optional YAML support
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def is_already_flat(data: dict) -> bool:
    """
    Check if the data is already in flattened format.
    :param data: Data to check.
    :return: True if data is already flattened, False otherwise.
    """
    if not data:
        return False

    # Check if all keys are strings (potentially flattened keys)
    # and all values are dictionaries with language keys
    for key, value in data.items():
        if not isinstance(key, str):
            return False
        if not isinstance(value, dict):
            return False
        # Check if value dict contains language-like keys (e.g., zh-cn, en-us, doc)
        # AND doesn't contain nested dictionaries
        has_language_keys = any(
            isinstance(k, str) and (k == 'doc' or '-' in k or k.isalpha())
            for k in value.keys()
        )
        has_nested_dicts = any(
            isinstance(v, dict) for v in value.values()
        )
        if not has_language_keys or has_nested_dicts:
            return False

    return True


def normalize_data(data: dict) -> dict[str, dict[str, str]]:
    """
    Recursively normalize nested TOML data into a flat dictionary.
    :param data: Nested TOML data.
    :return: Flattened dictionary with language keys.
    """
    # Check if data is already flattened
    if is_already_flat(data):
        return {k: v for k, v in data.items() if k.strip()}

    result = {}

    def normalize_dict(d: dict, current_path: list[str]):
        for k, v in d.items():
            new_path = current_path + [k]
            if isinstance(v, dict):
                normalize_dict(v, new_path)
            else:
                flat_key = '.'.join(current_path)
                if flat_key not in result:
                    result[flat_key] = {}
                result[flat_key][k] = str(v) if v is not None else ""

    normalize_dict(data, [])
    return {k: v for k, v in result.items() if k.strip()}


def sanitize_method_name(name: str) -> str:
    """
    Clean up method names to ensure they follow Python identifier rules.
    - Replace non-alphanumeric/underscore characters with _.
    - Prefix with _ if it starts with a number.
    """
    # Replace . with _, then clean other invalid characters
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.replace('.', '_'))
    # Add prefix _ if starts with number
    if re.match(r'^\d', sanitized):
        sanitized = f"_{sanitized}"
    return sanitized


def escape_doc_string(text) -> str:
    """
    Escape special characters in doc strings.
    - Escape double quotes.
    - Handle newlines as \n.
    """
    if not text or not isinstance(text, str):
        return ""
    # Escape double quotes, replace newlines with \n
    return text.replace('"', '\\"').replace('\n', '\\n')


def extract_interpolation_variables(text: str) -> list[str]:
    """
    Extract variable names from a string with interpolation placeholders.
    :param text: String that may contain interpolation placeholders like {name}
    :return: List of variable names found in the string
    """
    if not text or not isinstance(text, str):
        return []
    
    # Find all {variable} patterns
    pattern = r'\{([^}]+)\}'
    matches = re.findall(pattern, text)
    return matches


def has_interpolation(text: str) -> bool:
    """
    Check if a string contains interpolation placeholders.
    :param text: String to check
    :return: True if the string contains interpolation placeholders
    """
    if not text or not isinstance(text, str):
        return False
    return bool(re.search(r'\{[^}]+\}', text))


def generate(input_path: str | Path, output_path: str | None = None) -> str:
    """
    Generate localization Python class code from a TOML, JSON, or YAML file.
    :param input_path: Path to the input TOML, JSON, or YAML file.
    :param output_path: Path to the output Python file (default: same as input, suffix changed to .py).
    :return: Generated code as a string.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() not in ['.toml', '.json', '.yaml', '.yml']:
        raise ValueError(f"Input file must be a TOML, JSON, or YAML file, current suffix: {input_path.suffix}")

    if not output_path:
        output_py = input_path.with_suffix('.py')
    else:
        output_py = Path(output_path).resolve()
    output_json = output_py.with_suffix('.json')
    cwd_output_json = str(output_json.relative_to(os.getcwd())).replace('\\', '/')

    try:
        if input_path.suffix.lower() == '.toml':
            with open(input_path, 'rb') as f:
                raw_data = tomllib.load(f)
        elif input_path.suffix.lower() == '.json':
            with open(input_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        elif input_path.suffix.lower() in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                raise ImportError("YAML support requires PyYAML. Install with: pip install pyl10nc[yaml]")
            with open(input_path, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f) # type: ignore
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Failed to parse TOML file: {e}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON file: {e}") from e
    except yaml.YAMLError as e: # type: ignore
        raise ValueError(f"Failed to parse YAML file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error reading input file: {e}") from e

    translation_data = normalize_data(raw_data) # type: ignore
    if not translation_data:
        raise ValueError("No valid translation data found in input file")

    if input_path.suffix.lower() == '.toml':
        file_type = "TOML"
    elif input_path.suffix.lower() == '.json':
        file_type = "JSON"
    else:
        file_type = "YAML"
    code_lines = [
        '# -*- coding: utf-8 -*-',
        '################################################################################',
        f'## Form generated from reading {file_type} file \'{input_path.name}\'',
        '##',
        '## Created by: pyl10nc',
        '##',
        '## WARNING! All changes made in this file will be lost when regenerate!',
        '################################################################################',
        '',
        'import json',
        '',
        '',
        'class Localization:',
        '    """Automatically generated localization class."""',
        '    __normalized_data: dict[str, dict[str, str]] = None',
        '    lang: str = "zh-cn"',
        '',
        '    def __init__(self):',
        '        """Initialize localization data."""',
        f"        with open('{cwd_output_json}', 'r', encoding='utf-8') as f:",
        '            self.__normalized_data = json.load(f)',
        '',
        '    def _get_translation(self, key: str) -> str:',
        '        """',
        '        Get the translation value for the specified key.',
        '        :param key: Flattened translation key (e.g., test.group1.hello)',
        '        :return: Translation value for the target language, or key if not found',
        '        """',
        '        resource = self.__normalized_data.get(key, {})',
        '        return resource.get(self.lang, key)',
        '',
    ]

    # generate property methods
    for flat_key, lang_dict in translation_data.items():
        method_name = sanitize_method_name(flat_key)
        # get doc string
        doc = lang_dict.get('doc', '')
        if not doc:
            # filter doc, take the first non-doc value
            lang_values = [v for k, v in lang_dict.items() if k != 'doc']
            doc = lang_values[0] if lang_values else flat_key
        # escape doc string
        escaped_doc = escape_doc_string(doc)
        
        # Check if any language value has interpolation
        has_interp = any(has_interpolation(v) for k, v in lang_dict.items() if k != 'doc')
        
        if has_interp:
            # Extract variables from the first language value that has interpolation
            interp_vars = []
            for k, v in lang_dict.items():
                if k != 'doc' and has_interpolation(v):
                    interp_vars = extract_interpolation_variables(v)
                    break
            
            # Create method with parameters
            params = ', '.join(interp_vars)
            # Create keyword arguments for format
            kwargs = ', '.join([f'{var}={var}' for var in interp_vars])
            code_lines.extend([
                f'    def {method_name}(self, {params}) -> str:',
                f'        """{escaped_doc}"""',
                f'        template = self._get_translation("{flat_key}")',
                f'        return template.format({kwargs})',
                ''
            ])
        else:
            # add property method
            code_lines.extend([
                f'    @property',
                f'    def {method_name}(self) -> str:',
                f'        """{escaped_doc}"""',
                f'        return self._get_translation("{flat_key}")',
                ''
            ])

    # add global instance
    code_lines.extend([
        'localization = Localization()',
        ''
    ])
    code = '\n'.join(code_lines)
    try:
        output_py.parent.mkdir(parents=True, exist_ok=True)
        with open(output_py, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"✅ Code generated successfully! File saved to: {output_py}")
        # also save JSON file
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(translation_data, f, ensure_ascii=False, indent=4)
        print(f"✅ JSON file generated successfully! File saved to: {output_json}")
    except Exception as e:
        raise RuntimeError(f"Failed to write output file: {e}") from e

    return code


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description='Generate localization code from TOML, JSON, or YAML file.')
    parser.add_argument('input', type=str, help='Path to the input TOML, JSON, or YAML file.')
    parser.add_argument('--output', '-o', type=str, nargs='?', default=None,
                        help='Path to the output Python file (default: same as input with .py suffix).')

    args = parser.parse_args()

    try:
        generate(args.input, args.output)
    except Exception as e:
        print(f"❌ Code generation failed: {e}")
        exit(1)


if __name__ == '__main__':
    main()
