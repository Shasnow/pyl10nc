import os
import tomllib
import re
import json
from pathlib import Path


def normalize_data(data: dict) -> dict[str, dict[str, str]]:
    """
    Recursively normalize nested TOML data into a flat dictionary.
    :param data: Nested TOML data.
    :return: Flattened dictionary with language keys.
    """
    result = {}

    def normalize_dict(d: dict, current_path: list[str]):
        for k, v in d.items():
            # 拼接当前层级的路径
            new_path = current_path + [k]
            if isinstance(v, dict):
                # 递归处理嵌套字典
                normalize_dict(v, new_path)
            else:
                # 扁平键（如 test.group1.hello）
                flat_key = '.'.join(current_path)
                # 初始化扁平键的字典
                if flat_key not in result:
                    result[flat_key] = {}
                # 存储语言/文档值（确保值为字符串）
                result[flat_key][k] = str(v) if v is not None else ""

    normalize_dict(data, [])
    # 过滤空键（避免生成无意义的属性）
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


def escape_doc_string(text: str) -> str:
    """
    Escape special characters in doc strings.
    - Escape double quotes.
    - Handle newlines as \n.
    """
    if not text:
        return ""
    # Escape double quotes, replace newlines with \n
    return text.replace('"', '\\"').replace('\n', '\\n')


def generate(input_path: str, output_path: str = None) -> str:
    """
    Generate localization Python class code from a TOML file.
    :param input_path: Path to the input TOML file.
    :param output_path: Path to the output Python file (default: same as input, suffix changed to .py).
    :return: Generated code as a string.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() not in ['.toml']:
        raise ValueError(f"Input file must be a TOML file, current suffix: {input_path.suffix}")

    if not output_path:
        output_py = input_path.with_suffix('.py')
    else:
        output_py= Path(output_path).resolve()
    output_json = output_py.with_suffix('.json')

    try:
        with open(input_path, 'rb') as f:
            raw_data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Failed to parse TOML file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error reading TOML file: {e}") from e

    translation_data = normalize_data(raw_data)
    if not translation_data:
        raise ValueError("No valid translation data found in TOML file")

    code_lines = [
        '# -*- coding: utf-8 -*-',
        '################################################################################',
        f'## Form generated from reading TOML file \'{input_path.name}\'',
        '##',
        '## Created by: pyl10nc',
        '##',
        '## WARNING! All changes made in this file will be lost when regenerate!',
        '################################################################################',
        '',
        'import json',
        '',
        'class Localization:',
        '    """Automatically generated localization class."""',
        '    __normalized_data: dict[str, dict[str, str]] = None',
        '    lang: str = "zh-cn"',
        '',
        '    def __init__(self):',
        '        """Initialize localization data."""',
        f"        with open('{output_json.relative_to(os.getcwd())}', 'r', encoding='utf-8') as f:",
        '            self.__normalized_data = json.load(f)',
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

__all__ = ['generate']
