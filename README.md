# pyl10nc

A Python library to convert TOML localization files into Python classes for easy access to localized strings.

## Features

- Convert TOML localization files to Python classes
- Support nested TOML structures
- Generate property-based access methods
- Automatic method name sanitization
- Multi-language support

## Installation

```bash
pip install pyl10nc
```

## Usage

### Command Line

```bash
pyl10nc input.toml -o output.py
```

### Python API

```python
from pyl10nc import generate

generate('input.toml', 'output.py')
```

## TOML Format Example

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

## Generated Python Code Example
```python
from filename import localization

localization.local = "en-us"  # Set desired locale if needed
print(localization.test.hello)
# Output: "Hello"
```

## Plan
- [ ] JSON format support
- [ ] YAML format support

## License

MIT License
