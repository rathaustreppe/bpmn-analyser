from typing import Optional, List, Tuple

from pedantic import pedantic_class
from xml.etree.ElementTree import Element

from src.converter.bpmn_models.bpmn_enum import BPMNEnum

@pedantic_class
class XMLReader:
    def __init__(self,
                 xml_dom: Optional[Element] = None,
                 abs_path: Optional[str] = None,
                 rel_path: Optional[str] = None) -> None:
        self.xml_dom = xml_dom
        self.abs_path = abs_path
        self.rel_path = rel_path

    def prepare_dom(self) -> None:
        """
        The bpmn-xml of demo.bpmn.io contains wrong
        xmlns-definitions that prevent the python xml
        parser to read the xml.
        We kick them out.
        It also creates alot of diagram-position-attributes.
        When kicking out <definitions>, the xml is still not
        well-formed:
        before:
        <definitions ....> # prevent parsing
            <process>
                # our process discription
            </process>
            <bpmndi>
                # information where to put diagrams in a gui
            </bpmndi>
        </definitions>
        So we delete bpmndi and all sub-tags too.
        Can work with relative and absolute paths.
        """

        # we need those sadistic low-level commands, because
        # we cannot parse the xml, modify it with xpath and
        # write it back, because the parser dies.
        if self.abs_path is None:
            self.abs_path = self.rel_to_abs_path()
        with open(self.abs_path, "r") as f:
            lines = f.readlines()

        # lines to delete containing:
        block_ids: Tuple[str, ...] = ('<definitions', '</definitions',
                       '<bpmndi', '</bpmndi',
                       '<omgdi', '<omgdc')

        new_file = [line for line in lines
                    if not any(map(line.__contains__,block_ids))]

        # write back without deleted lines in new file
        with open(self.abs_path, "w") as f:
            for line in new_file:
                f.write(line)

    def parse_to_dom(self, abs_path: Optional[str] = None) -> Element:
        """
        Reads the file from self.abs_path and tries to
        parse it. Returns a traversable xml-dom object.
        (Not a long string!)
        Returns:
            Element: with XPath traversable XML Element Tree.
        """
        if abs_path is not None:
            self.abs_path = abs_path

        # abs_path can be set via constructor, so extra check
        # needed
        if self.abs_path is None:
            self.abs_path = self.rel_to_abs_path()
        try:
            import xml.etree.ElementTree as ET
            self.xml_dom = ET.parse(self.abs_path).getroot()

        except Exception as e:
            print(e)
        return self.xml_dom

    def query(self, element_name: BPMNEnum) -> List[Element]:
        """
        access all <elementnames> of xml file with XPath syntax
        .// means: in whole xml document (doesnt care about depth)
        https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath
        optional, you can specifiy a list of elements
        that are ignored
        return a list containing all elements in the xml with
        the <elementname> tag
        Example with exclude_ids: 123
        <hello>
          <world id=123\>
          <world id=456\>
        <\hello>
        elementname: 'world'
        Returns: [<world id=456>] with 'world' beeing an object
        Args:
            element_name (str): elementname of bpmn-specification

        Returns:
        """
        elements_in_file = []
        for element in self.xml_dom.findall(
                './/' + element_name.value):
            # We dont need to preserve which sequence flow is
            # incomming and outgoing. This is stored in
            # sourceRef and targetRef of each sequenceFlow.
            elements_in_file.append(element)

        return elements_in_file


    def rel_to_abs_path(self) -> str:
        import os
        abs_path = os.path.abspath(self.rel_path)
        self.abs_path = abs_path
        return abs_path
