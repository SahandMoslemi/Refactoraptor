## Research Replication 
- Replication package of research part is located in `dataset/`
- Each `.json` file in `dataset/` includes 48 (4 Languages * 3 Difficulties * 4) records. Each record has only 1 violation and comes with its non violating version. These files are the manually prepared ground truth.
- `dataset/clean_code_pipeline.py`, `dataset/processing_pipeline.py` and `dataset/known_violation_pipeline.py` generates the files in `dataset/output/` using Refactoraptor API (with the server running locally) for all strategies. 
- `dataset/clean_code_pipeline.py` uses already clean code as input.
- `dataset/processing_pipeline.py` uses violated code wwithour specifying ground truth violation. Generates files with the same names as those in `dataset/clean_code_pipeline.py`.
- `dataset/known_violation_pipeline.py` uses violated code and includes the ground truth violation type in the prompt.

- `sahand.py` contains disorganized code that I need to restructure.
 

## TMP
 
DIP
we already have Email Service Dependencies come up with another
an we already have Database Connection Management
and we have Payment Processing System already
Document Processing System

LSP
Vehicle Fuel System
Payment Processing System
Bird Flying Behavior 
Document Processing System
