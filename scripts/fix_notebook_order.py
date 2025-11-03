#!/usr/bin/env python3
"""
Fix the notebook cell order
"""
import json
from pathlib import Path

# Load broken notebook
broken_path = Path("/Users/justin/Repos/poetry-bert-formalism/examples/shakespeare_sonnets_analysis_broken.ipynb")
with open(broken_path, 'r') as f:
    nb = json.load(f)

# Extract cells by their ID/position (based on analysis of content)
cells = nb['cells']

# Map cell indices to their content type for reordering
# Based on the read output, the cells are:
# 0: Enhanced Layer 3 Interpretation (markdown)
# 1: Three-layer comparison plot
# 2: Comparison statistics
# 3: Load enhanced Layer 3
# 4: Title
# 5: Imports
# 6: Load Results header
# 7: Load Layer 1 data
# 8-21: Layer 1 analysis
# 22-31: Basic Layer 3 analysis
# 32: Enhanced Layer 3 header

# Correct order
correct_order = [
    4,   # Title
    5,   # Imports
    6,   # Load Results header
    7,   # Load Layer 1 data
    8,   # Overall Statistics header
    9,   # Overall statistics
    10,  # Distribution Plot header
    11,  # Distribution plot
    12,  # Tortuosity Across Sequence header
    13,  # Tortuosity sequence plot
    14,  # Comparison by Sequence header
    15,  # Box plots by sequence
    16,  # Top 10 header
    17,  # Top 10 complex
    18,  # Bottom 10 header
    19,  # Bottom 10 complex
    20,  # Couplet Analysis header
    21,  # Couplet plot
    22,  # Layer 3 header
    23,  # Layer 3 methodology
    24,  # Load Layer 3 data
    25,  # Layer 3 Results header
    26,  # Layer 3 statistics
    27,  # Layer 3 by sequence
    28,  # Visualizations header
    29,  # Layer 3 comparison plots
    30,  # Layer 3 scatter plot
    31,  # Layer 3 interpretation
    32,  # Enhanced Layer 3 header
    3,   # Load enhanced data
    2,   # Enhanced statistics
    1,   # Enhanced visualization
    0,   # Enhanced interpretation
]

# Reorder cells
reordered_cells = [cells[i] for i in correct_order]

# Create new notebook with reordered cells
nb['cells'] = reordered_cells

# Write to new file
output_path = Path("/Users/justin/Repos/poetry-bert-formalism/examples/shakespeare_sonnets_analysis.ipynb")
with open(output_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"✓ Fixed notebook saved to {output_path}")
print(f"  Total cells: {len(reordered_cells)}")
