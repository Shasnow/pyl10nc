# pyl10nc

A Python library to convert TOML, JSON, and YAML localization files into Python classes for easy access to localized strings.

[**中文文档**](README_zh.md) | English

## Background

Consider the traditional approach to internationalization in Python:

```python
import gettext

# Create translation instance
t = gettext.translation('myapplication', '/path/to/my/language/directory')
_ = t.gettext

# Use translation function
print(_('This is a translatable string.'))
```

There are several pain points with this approach:

1. **Tedious string typing**: When using translation content, you have to type out each string character by character—including quotes and parentheses. Sometimes you're not even sure if these translations exist in the resource files.

2. **Unused translations**: Resource files may contain translation resources that are never actually used in the code!

3. **Complex file management**: Jumping between `en-us.json` and `zh-cn.json` files or preparing `xxx.mo` files is genuinely cumbersome!

That's where `pyl10nc` comes in. It converts language translation resource files represented in TOML, JSON, or YAML format into Python code!

Now you can use `localization` and access properties with `.` to get auto-completion in various IDEs. No more typing entire strings—perhaps when you type `This`, your IDE has already completed the input for you. I love auto-completion! Additionally, you can identify unused translations by checking usage, making it easy to clean them up.

## Features

- Convert TOML, JSON, and YAML localization files to Python classes
- Support nested and flat structures for all formats
- Generate property-based access methods
- Automatic method name sanitization
- Optional YAML support via PyYAML

## Installation

```bash
# Basic installation (TOML and JSON support)
pip install pyl10nc

# With YAML support
pip install pyl10nc[yaml]
```

## Usage

### Command Line

```bash
# TOML file
pyl10nc input.toml -o output.py

# JSON file
pyl10nc input.json -o output.py

# YAML file (requires PyYAML)
pyl10nc input.yaml -o output.py
```

### Python API

```python
import pyl10nc

# TOML file
pyl10nc.generate('input.toml', 'output.py')

# JSON file
pyl10nc.generate('input.json', 'output.py')

# YAML file (requires PyYAML)
pyl10nc.generate('input.yaml', 'output.py')
```

## Supported Formats

### TOML Format Example

```toml
# filename.toml
[test.hello]
zh-cn = "你好"
en-us = "Hello"

[test.hello_doc]
doc = "Use 'doc' to specify the documentation for the property."
zh-cn = "这是一个测试"
en-us = "This is a test"

[test.goodbye]
zh-cn = "再见"
en-us = "Goodbye"
```

### JSON Format Example

#### Nested Structure
```json
{
  "test": {
    "hello": {
      "zh-cn": "你好",
      "en-us": "Hello"
    },
    "goodbye": {
      "zh-cn": "再见",
      "en-us": "Goodbye"
    }
  }
}
```

#### Flat Structure
```json
{
  "test.hello": {
    "zh-cn": "你好",
    "en-us": "Hello"
  },
  "test.goodbye": {
    "zh-cn": "再见",
    "en-us": "Goodbye"
  }
}
```

### YAML Format Example

#### Nested Structure
```yaml
# filename.yaml
test:
  hello:
    zh-cn: "你好"
    en-us: "Hello"
  goodbye:
    zh-cn: "再见"
    en-us: "Goodbye"
```

#### Flat Structure
```yaml
# filename_flat.yaml
test.hello:
  zh-cn: "你好"
  en-us: "Hello"
test.goodbye:
  zh-cn: "再见"
  en-us: "Goodbye"
```

## Generated Python Code Example

### Generated code
```python
# filename.py
import json

class Localization:
    """Automatically generated localization class."""
    __normalized_data: dict[str, dict[str, str]] = None
    lang: str = "zh-cn"

    def __init__(self):
        """Initialize localization data."""
        with open('filename.json', 'r', encoding='utf-8') as f:
            self.__normalized_data = json.load(f)
    def _get_translation(self, key: str) -> str:
        """
        Get the translation value for the specified key.
        :param key: Flattened translation key (e.g., test.group1.hello)
        :return: Translation value for the target language, or key if not found
        """
        resource = self.__normalized_data.get(key, {})
        return resource.get(self.lang, key)

    @property
    def test_hello(self) -> str:
        """你好"""
        return self._get_translation("test.hello")

    @property
    def test_group1_welcome(self) -> str:
        """欢迎"""
        return self._get_translation("test.group1.welcome")

    @property
    def test_group1_farewell(self) -> str:
        """再见"""
        return self._get_translation("test.group1.farewell")

    @property
    def test_group2_question(self) -> str:
        """你好吗？"""
        return self._get_translation("test.group2.question")

    @property
    def test_group2_response(self) -> str:
        """The response to the question 'How are you?'"""
        return self._get_translation("test.group2.response")

localization = Localization()
```

### Usage
```python
from filename import localization

localization.lang = "en-us"  # Set desired locale
print(localization.test_hello)
# Output: "Hello"

# Switch to Chinese
localization.lang = "zh-cn"
print(localization.test_hello)
# Output: "你好"
```

## License

MIT License
