# prompt_template.py

def get_hsg9_prompt(query, search_context):
    return f'''
    You are an elite National Mathematics Olympiad coach and master problem solver for Gifted Students (HSG Toán 9). 
    Topic Focus: {query}

    Comprehensive Reference Context:
    {search_context}

    ---

    ### STRICT REQUIREMENTS FOR THE REPORT:
    1. **Academic Tone & Depth**: Written in professional academic English, structured with rigorous mathematical proofs, lemmas, and insights suitable for top-tier student competitions.
    2. **Multi-Approach Generation (Max Exhaustion)**: Provide exactly **15 distinct, highly creative, and rigorous solution methods** (breaking down algebraic manipulation, transformations, analytical, geometric, symmetry, or functional perspectives) for representative master problems in this topic.
    3. **LaTeX Rigor (Crucial)**: 
       - Every single mathematical expression, variable, equation, or theorem MUST be wrapped in standard LaTeX syntax.
       - Use inline math with single dollar signs (e.g., $x^2 + y^2 \\geq 2xy$) and block equations with double dollar signs:
         $$\\frac{{a}}{{b}} + \\frac{{b}}{{a}} \\ge 2$$
       - Do not use plain text for math symbols.
    4. **Structure**:
       - **# Title**: Formal title for the topic.
       - **## Overview & Core Principles**: Theoretical foundations and background theorems.
       - **## 50 Distinct Solution Methods**: Detailed step-by-step presentation of all 50 methods applied to the representative problems, clearly numbered from Method 1 to Method 50.
       - **## Comparative Insights & Summary**: A brief expert synthesis on when to apply each method effectively.
    '''
