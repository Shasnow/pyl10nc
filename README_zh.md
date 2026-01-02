# pyl10nc

一个用于将TOML、JSON和YAML本地化文件转换为Python类的库，以便轻松访问本地化字符串。

中文 | [**English**](README.md)

## 项目背景

考虑一下Python中传统的国际化方法：

```python
import gettext

# 创建翻译实例
t = gettext.translation('myapplication', '/path/to/my/language/directory')
_ = t.gettext

# 使用翻译函数
print(_('This is a translatable string.'))
```

这种方法有几个痛点：

1. **繁琐的字符串输入**：使用翻译内容时，你必须逐个字符地输入每个字符串——包括引号和括号。有时你甚至不确定这些翻译是否存在于资源文件中。

2. **未使用的翻译**：资源文件可能包含代码中从未实际使用的翻译资源！

3. **复杂的文件管理**：在`en-us.json`和`zh-cn.json`文件之间跳转，或准备`xxx.mo`文件真的很麻烦！

这就是`pyl10nc`的用武之地。它将用TOML、JSON或YAML格式表示的语言翻译资源文件转换为Python代码！

现在你可以使用`localization`并通过`.`访问属性来在各种IDE中获取自动补全。不再需要输入整个字符串——也许当你输入`This`时，你的IDE已经为你完成了输入。我喜欢自动补全！此外，你可以通过检查使用情况来识别未使用的翻译，以便轻松清理它们。

## 功能特性

- 将TOML、JSON和YAML本地化文件转换为Python类
- 支持所有格式的嵌套和扁平结构
- 生成基于属性的访问方法
- 自动方法名清理
- 通过PyYAML提供可选的YAML支持

## 安装

```bash
# 基本安装（TOML和JSON支持）
pip install pyl10nc

# 包含YAML支持
pip install pyl10nc[yaml]
```

## 使用方法

### 命令行

```bash
# TOML文件
pyl10nc input.toml -o output.py

# JSON文件
pyl10nc input.json -o output.py

# YAML文件（需要PyYAML）
pyl10nc input.yaml -o output.py
```

### Python API

```python
import pyl10nc

# TOML文件
pyl10nc.generate('input.toml', 'output.py')

# JSON文件
pyl10nc.generate('input.json', 'output.py')

# YAML文件（需要PyYAML）
pyl10nc.generate('input.yaml', 'output.py')
```

## 支持的格式

### TOML格式示例

```toml
# filename.toml
[test.hello]
zh-cn = "你好"
en-us = "Hello"

[test.hello_doc]
doc = "使用'doc'指定属性的文档。"
zh-cn = "这是一个测试"
en-us = "This is a test"

[test.goodbye]
zh-cn = "再见"
en-us = "Goodbye"
```

### JSON格式示例

#### 嵌套结构
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

#### 扁平结构
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

### YAML格式示例

#### 嵌套结构
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

#### 扁平结构
```yaml
# filename_flat.yaml
test.hello:
  zh-cn: "你好"
  en-us: "Hello"
test.goodbye:
  zh-cn: "再见"
  en-us: "Goodbye"
```

## 生成的Python代码示例

### 生成的代码
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

### 用例
```python
from filename import localization

localization.lang = "en-us"  # 设置所需的语言环境
print(localization.test_hello)
# 输出: "Hello"

# 切换到中文
localization.lang = "zh-cn"
print(localization.test_hello)
# 输出: "你好"
```

## 许可证

MIT许可证