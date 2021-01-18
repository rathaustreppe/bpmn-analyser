# BPMN-Analyser 

<!-- PROJECT SHIELDS -->
[![Build Status][travis-shield]][travis-url]
[![Coverage Status][coverage-badge]][coverage-url]

Educational tool for semantic analysis of BPMN-diagrams. 
Define sample solutions, let your students create diagrams
and compare their solutions with yours.



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Features](#features)
* [Getting Started](#getting-started)
* [RoadMap](#roadmap)

## About the Project
Software engineers and business administration need to understand business processes in order 
to develop software that fits the need and simplifies the whole process.

Teach your students business process modelling skills by focusing on what is important:
Understanding real-life-constraints and expressing their ideas with modelling.

Think about a business process in real-life. Maybe a customer orders 
coffee beans in your online shop or your universitity administration takes ages to reply to your application.
If you want your students to model this process, BPMN-Analyzer helps you to
* precisely formulate a task description
* define real-life-constraints that limit your process

Let your students model this process
* on a web-application without any installation necessary
* supporting them with automated BPMN2.0 syntax checking

Check your students solutions
* in an automated or single-stepped simulation
* compare it with the real-life-constraints you defined above.
Check if they found them as well! This is the evidence if your
students modelled the process correctly.


## Features
BPMN-Analyzer can
* read valid and well-formed BPMN2.0-XMLs. Use [camundas BPMN tool](https://demo.bpmn.io) for modelling!
Check out the [BPMN linting tool](https://github.com/bpmn-io/bpmnlint-playground) for syntax checks.
* execute elements of BPMN:
    * activities, start-and end events
    * gateways: parallel, inclusive & exclusive 
    * explicit loops
* define rules and token for sample solution


## Getting Started
This piece of software is currently under development.
It is not yet published or hosted. Please refer to the [RoadMap](#roadmap) to 
see when this will happen. This means there is no real 'getting started' yet.

Nevertheless you can have a look in the [examples.](https://github.com/rathaustreppe/bpmn-analyser/tree/master/src/examples)
They are documented in code.

If you wish to execute them, clone the repository,
install Python 3.8 (or newer) and execute the main.py.


## RoadMap
For further workflow-optimization a front-end integration will be done 
in early 2021.


[travis-shield]: https://travis-ci.com/rathaustreppe/bpmn-analyser.svg?branch=master
[travis-url]: https://travis-ci.com/rathaustreppe/bpmn-analyser
[coverage-badge]:https://coveralls.io/repos/github/rathaustreppe/bpmn-analyser/badge.svg
[coverage-url]:https://coveralls.io/github/rathaustreppe/bpmn-analyser