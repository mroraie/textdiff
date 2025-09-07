# **Project Report: Persian Text Comparator**

**Date:** September 2025  
**Course:** Data Structures, Dr. Navid Naderi
**Project Topic:** Web-based Persian Text Comparison
**Technology:** Python, Django Framework

## **1. Abstract**

In this project, a web-based application was designed and implemented to calculate the similarity between two Persian sentences. The core algorithm used is the [[**Levenshtein Distance**https://en.wikipedia.org/wiki/Levenshtein_distance]], which computes the minimum number of edit operations (insertion, deletion, or substitution of characters) required to transform one text into another.

To improve accuracy for Persian texts, a **preprocessing(preprocessing.py) and normalization**(aligment.py) stage was added, converting the input into a uniform phonetic representation. The user interface was developed with the Django framework.

## **2. Introduction**

Text similarity comparison is a fundamental problem in Natural Language Processing (NLP) with applications in spell-checking, plagiarism detection, and duplicate data elimination.

The main challenge in Persian lies in the existence of **diacritics (harakat)** and letters with variable phonetic roles (such as "و"). To address this, the project operates in two steps:

1. **Preprocessing and normalization:** Removing noise and converting the text into a standard phonetic representation.
    
2. **Similarity calculation:** Applying the Levenshtein algorithm to the normalized texts.
	and calcute the similitry score
    

## **3. System Architecture**

The workflow is as follows:

1. Receive texts from the user
2. Apply preprocessing (remove diacritics, normalize “alef” forms, detect and silence “و”)
3. Convert text into a phonetic representation
4. Run the Levenshtein algorithm
5. Display results and similarity percentage in the web interface
6.  generate destence graph (based on lenvenshtain graph travsing theory)
    

## **4. Key Algorithms and Functions**

### **4.1. Levenshtein Algorithm**

- **Input:** Two strings (list of characters or words)
    
- **Output:** Edit distance and the sequence of operations (insertion, deletion, substitution)
    
- **Implementation:** Dynamic Programming
    

Similarity formula:

Similarity(%)=(1−Distancemax⁡(len(str1),len(str2)))×100Similarity(\%) = \Big(1 - \frac{Distance}{\max(len(str1), len(str2))}\Big) \times 100

### **4.2. Preprocessing (`preprocessing.py`)**

The `preprocessing.py` module provides several key functions for cleaning and normalizing Persian text before similarity calculation:

- **`clean_word(word)`**  
    Removes ignored characters (e.g., diacritics, elongation marks, spaces, "ـ").  

    
- **`get_removed_chars(word)`**  
    Returns only the list of removed characters without modifying the original text.
    
- **`is_diacritic(char)`**  
    Checks whether a character is a diacritic (vowel markers used in Persian/Arabic scripts).
    
- **`is_phonetically_silent_vav(word, pos)`**  
    Detects instances of the letter “و” that are phonetically silent.
    
- **`validate_text_length(view_func)`**  
    A decorator that validates input length and word count. If either exceeds the allowed threshold, it raises an error and prevents further execution.
    
- **`convert_to_phonetic(text)`**  
    Converts Persian/Arabic text into a **phonetic representation** by mapping characters (e.g., “و” → `v` or `u`).  
    **Input:** Original text  
    **Output:** Phonetic text

### **4.3. Alignment**
The `alignment.py` module presents the algorithm

- **`align_words()`**: Word-by-word comparison with different operation costs (insert, delete, substitute)
    
- **`align_words_with_similarity()`**: Approximate alignment using a similarity threshold (for spelling mistakes)
    
- **`align_texts_step_by_step()`**: Runs all methods and aggregates results
    

### **4.4. Highlighting**

The `highlighting.py` module presents the algorithm output as color-coded text for the user:

- **Red:** Deletion
    
- **Green:** Insertion
    
- **Blue/Purple:** Substitution of specific letters (e.g., alef variants or “و”)
    

Special considerations in project design:

- **Modularity:** Clear separation of components (preprocessing, algorithms, highlighting, Django views)
- **Maintainability:** Adjustable configurations via `constants.py` without altering core logic
- **Readable Naming:** Functions and variables clearly describe their purpose
- **Documentation & Docstrings:** Each function includes detailed explanations



Proof of work: 

Index page:
![[Pasted image 20250906103801.png]]


Resaults Summery:
![[Pasted image 20250906103824.png]]


Preprocessing:
![[Pasted image 20250906103846.png]]

Execution of alignment algorithms for detecting words at a specific alignment (useful for sentences with unequal word counts):

![[Pasted image 20250906103948.png]]

resaults of Execution of alignment algorithms:


![[Pasted image 20250906104231.png]]


Visualization of the alignment matrix:

![[Pasted image 20250906104313.png]]


final resault: 
* persian text:
![[Pasted image 20250906104430.png]]
* phonetic:
![[Pasted image 20250906104801.png]]


final graph:
![[Pasted image 20250906104700.png]]

this app can make a Markdown report file with summery details:
![[Pasted image 20250906105557.png]]


## References 
1. Levenshtein Distance: [Wikipedia](https://en.wikipedia.org/wiki/Levenshtein_distance)  
2. Project Source Code: [GitHub Repository](https://github.com/mroraie/textdiff)  
3. Live Demo: [TextDiff Web Application](http://www.mroraie.ir/textdiff)  
4. Django Documentation - [https://www.djangoproject.com/](https://www.djangoproject.com/)  


