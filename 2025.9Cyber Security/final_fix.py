#!/usr/bin/env python3
import re

def final_fix_nested_titles(filename):
    """最终修复所有嵌套的LaTeX标题"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("开始最终修复所有嵌套的LaTeX标题...")
    
    # 修复所有嵌套的subsubsection标题
    # 处理多层嵌套的情况
    while re.search(r'\\subsubsection\{[^{}]*\\subsubsection\{', content):
        content = re.sub(r'\\subsubsection\{([^{}]*?)\\subsubsection\{[^{}]*?\}([^{}]*?)\}', 
                        r'\\subsubsection{\1\2}', content)
        print("✓ 修复了一层subsubsection嵌套")
    
    # 修复所有嵌套的subsection标题
    while re.search(r'\\subsection\{[^{}]*\\subsection\{', content):
        content = re.sub(r'\\subsection\{([^{}]*?)\\subsection\{[^{}]*?\}([^{}]*?)\}', 
                        r'\\subsection{\1\2}', content)
        print("✓ 修复了一层subsection嵌套")
    
    # 修复所有嵌套的section标题
    while re.search(r'\\section\{[^{}]*\\section\{', content):
        content = re.sub(r'\\section\{([^{}]*?)\\section\{[^{}]*?\}([^{}]*?)\}', 
                        r'\\section{\1\2}', content)
        print("✓ 修复了一层section嵌套")
    
    # 修复跨级别的嵌套（如subsubsection中包含subsection）
    content = re.sub(r'\\subsubsection\{([^{}]*?)\\subsection\{[^{}]*?\}([^{}]*?)\}', 
                    r'\\subsubsection{\1\2}', content)
    content = re.sub(r'\\subsection\{([^{}]*?)\\section\{[^{}]*?\}([^{}]*?)\}', 
                    r'\\subsection{\1\2}', content)
    
    # 特殊处理：修复特定的标题
    content = re.sub(r'\\subsubsection\{What are the main applications of MITRE ATT.*?CK in cybersecurity\?\}.*?\}.*?\}.*?\}.*?\}', 
                    r'\\subsubsection{What are the main applications of MITRE ATT\\&CK in cybersecurity?}', content)
    
    content = re.sub(r'\\subsubsection\{How does MITRE ATT.*?CK differ from traditional cybersecurity frameworks\?\}.*?\}.*?\}', 
                    r'\\subsubsection{How does MITRE ATT\\&CK differ from traditional cybersecurity frameworks?}', content)
    
    content = re.sub(r'\\subsection\{Part 2: Network.*?System Security Study Questions\}.*?\}.*?\}', 
                    r'\\subsection{Part 2: Network \\& System Security Study Questions}', content)
    
    content = re.sub(r'\\subsubsection\{Physical.*?Link Layer Security\}.*?\}.*?\}', 
                    r'\\subsubsection{Physical \\& Link Layer Security}', content)
    
    # 写回文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("最终LaTeX标题修复完成！")

if __name__ == "__main__":
    final_fix_nested_titles("Report2.tex")