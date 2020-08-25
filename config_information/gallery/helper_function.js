function get_schema(){

const dict_of_schemas={
    "graphic_schema": {
        "$schema": "http://json-schema.org/draft/2019-09/schema#",
        "type": "object",
        "title": "Escalation Graphic Config Generator",
        "description": "Have a unique one of these for each graphic on the page",
        "required": [
            "plot_manager",
            "title",
            "brief_desc",
            "data_sources"
        ],
        "additionalProperties": false,
        "properties": {
            "plot_manager": {
                "type": "string",
                "description": "plot library you would like to use (only plotly is currently available)",
                "enum": [
                    "plotly"
                ]
            },
            "title": {
                "type": "string",
                "description": "Graph title (optional)"
            },
            "brief_desc": {
                "type": "string",
                "description": "Text caption shown above the graph (optional)"
            },
            "data_sources": {
                "type": "object",
                "description": "Define which data tables are used in this graphic, and on which columns the data tables are joined",
                "required": [
                    "main_data_source"
                ],
                "properties": {
                    "main_data_source": {
                        "type": "object",
                        "additionalProperties": false,
                        "required": [
                            "data_source_type"
                        ],
                        "properties": {
                            "data_source_type": {
                                "type": "string",
                                "enum": [
                                    "penguin_size",
                                    "mean_penguin_stat",
                                    "penguin_size_small"
                                ]
                            }
                        }
                    },
                    "additional_data_sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": false,
                            "required": [
                                "data_source_type",
                                "join_keys"
                            ],
                            "properties": {
                                "data_source_type": {
                                    "type": "string",
                                    "enum": [
                                        "penguin_size",
                                        "mean_penguin_stat",
                                        "penguin_size_small"
                                    ]
                                },
                                "join_keys": {
                                    "type": "array",
                                    "description": "Column names along which to join the tables (in the case of 2 or more tables)",
                                    "items": {
                                        "type": "array",
                                        "uniqueItems": true,
                                        "minItems": 2,
                                        "maxItems": 2,
                                        "items": {
                                            "type": "string",
                                            "enum": [
                                                "penguin_size:study_name",
                                                "penguin_size:species",
                                                "penguin_size:island",
                                                "penguin_size:sex",
                                                "penguin_size:region",
                                                "penguin_size:culmen_depth_mm",
                                                "penguin_size:culmen_length_mm",
                                                "penguin_size:flipper_length_mm",
                                                "penguin_size:body_mass_g",
                                                "mean_penguin_stat:study_name",
                                                "mean_penguin_stat:species",
                                                "mean_penguin_stat:sex",
                                                "mean_penguin_stat:culmen_length",
                                                "mean_penguin_stat:culmen_depth",
                                                "mean_penguin_stat:flipper_length",
                                                "mean_penguin_stat:body_mass",
                                                "mean_penguin_stat:delta_15_n",
                                                "mean_penguin_stat:delta_13_c",
                                                "penguin_size_small:species",
                                                "penguin_size_small:island",
                                                "penguin_size_small:culmen_length_mm",
                                                "penguin_size_small:culmen_depth_mm",
                                                "penguin_size_small:flipper_length_mm",
                                                "penguin_size_small:body_mass_g",
                                                "penguin_size_small:sex"
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "plotly_schema": {
        "scatter": {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "plotly graph definition",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [
                "data"
            ],
            "properties": {
                "data": {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "title": "data dictionary",
                        "required": [
                            "type",
                            "x",
                            "y",
                            "mode"
                        ],
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "scattergl uses uses WebGL which is faster for lots of points",
                                "enum": [
                                    "scatter",
                                    "scattergl"
                                ]
                            },
                            "x": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "y": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "mode": {
                                "type": "string",
                                "description": "marker for scatter plot, line for line plot",
                                "enum": [
                                    "lines",
                                    "markers",
                                    "text",
                                    "lines+markers",
                                    "markers+text",
                                    "lines+text",
                                    "lines+markers+text",
                                    "none",
                                    "group"
                                ]
                            }
                        }
                    }
                },
                "layout": {
                    "title": "Graph layout",
                    "description": "Determines how the graph looks",
                    "type": "object",
                    "properties": {
                        "height": {
                            "type": "number",
                            "minimum": 10
                        },
                        "width": {
                            "type": "number",
                            "minimum": 10
                        },
                        "xaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "yaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "hovermode": {
                            "type": "string",
                            "enum": [
                                "x",
                                "y",
                                "closest",
                                "false",
                                "x unified",
                                "y unified"
                            ]
                        }
                    }
                }
            }
        },
        "bar": {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "plotly graph definition",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [
                "data"
            ],
            "properties": {
                "data": {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "title": "data dictionary",
                        "required": [
                            "type",
                            "x",
                            "y"
                        ],
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "type of plot",
                                "enum": [
                                    "bar"
                                ]
                            },
                            "x": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "y": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            }
                        }
                    }
                },
                "layout": {
                    "title": "Graph layout",
                    "description": "Determines how the graph looks",
                    "type": "object",
                    "properties": {
                        "height": {
                            "type": "number",
                            "minimum": 10
                        },
                        "width": {
                            "type": "number",
                            "minimum": 10
                        },
                        "xaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "yaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "hovermode": {
                            "type": "string",
                            "enum": [
                                "x",
                                "y",
                                "closest",
                                "false",
                                "x unified",
                                "y unified"
                            ]
                        }
                    }
                }
            }
        },
        "box": {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "plotly graph definition",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [
                "data"
            ],
            "properties": {
                "data": {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "title": "data dictionary",
                        "required": [
                            "type",
                            "y"
                        ],
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "Best used with the group by visualization option",
                                "enum": [
                                    "box"
                                ]
                            },
                            "y": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            }
                        }
                    }
                },
                "layout": {
                    "title": "Graph layout",
                    "description": "Determines how the graph looks",
                    "type": "object",
                    "properties": {
                        "height": {
                            "type": "number",
                            "minimum": 10
                        },
                        "width": {
                            "type": "number",
                            "minimum": 10
                        },
                        "xaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "yaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "hovermode": {
                            "type": "string",
                            "enum": [
                                "x",
                                "y",
                                "closest",
                                "false",
                                "x unified",
                                "y unified"
                            ]
                        }
                    }
                }
            }
        },
        "violin": {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "plotly graph definition",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [
                "data"
            ],
            "properties": {
                "data": {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "title": "data dictionary",
                        "required": [
                            "type",
                            "y"
                        ],
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "type of plot",
                                "enum": [
                                    "violin"
                                ]
                            },
                            "y": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            }
                        }
                    }
                },
                "layout": {
                    "title": "Graph layout",
                    "description": "Determines how the graph looks",
                    "type": "object",
                    "properties": {
                        "height": {
                            "type": "number",
                            "minimum": 10
                        },
                        "width": {
                            "type": "number",
                            "minimum": 10
                        },
                        "xaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "yaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "hovermode": {
                            "type": "string",
                            "enum": [
                                "x",
                                "y",
                                "closest",
                                "false",
                                "x unified",
                                "y unified"
                            ]
                        }
                    }
                }
            }
        },
        "histogram": {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "plotly graph definition",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [
                "data"
            ],
            "properties": {
                "data": {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "title": "data dictionary",
                        "required": [
                            "type",
                            "x"
                        ],
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "type of plot",
                                "enum": [
                                    "histogram"
                                ]
                            },
                            "x": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            }
                        }
                    }
                },
                "layout": {
                    "title": "Graph layout",
                    "description": "Determines how the graph looks",
                    "type": "object",
                    "properties": {
                        "height": {
                            "type": "number",
                            "minimum": 10
                        },
                        "width": {
                            "type": "number",
                            "minimum": 10
                        },
                        "xaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "yaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "hovermode": {
                            "type": "string",
                            "enum": [
                                "x",
                                "y",
                                "closest",
                                "false",
                                "x unified",
                                "y unified"
                            ]
                        }
                    }
                }
            }
        },
        "contour": {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "plotly graph definition",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [
                "data"
            ],
            "properties": {
                "data": {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "title": "data dictionary",
                        "required": [
                            "type",
                            "x",
                            "y",
                            "z"
                        ],
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "type of plot",
                                "enum": [
                                    "contour"
                                ]
                            },
                            "x": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "y": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "z": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            }
                        }
                    }
                },
                "layout": {
                    "title": "Graph layout",
                    "description": "Determines how the graph looks",
                    "type": "object",
                    "properties": {
                        "height": {
                            "type": "number",
                            "minimum": 10
                        },
                        "width": {
                            "type": "number",
                            "minimum": 10
                        },
                        "xaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "yaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "hovermode": {
                            "type": "string",
                            "enum": [
                                "x",
                                "y",
                                "closest",
                                "false",
                                "x unified",
                                "y unified"
                            ]
                        }
                    }
                }
            }
        },
        "mesh3d": {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "plotly graph definition",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [
                "data"
            ],
            "properties": {
                "data": {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "title": "data dictionary",
                        "required": [
                            "type",
                            "x",
                            "y",
                            "z"
                        ],
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "type of plot",
                                "enum": [
                                    "mesh3d"
                                ]
                            },
                            "x": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "y": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "z": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            }
                        }
                    }
                },
                "layout": {
                    "title": "Graph layout",
                    "description": "Determines how the graph looks",
                    "type": "object",
                    "properties": {
                        "height": {
                            "type": "number",
                            "minimum": 10
                        },
                        "width": {
                            "type": "number",
                            "minimum": 10
                        },
                        "xaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "yaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "hovermode": {
                            "type": "string",
                            "enum": [
                                "x",
                                "y",
                                "closest",
                                "false",
                                "x unified",
                                "y unified"
                            ]
                        }
                    }
                }
            }
        },
        "heatmap": {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "plotly graph definition",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [
                "data"
            ],
            "properties": {
                "data": {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "title": "data dictionary",
                        "required": [
                            "type",
                            "x",
                            "y",
                            "z"
                        ],
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "heatmapgl uses WebGL which may be faster for lots of points",
                                "enum": [
                                    "heatmap",
                                    "heatmapgl"
                                ]
                            },
                            "x": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "y": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "z": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            }
                        }
                    }
                },
                "layout": {
                    "title": "Graph layout",
                    "description": "Determines how the graph looks",
                    "type": "object",
                    "properties": {
                        "height": {
                            "type": "number",
                            "minimum": 10
                        },
                        "width": {
                            "type": "number",
                            "minimum": 10
                        },
                        "xaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "yaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "hovermode": {
                            "type": "string",
                            "enum": [
                                "x",
                                "y",
                                "closest",
                                "false",
                                "x unified",
                                "y unified"
                            ]
                        }
                    }
                }
            }
        },
        "scatter3d": {
            "$schema": "http://json-schema.org/draft/2019-09/schema#",
            "title": "plotly graph definition",
            "description": "dictionary that follows https://plotly.com/javascript/reference/",
            "type": "object",
            "required": [
                "data"
            ],
            "properties": {
                "data": {
                    "type": "array",
                    "description": "list of graphs to be plotted on a single plot",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "title": "data dictionary",
                        "required": [
                            "type",
                            "x",
                            "y",
                            "z",
                            "mode"
                        ],
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "type of plot",
                                "enum": [
                                    "scatter3d"
                                ]
                            },
                            "x": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "y": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "z": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            },
                            "mode": {
                                "type": "string",
                                "description": "if using line make sure your points are in a sensible order",
                                "enum": [
                                    "lines",
                                    "markers",
                                    "text",
                                    "lines+markers",
                                    "markers+text",
                                    "lines+text",
                                    "lines+markers+text",
                                    "none",
                                    "group"
                                ]
                            }
                        }
                    }
                },
                "layout": {
                    "title": "Graph layout",
                    "description": "Determines how the graph looks",
                    "type": "object",
                    "properties": {
                        "height": {
                            "type": "number",
                            "minimum": 10
                        },
                        "width": {
                            "type": "number",
                            "minimum": 10
                        },
                        "xaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "yaxis": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "automargin": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "hovermode": {
                            "type": "string",
                            "enum": [
                                "x",
                                "y",
                                "closest",
                                "false",
                                "x unified",
                                "y unified"
                            ]
                        }
                    }
                }
            }
        }
    },
    "visualization_schema": {
        "type": "object",
        "title": "Visualization List",
        "description": "modifications to the existing graph",
        "additionalProperties": false,
        "properties": {
            "hover_data": {
                "type": "object",
                "title": "Hover data",
                "description": "data shown on hover over by mouse",
                "required": [
                    "column"
                ],
                "properties": {
                    "column": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "penguin_size:study_name",
                                "penguin_size:species",
                                "penguin_size:island",
                                "penguin_size:sex",
                                "penguin_size:region",
                                "penguin_size:culmen_depth_mm",
                                "penguin_size:culmen_length_mm",
                                "penguin_size:flipper_length_mm",
                                "penguin_size:body_mass_g",
                                "mean_penguin_stat:study_name",
                                "mean_penguin_stat:species",
                                "mean_penguin_stat:sex",
                                "mean_penguin_stat:culmen_length",
                                "mean_penguin_stat:culmen_depth",
                                "mean_penguin_stat:flipper_length",
                                "mean_penguin_stat:body_mass",
                                "mean_penguin_stat:delta_15_n",
                                "mean_penguin_stat:delta_13_c",
                                "penguin_size_small:species",
                                "penguin_size_small:island",
                                "penguin_size_small:culmen_length_mm",
                                "penguin_size_small:culmen_depth_mm",
                                "penguin_size_small:flipper_length_mm",
                                "penguin_size_small:body_mass_g",
                                "penguin_size_small:sex"
                            ]
                        }
                    }
                }
            },
            "groupby": {
                "type": "object",
                "title": "Group by",
                "description": "Grouping of the data see https://plotly.com/javascript/group-by/",
                "required": [
                    "column"
                ],
                "properties": {
                    "column": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "penguin_size:study_name",
                                "penguin_size:species",
                                "penguin_size:island",
                                "penguin_size:sex",
                                "penguin_size:region",
                                "penguin_size:culmen_depth_mm",
                                "penguin_size:culmen_length_mm",
                                "penguin_size:flipper_length_mm",
                                "penguin_size:body_mass_g",
                                "mean_penguin_stat:study_name",
                                "mean_penguin_stat:species",
                                "mean_penguin_stat:sex",
                                "mean_penguin_stat:culmen_length",
                                "mean_penguin_stat:culmen_depth",
                                "mean_penguin_stat:flipper_length",
                                "mean_penguin_stat:body_mass",
                                "mean_penguin_stat:delta_15_n",
                                "mean_penguin_stat:delta_13_c",
                                "penguin_size_small:species",
                                "penguin_size_small:island",
                                "penguin_size_small:culmen_length_mm",
                                "penguin_size_small:culmen_depth_mm",
                                "penguin_size_small:flipper_length_mm",
                                "penguin_size_small:body_mass_g",
                                "penguin_size_small:sex"
                            ]
                        }
                    },
                    "styles": {
                        "type": "object"
                    }
                }
            },
            "aggregate": {
                "type": "object",
                "title": "Aggregate",
                "description": "see https://plotly.com/javascript/aggregations/",
                "required": [
                    "column"
                ],
                "properties": {
                    "column": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "penguin_size:study_name",
                                "penguin_size:species",
                                "penguin_size:island",
                                "penguin_size:sex",
                                "penguin_size:region",
                                "penguin_size:culmen_depth_mm",
                                "penguin_size:culmen_length_mm",
                                "penguin_size:flipper_length_mm",
                                "penguin_size:body_mass_g",
                                "mean_penguin_stat:study_name",
                                "mean_penguin_stat:species",
                                "mean_penguin_stat:sex",
                                "mean_penguin_stat:culmen_length",
                                "mean_penguin_stat:culmen_depth",
                                "mean_penguin_stat:flipper_length",
                                "mean_penguin_stat:body_mass",
                                "mean_penguin_stat:delta_15_n",
                                "mean_penguin_stat:delta_13_c",
                                "penguin_size_small:species",
                                "penguin_size_small:island",
                                "penguin_size_small:culmen_length_mm",
                                "penguin_size_small:culmen_depth_mm",
                                "penguin_size_small:flipper_length_mm",
                                "penguin_size_small:body_mass_g",
                                "penguin_size_small:sex"
                            ]
                        }
                    },
                    "aggregations": {
                        "type": "object",
                        "description": "axis to function on the data e.g. x:avg",
                        "patternProperties": {
                            "^[a-zA-Z]$": {
                                "type": "string",
                                "description": "function on the data",
                                "enum": [
                                    "avg",
                                    "sum",
                                    "min",
                                    "max",
                                    "mode",
                                    "median",
                                    "count",
                                    "stddev",
                                    "first",
                                    "last"
                                ]
                            }
                        }
                    }
                }
            }
        }
    },
    "selector_schema": {
        "type": "object",
        "title": "Selector List",
        "description": "dictionary of data selectors for a graphic",
        "additionalProperties": false,
        "properties": {
            "filter": {
                "type": "array",
                "title": "Filter",
                "description": "a filter operation based on label",
                "items": {
                    "type": "object",
                    "required": [
                        "column"
                    ],
                    "additionalProperties": false,
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "name in table",
                            "enum": [
                                "penguin_size:study_name",
                                "penguin_size:species",
                                "penguin_size:island",
                                "penguin_size:sex",
                                "penguin_size:region",
                                "penguin_size:culmen_depth_mm",
                                "penguin_size:culmen_length_mm",
                                "penguin_size:flipper_length_mm",
                                "penguin_size:body_mass_g",
                                "mean_penguin_stat:study_name",
                                "mean_penguin_stat:species",
                                "mean_penguin_stat:sex",
                                "mean_penguin_stat:culmen_length",
                                "mean_penguin_stat:culmen_depth",
                                "mean_penguin_stat:flipper_length",
                                "mean_penguin_stat:body_mass",
                                "mean_penguin_stat:delta_15_n",
                                "mean_penguin_stat:delta_13_c",
                                "penguin_size_small:species",
                                "penguin_size_small:island",
                                "penguin_size_small:culmen_length_mm",
                                "penguin_size_small:culmen_depth_mm",
                                "penguin_size_small:flipper_length_mm",
                                "penguin_size_small:body_mass_g",
                                "penguin_size_small:sex"
                            ]
                        },
                        "multiple": {
                            "type": "boolean"
                        },
                        "default_selected": {
                            "type": "array",
                            "description": "default filter, list of column values",
                            "items": {
                                "type": "string"
                            }
                        },
                        "unfiltered_selector": {
                            "type": "boolean"
                        }
                    }
                }
            },
            "numerical_filter": {
                "type": "array",
                "title": "Numerical Filter",
                "description": "a filter operation on numerical data",
                "items": {
                    "type": "object",
                    "required": [
                        "column"
                    ],
                    "additionalProperties": false,
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "name in table",
                            "enum": [
                                "penguin_size:study_name",
                                "penguin_size:species",
                                "penguin_size:island",
                                "penguin_size:sex",
                                "penguin_size:region",
                                "penguin_size:culmen_depth_mm",
                                "penguin_size:culmen_length_mm",
                                "penguin_size:flipper_length_mm",
                                "penguin_size:body_mass_g",
                                "mean_penguin_stat:study_name",
                                "mean_penguin_stat:species",
                                "mean_penguin_stat:sex",
                                "mean_penguin_stat:culmen_length",
                                "mean_penguin_stat:culmen_depth",
                                "mean_penguin_stat:flipper_length",
                                "mean_penguin_stat:body_mass",
                                "mean_penguin_stat:delta_15_n",
                                "mean_penguin_stat:delta_13_c",
                                "penguin_size_small:species",
                                "penguin_size_small:island",
                                "penguin_size_small:culmen_length_mm",
                                "penguin_size_small:culmen_depth_mm",
                                "penguin_size_small:flipper_length_mm",
                                "penguin_size_small:body_mass_g",
                                "penguin_size_small:sex"
                            ]
                        }
                    }
                }
            },
            "axis": {
                "type": "array",
                "title": "Axis Selector",
                "description": "change what column data is shown on a axis",
                "items": {
                    "type": "object",
                    "required": [
                        "column",
                        "entries"
                    ],
                    "additionalProperties": false,
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "axis name",
                            "pattern": "^[a-zA-Z]$"
                        },
                        "entries": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "penguin_size:study_name",
                                    "penguin_size:species",
                                    "penguin_size:island",
                                    "penguin_size:sex",
                                    "penguin_size:region",
                                    "penguin_size:culmen_depth_mm",
                                    "penguin_size:culmen_length_mm",
                                    "penguin_size:flipper_length_mm",
                                    "penguin_size:body_mass_g",
                                    "mean_penguin_stat:study_name",
                                    "mean_penguin_stat:species",
                                    "mean_penguin_stat:sex",
                                    "mean_penguin_stat:culmen_length",
                                    "mean_penguin_stat:culmen_depth",
                                    "mean_penguin_stat:flipper_length",
                                    "mean_penguin_stat:body_mass",
                                    "mean_penguin_stat:delta_15_n",
                                    "mean_penguin_stat:delta_13_c",
                                    "penguin_size_small:species",
                                    "penguin_size_small:island",
                                    "penguin_size_small:culmen_length_mm",
                                    "penguin_size_small:culmen_depth_mm",
                                    "penguin_size_small:flipper_length_mm",
                                    "penguin_size_small:body_mass_g",
                                    "penguin_size_small:sex"
                                ]
                            }
                        }
                    }
                }
            },
            "groupby": {
                "type": "object",
                "title": "Group By Selector",
                "required": [
                    "entries"
                ],
                "additionalProperties": false,
                "properties": {
                    "entries": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "penguin_size:study_name",
                                "penguin_size:species",
                                "penguin_size:island",
                                "penguin_size:sex",
                                "penguin_size:region",
                                "penguin_size:culmen_depth_mm",
                                "penguin_size:culmen_length_mm",
                                "penguin_size:flipper_length_mm",
                                "penguin_size:body_mass_g",
                                "mean_penguin_stat:study_name",
                                "mean_penguin_stat:species",
                                "mean_penguin_stat:sex",
                                "mean_penguin_stat:culmen_length",
                                "mean_penguin_stat:culmen_depth",
                                "mean_penguin_stat:flipper_length",
                                "mean_penguin_stat:body_mass",
                                "mean_penguin_stat:delta_15_n",
                                "mean_penguin_stat:delta_13_c",
                                "penguin_size_small:species",
                                "penguin_size_small:island",
                                "penguin_size_small:culmen_length_mm",
                                "penguin_size_small:culmen_depth_mm",
                                "penguin_size_small:flipper_length_mm",
                                "penguin_size_small:body_mass_g",
                                "penguin_size_small:sex"
                            ]
                        }
                    },
                    "multiple": {
                        "type": "boolean"
                    },
                    "default_selected": {
                        "type": "array",
                        "description": "default filter, list of column values",
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
};
return dict_of_schemas
}