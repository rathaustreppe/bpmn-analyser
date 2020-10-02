# BPMN-Analyser [![Build Status](https://travis-ci.com/rathaustreppe/bpmn-analyser.svg?branch=master)](https://travis-ci.com/rathaustreppe/bpmn-analyser) [![Coverage Status](https://coveralls.io/repos/github/rathaustreppe/bpmn-analyser/badge.svg)](https://coveralls.io/github/rathaustreppe/bpmn-analyser)

Semantic analysis of BPMN-charts.

Research project to build a KISS-BPMNEngine for token based semantic checks of BPMN-diagrams.
Used in education to automatically compare students solutions with a master-solution.
Makes use of Natural Language Processing capabilities to read and understand semi-structured
text in BPMN diagrams.

Currently (10.2020) everything is under construction.

Current implemented features:
- can read valid and well-formed xml-bpmn files
- goes through the diagram and changes token
- text analysis features:
    - finds state-changing rules with RegExp-Chunker
    - uses wordnet to check for synonyms
- bpmn features:
    - sequence flows connecting elements
    - branching and joining inclusive, exclusive and parallel gateways
    - explicit loops (build with gateways)
    - loop-operators: increment, smaller and greather than