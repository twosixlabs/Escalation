import copy
import json

from graphics.cytoscape import Cytoscape
from utility.constants import (
    NODE_ID,
    SOURCE,
    TARGET,
    EDGE_ID,
    ELEMENT_PROPERTIES,
    PROPERTY_NAME,
    NODES,
    GROUP,
    COLUMN_NAME,
    LAYOUT,
    STYLE,
    SELECTOR,
    ELEMENT_STYLE,
    DATA,
    ID,
    ELEMENTS,
    STYLE_NAME,
    EDGES,
    PLOT_SPECIFIC_INFO,
)
import pytest


@pytest.fixture()
def make_data_cyto():
    data = {
        "beings": ["Zeus", "Poseidon", "Hades", "Theseus", "Orion"],
        "start": [
            "Zeus",
            "Poseidon",
            "Poseidon",
            "Poseidon",
            "Zeus",
            "Poseidon",
            "Hades",
            "Hades",
        ],
        "end": [
            "Poseidon",
            "Zeus",
            "Theseus",
            "Orion",
            "Hades",
            "Hades",
            "Zeus",
            "Poseidon",
        ],
        "numbers": ["0", "1", "2", "3", "4", "5", "6", "7"],
        "color": ["yellow", "blue", "red", "blue", "blue"],
        "class": ["god", "god,poseidon", "god", "poseidon", "poseidon"],
    }

    return data


@pytest.fixture()
def make_graphic_dict_cyto():
    graphic_dict = {
        PLOT_SPECIFIC_INFO: {
            NODE_ID: "beings",
            SOURCE: "start",
            TARGET: "end",
            EDGE_ID: "numbers",
            ELEMENT_PROPERTIES: [
                {PROPERTY_NAME: "classes", GROUP: NODES, COLUMN_NAME: "class"}
            ],
            LAYOUT: {"name": "cose"},
            STYLE: [
                {
                    SELECTOR: "node",
                    STYLE: {"shape": "round-pentagon", "label": "data(id)"},
                },
                {
                    SELECTOR: "edge",
                    STYLE: {
                        "target-arrow-shape": "triangle",
                        "curve-style": "straight",
                    },
                },
            ],
            ELEMENT_STYLE: [
                {STYLE_NAME: "background-color", GROUP: NODES, COLUMN_NAME: "color",}
            ],
        }
    }

    return graphic_dict


def test_make_dict_for_html_plot(make_data_cyto, make_graphic_dict_cyto):

    expected_dict = {
        ELEMENTS: [
            {GROUP: NODES, DATA: {ID: "Zeus"}, "classes": "god"},
            {GROUP: NODES, DATA: {ID: "Poseidon"}, "classes": "god,poseidon"},
            {GROUP: NODES, DATA: {ID: "Hades"}, "classes": "god"},
            {GROUP: NODES, DATA: {ID: "Theseus"}, "classes": "poseidon"},
            {GROUP: NODES, DATA: {ID: "Orion"}, "classes": "poseidon"},
            {DATA: {ID: "0", SOURCE: "Zeus", TARGET: "Poseidon"}, GROUP: EDGES},
            {DATA: {ID: "1", SOURCE: "Poseidon", TARGET: "Zeus"}, GROUP: EDGES},
            {DATA: {ID: "2", SOURCE: "Poseidon", TARGET: "Theseus"}, GROUP: EDGES},
            {DATA: {ID: "3", SOURCE: "Poseidon", TARGET: "Orion"}, GROUP: EDGES},
            {DATA: {ID: "4", SOURCE: "Zeus", TARGET: "Hades"}, GROUP: EDGES},
            {DATA: {ID: "5", SOURCE: "Poseidon", TARGET: "Hades"}, GROUP: EDGES},
            {DATA: {ID: "6", SOURCE: "Hades", TARGET: "Zeus"}, GROUP: EDGES},
            {DATA: {ID: "7", SOURCE: "Hades", TARGET: "Poseidon"}, GROUP: EDGES},
        ],
        LAYOUT: {"name": "cose"},
        STYLE: [
            {SELECTOR: "node", STYLE: {"shape": "round-pentagon", "label": "data(id)"}},
            {
                SELECTOR: "edge",
                STYLE: {"target-arrow-shape": "triangle", "curve-style": "straight"},
            },
            {SELECTOR: "#Zeus", STYLE: {"background-color": "yellow"},},
            {SELECTOR: "#Poseidon", STYLE: {"background-color": "blue"},},
            {SELECTOR: "#Hades", STYLE: {"background-color": "red"},},
            {SELECTOR: "#Theseus", STYLE: {"background-color": "blue"},},
            {SELECTOR: "#Orion", STYLE: {"background-color": "blue"},},
        ],
    }

    cyto_test = Cytoscape(make_graphic_dict_cyto)
    cyto_test.data = make_data_cyto
    cyto_test.make_dict_for_html_plot()
    cyto_dict = json.loads(cyto_test.graph_json_str)
    assert cyto_dict == expected_dict


