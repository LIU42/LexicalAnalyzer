# Lexical Analyzer

**《编译原理》课程设计，基于有穷自动机的类 C 语言词法分析器**

*<u>本项目配套的 [语法分析器](https://github.com/LIU42/SyntaxParser)</u>*

## 项目简介

本项目为一个基于有穷自动机的类 C 语言词法分析器，可以将一种类似 C 语言的源程序（不包含编译预处理指令）解析为以下五类 Token 构成的序列：

- 标识符（identifiers）
- 常量（constants）
- 关键字（keywords）
- 运算符（operators）
- 界符（bounds）

其中每一个 Token 为一个四元组，其格式为 *<所在行号，所在列号，所属类别，内容>*。

### 文法规则

本项目提供一个默认的文法规则，也可通过修改默认的文法配置文件（<u>configs/grammar.json</u>）实现自定义规则：

- 标识符仅能由字母、数字和下划线组成，且不能以数字开头。

- 常量包括整数（例如 123）、浮点数（例如 123.456）、字符（例如 'c'）、字符串（例如 "string"）、科学计数法表示的整数或浮点数（例如 2E5 和 1.23e-2）、复数（例如 1.5+3.8i）、布尔类型（true 和 false）。

- 仅支持十进制表示的数字。

- 关键字在 C 语言 32 个关键字的基础上添加 bool（表示布尔类型）和 complex（表示复数类型） 关键字。

- 运算符和界符与 C 语言保持一致。

## 实现方案

### 识别方案

针对标识符和常量的识别，采用有穷自动机实现。详细步骤如下：

1. 读取文法配置文件中定义的标识符和常量的正规文法（3 型文法）构造不确定的有穷自动机（NFA）。

2. 将不确定的有穷自动机采用子集法确定化为确定的有穷自动机（DFA）。

3. 对标识符和常量分别利用对应确定的有穷自动机进行识别。

针对运算符和界符，采用枚举的方法进行识别。识别过程中采用**贪心**的策略，即尽可能地向前搜索，在正确的前提下尽可能将更多的字符组合识别为单个运算符，也就是优先匹配更长的运算符。

针对关键字的识别，由于关键字可以视为特殊的标识符，因此关键字的识别在确定为标识符后对所有的关键字进行枚举比对实现。

### 分析处理流程

在读入字符的过程中，分析程序的处理流程如下：

1. 若当前没有正在运行的自动机且当前读入的字符可以作为某个自动机的初态，则分配该自动机进行识别。

2. 若仍然没有分配到自动机，说明当前读入的字符应为运算符、界符或是空白符号，则调用可枚举 Token 处理程序进行识别。

3. 若已经分配到自动机，则调用自动机处理程序，尝试进行状态转换：
   
   1. 若状态转换成功，则继续读入下一个字符。
   
   2. 转换不成功时，若位于终态则识别成功，转入进一步的判断，否则进入出错处理程序。

#### 流程伪代码描述

```c
while (指针未到达末尾) {
    从指针位置读入一个字符;
    if (当前没有正在运行的自动机) {
        根据读入的字符尝试分配自动机;
    }
    if (仍然没有分配到自动机) {
        调用可枚举 Token 处理程序进行识别;
        根据识别结果调整指针位置
    } else {
        尝试进行状态转换;
        if (状态转换成功) {
            进行进一步的判断确定其类型;
            指针向后移动一个字符;
        } else {
            调用出错处理程序;
        }
    }
}
```

## 使用说明

configs 目录下的 grammar.json 文件为本项目的文法配置文件，本项目提供一种默认的文法，也可根据需要调整其中内容，其结构如下：

```json5
{
    "alias": {
        /*
         * 这里包含文法中一组终结符的别名，其结构为别名名称对应终结符列表
         * 使用别名可以减少文法的编写工作量
         */
    },
    "keywords": [
        // 所有的关键字列表
    ],
    "constants": {
        "specials": [
            // 特殊常量列表
        ],
        "formulas": [
            /*
             * 描述常量的正规文法产生式列表
             * 产生式编写规则形如："[非终结符] -> 终结符|`别名` [非终结符]|ε"
             * 非终结符以[]包裹，名称可自定义
             * 终结符集合别名以``包裹
             * 单个终结符直接编写即可
             */
        ],
        "start": /* 文法起始符号 */, 
        "final": /* 文法结束符号 */
    },
    "identifiers": {
        "formulas": [
            // 描述标识符的正规文法产生式列表，编写规则同上
        ],
        "start": /* 文法起始符号 */, 
        "final": /* 文法结束符号 */
    },
    "operators": [
        // 所有的运算符列表，排列的顺序即为匹配的优先顺序
    ],
    "bounds": [
        // 所有的界符列表
    ],
    "spaces": [
       // 所有的空白符号列表，包括空格、制表符以及换行符等
    ]
}
```

本项目没有依赖其他任何第三方库，运行主程序 main.py 即可。本项目提供了一些测试用例，也可根据需要调整输入和输出文件路径。
