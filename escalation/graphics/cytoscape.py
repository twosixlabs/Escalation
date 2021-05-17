import json

from graphics.graphic_class import Graphic
from utility.constants import (
    DATA,
    NODE_ID,
    GROUP,
    NODES,
    ID,
    SOURCE,
    TARGET,
    EDGE_ID,
    EDGES,
    ELEMENTS,
    ELEMENT_PROPERTIES,
    COLUMN_NAME,
    STYLE,
    LAYOUT,
    PROPERTY_NAME,
    PROPERTIES,
    STYLE_NAME,
    ELEMENT_STYLE,
    SELECTOR,
    PLOT_SPECIFIC_INFO,
)

keys_transferred_as_is = [
    LAYOUT,
    "data",
    "zoom",
    "pan",
    "minZoom",
    "maxZoom",
    "zoomingEnabled",
    "userZoomingEnabled",
    "panningEnabled",
    "userPanningEnabled",
    "boxSelectionEnabled",
    "selectionType",
    "touchTapThreshold",
    "desktopTapThreshold",
    "autoungrabify",
    "autolock",
    "autounselectify",
    "headless",
    "styleEnabled",
    "hideEdgesOnViewport",
    "textureOnViewport",
    "motionBlur",
    "motionBlurOpacity",
    "wheelSensitivity",
    "pixelRatio",
]


class Cytoscape(Graphic):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.id_dict = {}
        self.node_dict = {}
        self.edge_dict = {}

    def data_to_element_array(self, instruction_array: list, is_property: bool = True):
        """
        Uses the instructions in the element array to put the data into the node and edge dict
        :param instruction_array:
        :param is_property: property or style
        """
        position_name_lookup = {"position_x": "x", "position_y": "y"}
        if is_property:
            name = PROPERTY_NAME
            intermediate_name = PROPERTIES
        else:
            name = STYLE_NAME
            intermediate_name = STYLE

        for instruction_dict in instruction_array:
            property_name = instruction_dict[name]
            element_type = instruction_dict[GROUP]
            if element_type == NODES:
                element_dict = self.node_dict  # both sides should have same reference
            elif element_type == EDGES:
                element_dict = self.edge_dict  # both sides should have same reference
            for element_id, value in zip(
                self.id_dict[element_type], self.data[instruction_dict[COLUMN_NAME]]
            ):

                if is_property and property_name in ["position_y", "position_x"]:
                    position = position_name_lookup[property_name]
                    position_dict_temp = element_dict[ID][intermediate_name].get(
                        "position", {}
                    )
                    position_dict_temp[position] = value
                    element_dict[element_id][intermediate_name][
                        "position"
                    ] = position_dict_temp
                else:
                    element_dict[element_id][intermediate_name][property_name] = value

    def make_arrays_for_cytoscape(self, style_array_for_cytoscape) -> [list, list]:
        """
        creates element and adds to style array from node and edge dictionaries for Cytoscape dictionary
        :param style_array_for_cytoscape: current array with style options from plot_options
        :return:
        """

        elements = []
        for element_dict, group in zip(
            [self.node_dict, self.edge_dict], [NODES, EDGES]
        ):
            for element_id, properties in element_dict.items():
                temp_dict = properties.get(PROPERTIES, {})
                temp_dict[GROUP] = group
                temp_dict[DATA] = {ID: element_id}
                if group == EDGES:
                    temp_dict[DATA][SOURCE] = properties[SOURCE]
                    temp_dict[DATA][TARGET] = properties[TARGET]
                elements.append(temp_dict)
                element_style_dict = properties[STYLE]
                if element_style_dict:
                    style_array_for_cytoscape.append(
                        {SELECTOR: f"#{element_id}", STYLE: element_style_dict}
                    )
        return elements, style_array_for_cytoscape

    def make_dict_for_html_plot(self) -> str:
        """
        Takes in the data as well user specified json and makes a json according to the specification of Cytoscape
        """
        plot_options = self.graphic_dict[PLOT_SPECIFIC_INFO]

        cytoscape_dict = {
            key: value
            for key, value in plot_options.items()
            if key in keys_transferred_as_is
        }

        sources = self.data[plot_options[SOURCE]]
        targets = self.data[plot_options[TARGET]]

        nodes = (
            self.data[plot_options[NODE_ID]]
            if NODE_ID in plot_options
            else set(sources).union(set(targets))
        )
        edges = (
            self.data[plot_options[EDGE_ID]]
            if EDGE_ID in plot_options
            else [f"{source}_to_{target}" for source, target in zip(sources, targets)]
        )

        id_dict = {NODES: nodes, EDGES: edges}

        # For simplicity, we add an extra step. we take the element level properties put them into dictionaries
        # then put them into the cytoscape json. The major reason being that cytoscape takes an array of dictionaries
        # with a key:value pair identifying the element

        # create element level dictionaries. maybe combined the two dictionaries.
        node_dict = {node: {PROPERTIES: {}, STYLE: {}} for node in nodes}
        edge_dict = {edge: {PROPERTIES: {}, STYLE: {}} for edge in edges}
        for source, target, edge in zip(sources, targets, edges):
            edge_dict[edge][SOURCE] = source
            edge_dict[edge][TARGET] = target

        self.id_dict = id_dict
        self.node_dict = node_dict
        self.edge_dict = edge_dict
        # Fill up the element level dictionaries
        # plot_option[ELEMENT_PROPERTIES] are data that goes into the cytoscape element array on a per element basis
        self.data_to_element_array(plot_options.get(ELEMENT_PROPERTIES, []), True)
        # plot_option[ELEMENT_STYLE] are data that goes into the cytoscape style array on a per element basis
        self.data_to_element_array(plot_options.get(ELEMENT_STYLE, []), False)

        # create json for cytoscape
        (elements, style_array_for_cytoscape,) = self.make_arrays_for_cytoscape(
            plot_options.get(STYLE, [])
        )

        cytoscape_dict[ELEMENTS] = elements
        cytoscape_dict[STYLE] = style_array_for_cytoscape

        self.graph_json_str = json.dumps(cytoscape_dict)

    @staticmethod
    def get_graph_html_template() -> str:
        return "cytoscape.html"

    def get_data_columns(self) -> set:
        """
        extracts what columns of data are needed from the plot_options
        :param plot_options:
        :return:
        """
        plot_options = self.graphic_dict[PLOT_SPECIFIC_INFO]
        possible_keys = [NODE_ID, SOURCE, TARGET, EDGE_ID]
        set_of_column_names = set()
        for key_name in possible_keys:
            if key_name in plot_options:
                set_of_column_names.add(plot_options[key_name])
        for key_name in [ELEMENT_PROPERTIES, ELEMENT_STYLE]:
            if key_name in plot_options:
                for option_dict in plot_options[key_name]:
                    set_of_column_names.add(option_dict[COLUMN_NAME])
        return set_of_column_names
