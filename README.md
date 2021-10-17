# Belief Improver
Implementation of Belief Improver

## Mutator Module
The Mutator generates mutated statements from an initial belief statement. 

`python3 mutator.py -i input.xml -o mutated`

The initial belief statement must be passed in as an XML file to the Mutator module with `-i` parameter. 

The output file name can be optionally specified using `-o` parameter.

## Evaluator Module
The Evaluator calculates the scores for the initial belief statement and the mutated statements based on the field data and outputs an evaluation csv file that contains the scores for each statement.

`python3 evaluator.py -i input.xml -m mutated.xml -d data.csv -o result_1 -a a`

The initial belief statement, mutated statements, and field data file must be passed in to the Evaluator module with `-i`, `-m`, and `-d` parameters, respectively. 

The output file name's prefix can be optionally specified using `-o` parameter.

By default, only the improved statements will be included in the resulting file. However, the user can optionally specify to include all statements and their scores in the result using `-a` parameter. 