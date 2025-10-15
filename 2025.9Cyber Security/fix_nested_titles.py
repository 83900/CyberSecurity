#!/usr/bin/env python3
import re

def fix_nested_latex_titles(filename):
    """修复嵌套的LaTeX标题"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("开始修复嵌套的LaTeX标题...")
    
    # 1. 修复Topic 2的section标题
    # 匹配模式: \section{Topic 2: Network \\section{...} System Security} System Security} System Security}
    topic2_pattern = r'\\section\{Topic 2: Network[^}]*\\section\{[^}]*\}[^}]*\}[^}]*\}[^}]*\}'
    if re.search(topic2_pattern, content):
        content = re.sub(topic2_pattern, r'\\section{Topic 2: Network \\& System Security}', content)
        print("✓ 修复了Topic 2的section标题")
    
    # 2. 修复MITRE ATT&CK的subsection标题
    # 匹配模式: \subsection{Part 1: MITRE ATT\\subsection{...}CK Framework}CK Framework}CK Framework}
    mitre_subsection_pattern = r'\\subsection\{Part 1: MITRE ATT[^}]*\\subsection\{[^}]*\}[^}]*\}[^}]*\}[^}]*\}'
    if re.search(mitre_subsection_pattern, content):
        content = re.sub(mitre_subsection_pattern, r'\\subsection{Part 1: MITRE ATT\\&CK Framework}', content)
        print("✓ 修复了MITRE ATT&CK的subsection标题")
    
    # 3. 修复第一个问题的subsubsection标题
    # 匹配模式: \subsubsection{What is the MITRE ATT\\subsubsection{...}CK Framework and its primary purpose?}...}
    question1_pattern = r'\\subsubsection\{What is the MITRE ATT[^}]*\\subsubsection\{[^}]*\}[^}]*\}[^}]*\}[^}]*\}'
    if re.search(question1_pattern, content):
        content = re.sub(question1_pattern, r'\\subsubsection{What is the MITRE ATT\\&CK Framework and its primary purpose?}', content)
        print("✓ 修复了第一个问题的subsubsection标题")
    
    # 4. 修复第二个问题的subsubsection标题
    # 匹配模式: \subsubsection{How is the MITRE ATT\\subsubsection{...}CK Framework organized?}...}
    question2_pattern = r'\\subsubsection\{How is the MITRE ATT[^}]*\\subsubsection\{[^}]*\}[^}]*\}[^}]*\}[^}]*\}'
    if re.search(question2_pattern, content):
        content = re.sub(question2_pattern, r'\\subsubsection{How is the MITRE ATT\\&CK Framework organized?}', content)
        print("✓ 修复了第二个问题的subsubsection标题")
    
    # 5. 通用修复：处理任何剩余的嵌套标题
    # 修复嵌套的section标题
    content = re.sub(r'\\section\{([^{}]*?)\\section\{[^{}]*?\}([^{}]*?)\}', r'\\section{\1\2}', content)
    content = re.sub(r'\\section\{([^{}]*?)\\section\{[^{}]*?\}([^{}]*?)\}([^{}]*?)\}', r'\\section{\1\2}', content)
    
    # 修复嵌套的subsection标题
    content = re.sub(r'\\subsection\{([^{}]*?)\\subsection\{[^{}]*?\}([^{}]*?)\}', r'\\subsection{\1\2}', content)
    content = re.sub(r'\\subsection\{([^{}]*?)\\section\{[^{}]*?\}([^{}]*?)\}', r'\\subsection{\1\2}', content)
    
    # 修复嵌套的subsubsection标题
    content = re.sub(r'\\subsubsection\{([^{}]*?)\\subsubsection\{[^{}]*?\}([^{}]*?)\}', r'\\subsubsection{\1\2}', content)
    content = re.sub(r'\\subsubsection\{([^{}]*?)\\subsection\{[^{}]*?\}([^{}]*?)\}', r'\\subsubsection{\1\2}', content)
    
    # 写回文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("LaTeX标题修复完成！")

if __name__ == "__main__":
    fix_nested_latex_titles("Report2.tex")