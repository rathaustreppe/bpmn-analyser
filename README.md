# BPMN-Analyser

Semantic analysis of BPMN-charts.
Research project with token based semantic checks of BPMN-diagrams.
And Natural Language Processing capabilities to read unstructured
text in BPMN diagrams.

Currently (09.2020) everything is under construction.

Current implemented features:
- can read valid and well-formed xml-bpmn files
- converts it to graph (linear graphs)
- goes through the graph and changes token
- text analysis features:
    - finds state-changing rules with RegExp-Chunker
    - uses wordnet to check for synonyms