def test_make_dict_for_html_plot_simple(make_data_cyto, make_graphic_dict_cyto):
    del make_graphic_dict_cyto[PLOT_SPECIFIC_INFO][ELEMENT_PROPERTIES]
    del make_graphic_dict_cyto[PLOT_SPECIFIC_INFO][STYLE]
    expected_dict = {
        ELEMENTS: [
            {GROUP: NODES, DATA: {ID: "Zeus"}},
            {GROUP: NODES, DATA: {ID: "Poseidon"}},
            {GROUP: NODES, DATA: {ID: "Hades"}},
            {GROUP: NODES, DATA: {ID: "Theseus"}},
            {GROUP: NODES, DATA: {ID: "Orion"}},
            {DATA: {ID: "0", SOURCE: "Zeus", TARGET: "Poseidon"}, GROUP: EDGES},
            {DATA: {ID: "1", SOURCE: "Poseidon", TARGET: "Zeus"}, GROUP: EDGES},
            {DATA: {ID: "2", SOURCE: "Poseidon", TARGET: "Theseus"}, GROUP: EDGES},
            {DATA: {ID: "3", SOURCE: "Poseidon", TARGET: "Orion"}, GROUP: EDGES},
            {DATA: {ID: "4", SOURCE: "Zeus", TARGET: "Hades"}, GROUP: EDGES},
            {DATA: {ID: "5", SOURCE: "Poseidon", TARGET: "Hades"}, GROUP: EDGES},
            {DATA: {ID: "6", SOURCE: "Hades", TARGET: "Zeus"}, GROUP: EDGES},
            {DATA: {ID: "7", SOURCE: "Hades", TARGET: "Poseidon"}, GROUP: EDGES},
        ],
        LAYOUT: {"name": "cose"},
        STYLE: [
            {SELECTOR: "#Zeus", STYLE: {"background-color": "yellow"},},
            {SELECTOR: "#Poseidon", STYLE: {"background-color": "blue"},},
            {SELECTOR: "#Hades", STYLE: {"background-color": "red"},},
            {SELECTOR: "#Theseus", STYLE: {"background-color": "blue"},},
            {SELECTOR: "#Orion", STYLE: {"background-color": "blue"},},
        ],
    }

    cyto_test = Cytoscape(make_graphic_dict_cyto)
    cyto_test.data = make_data_cyto
    cyto_test.make_dict_for_html_plot()
    cyto_dict = json.loads(cyto_test.graph_json_str)
    assert cyto_dict == expected_dict


def test_get_data_columns(make_data_cyto, make_graphic_dict_cyto):
    cyto_test = Cytoscape(make_graphic_dict_cyto)
    column_names = cyto_test.get_data_columns()
    expected_columns = set(make_data_cyto.keys())
    assert column_names == expected_columns
