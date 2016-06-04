from tree import Tree

class SyntaxTree(Tree):
    '''
    NOTE:
     - contruct ST using an abstract parser
     - practical parser implements the abstract parser
     - ConcreteSyntaxTree uses a parser that can provide original formatting so that
       the original formatting can be recovered, while AbstractSyntaxTree is not
     - May inherit from multiple parent class for adding generic the recovery feature
     - A parser may have multiple level parsing: (multiple)line-level, statement level, expression level, ...
     - Reader class read external information source with a particular format or soruce types and 
       convert it to the format that a parser can parse
'''
