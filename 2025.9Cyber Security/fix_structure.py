import re

def fix_latex_structure(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复嵌套的section标题
    # 匹配类似 \section{Topic 2: Network \\section{...} System Security} 的模式
    content = re.sub(r'\\section\{([^{}]*?)\\section\{[^{}]*?\}([^{}]*?)\}([^{}]*?)\}([^{}]*?)\}', 
                     r'\\section{\1\2}', content)
    content = re.sub(r'\\section\{([^{}]*?)\\section\{[^{}]*?\}([^{}]*?)\}([^{}]*?)\}', 
                     r'\\section{\1\2}', content)
    content = re.sub(r'\\section\{([^{}]*?)\\section\{[^{}]*?\}([^{}]*?)\}', 
                     r'\\section{\1\2}', content)
    
    # 修复嵌套的subsection标题
    content = re.sub(r'\\subsection\{([^{}]*?)\\subsection\{[^{}]*?\}([^{}]*?)\}([^{}]*?)\}([^{}]*?)\}', 
                     r'\\subsection{\1\2}', content)
    content = re.sub(r'\\subsection\{([^{}]*?)\\subsection\{[^{}]*?\}([^{}]*?)\}([^{}]*?)\}', 
                     r'\\subsection{\1\2}', content)
    content = re.sub(r'\\subsection\{([^{}]*?)\\subsection\{[^{}]*?\}([^{}]*?)\}', 
                     r'\\subsection{\1\2}', content)
    content = re.sub(r'\\subsection\{([^{}]*?)\\section\{[^{}]*?\}([^{}]*?)\}', 
                     r'\\subsection{\1\2}', content)
    
    # 修复嵌套的subsubsection标题
    content = re.sub(r'\\subsubsection\{([^{}]*?)\\subsubsection\{[^{}]*?\}([^{}]*?)\}([^{}]*?)\}([^{}]*?)\}', 
                     r'\\subsubsection{\1\2}', content)
    content = re.sub(r'\\subsubsection\{([^{}]*?)\\subsubsection\{[^{}]*?\}([^{}]*?)\}([^{}]*?)\}', 
                     r'\\subsubsection{\1\2}', content)
    content = re.sub(r'\\subsubsection\{([^{}]*?)\\subsubsection\{[^{}]*?\}([^{}]*?)\}', 
                     r'\\subsubsection{\1\2}', content)
    content = re.sub(r'\\subsubsection\{([^{}]*?)\\subsection\{[^{}]*?\}([^{}]*?)\}', 
                     r'\\subsubsection{\1\2}', content)
    
    # 特殊处理Topic 2的标题
    content = re.sub(r'\\section\{Topic 2: Network.*?System Security\}.*?System Security\}.*?System Security\}', 
                     r'\\section{Topic 2: Network \\& System Security}', content)
    
    # 特殊处理MITRE ATT&CK的标题
    content = re.sub(r'\\subsection\{Part 1: MITRE ATT.*?CK Framework\}.*?CK Framework\}.*?CK Framework\}', 
                     r'\\subsection{Part 1: MITRE ATT\\&CK Framework}', content)
    
    # 修复问题标题
    content = re.sub(r'\\subsubsection\{What is the MITRE ATT.*?CK Framework and its primary purpose\?\}.*?CK Framework and its primary purpose\?\}.*?CK Framework and its primary purpose\?\}', 
                     r'\\subsubsection{What is the MITRE ATT\\&CK Framework and its primary purpose?}', content)
    
    content = re.sub(r'\\subsubsection\{How is the MITRE ATT.*?CK Framework organized\?\}.*?CK Framework organized\?\}.*?CK Framework organized\?\}', 
                     r'\\subsubsection{How is the MITRE ATT\\&CK Framework organized?}', content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("LaTeX structure fixed successfully!")

if __name__ == "__main__":
    fix_latex_structure("Report2.tex")