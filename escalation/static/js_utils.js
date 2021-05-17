// Copyright [2020] [Two Six Labs, LLC]
// Licensed under the Apache License, Version 2.0

function post_to_server(id_on_web_page) {
    //This allows the web page to focus where the plot was updated instead of starting at the top of the web page
    let web_form=$('#form_'.concat(id_on_web_page));
    web_form.attr('action','#'.concat(id_on_web_page));
    web_form.submit();
}

function reset_form(id_on_web_page) {
    //This allows the web page to focus where the plot was updated instead of starting at the top of the web page
    $('#form_'.concat(id_on_web_page))[0].process.value='';
    post_to_server(id_on_web_page);

}

function show_all_row_handler(selector_id, exclusive_value) {
    let selector = $("#".concat(selector_id));
    const selected_elements = selector.val();
    if (selected_elements.length==0){
        selector.val(exclusive_value);
        selector.attr('data-top_selected',true)
    }
    else if (selector.attr('data-top_selected')=="true"){
        // If something is selected along with show all rows
        // Pop the show all rows item out using shift, then set elements to remaining
        selected_elements.shift();
        selector.val(selected_elements);
        selector.attr('data-top_selected',false)
    }
    else if (selected_elements.includes(exclusive_value)){
        // If the user has selected show all rows, deselect everything else
        selector.selectpicker('deselectAll');
        selector.val(exclusive_value);
        selector.attr('data-top_selected',true)
    }
    selector.selectpicker('refresh');
}


function edit_graphic(page_id,graphic,graphic_status,post_url) {
    //This allows the web page to focus where the plot was updated instead of starting at the top of the web page
    let graphic_form=$('#form_button_click');

    graphic_form[0].page_id.value=page_id;
    graphic_form[0].graphic.value=graphic;
    graphic_form[0].graphic_status.value=graphic_status;
    graphic_form.attr('action', post_url);
    graphic_form.submit();
}

function modify_config(modification, page_id=-1,graphic=''){
    let graphic_form=$('#form_button_click');
    let add_page_form = $('#form_add_page');
    let input_box = document.getElementById("webpage_label_".concat(page_id.toString()))
    let name = input_box.value;
    if ((!modification.includes('delete') || confirm('Confirm deletion'))
        && ((modification!='add_page' && modification!='rename_page') || name)) {
        add_page_form[0].page_id.value = page_id;
        add_page_form[0].graphic.value = graphic;
        add_page_form[0].modification.value = modification;
        add_page_form[0].title.value = graphic_form[0].title.value;
        add_page_form[0].brief_desc.value = graphic_form[0].brief_desc.value;
        add_page_form[0].webpage_label.value = name;
        add_page_form.submit();
    }
    else if((modification=='add_page' || modification=='rename_page') && !name){
        input_box.classList.add("is-invalid");
    }
}

function get_main_data_sources(data_source_dict){
    let data_sources = [];
    data_sources.push(data_source_dict['main_data_source']['data_source_type']);
    let additional_data_source;
    if ('additional_data_sources' in data_source_dict) {
        for (additional_data_source of data_source_dict['additional_data_sources']) {
            data_sources.push(additional_data_source['data_source_type'])
        }
    }
    return data_sources
}

function check_duplicate_data_sources(data_source_dict){
    let data_sources = new Set();
    data_sources.add(data_source_dict['main_data_source']['data_source_type']);
    let additional_data_source;
    let data_source;
    if ('additional_data_sources' in data_source_dict) {
        for (additional_data_source of data_source_dict['additional_data_sources']) {
            data_source=additional_data_source['data_source_type'];
            if (data_sources.has(data_source)){
                return true
            }else{
                data_sources.add(data_source)
            }

        }
    }
    return false
}

function any_identifiers_active(data_source) {
    let web_form=$('#form_'.concat(data_source));
    const table_data=$(`#table_${data_source}`).bootstrapTable('getData')
    let flag=0;
    function active_table_data_to_form(dict) {
        web_form[0]["id_".concat(dict['upload_id'])].value=(dict['active'] ? 'active' : 'inactive');
      if (dict['active']){
          flag=1
      }
    }
    table_data.forEach(active_table_data_to_form)
    if (flag){
        web_form.attr('action','#'.concat(data_source));
        web_form.submit()
    }
    else{
       alert('At least one identifier needs to be selected');
    }
}

function toggle_rename_page(page_id) {
    let page_div = document.getElementById("page_".concat(page_id));
    let rename_page_div = document.getElementById("rename_page_".concat(page_id));
    if (page_div.style.display === "none") {
        page_div.style.display = "block";
        rename_page_div.style.display = "none";
    } else {
        page_div.style.display = "none";
        rename_page_div.style.display = "block";
    }
}


function get_collapse_dict(editors) {
    let collapse_dict= new Object();
    collapse_dict['additional_data_sources'] =  editors['graphic_meta_info'].getEditor('root.data_sources.additional_data_sources').collapsed
    collapse_dict['hover_data'] = editors['visualization'].getEditor('root.hover_data').collapsed
    collapse_dict['groupby'] =  editors['visualization'].getEditor('root.groupby').collapsed
    collapse_dict['aggregate'] = editors['visualization'].getEditor('root.aggregate').collapsed
    collapse_dict['filter'] = editors['selector'].getEditor('root.filter').collapsed
    collapse_dict['numerical_filter'] = editors['selector'].getEditor('root.numerical_filter').collapsed
    collapse_dict['axis'] = editors['selector'].getEditor('root.axis').collapsed
    collapse_dict['groupby_selector'] = editors['selector'].getEditor('root.groupby').collapsed
    collapse_dict['visualization_options'] = editors['visualization'].getEditor('root').collapsed
    collapse_dict['selectable_data_dict'] = editors['selector'].getEditor('root').collapsed
    return collapse_dict
}

function find_word_in_dict(word_list,found_word,dict,key){
    let check_all_true = arr => arr.every(Boolean);
    //Performs a depth first search to match word
    // output is the path delimited by '.'

    const DESCRIPTION = "description";
    const PROPERTIES = "properties";
    const ITEMS = "items";
    let stack = [];
    const name=key;
    const dict_type = dict["type"];
    let any_word = false;

    word_list.forEach(function(word,i){
        if (key.toLowerCase().includes(word.toLowerCase())){
        found_word[i] = true;
        any_word = true;
    }
    });
    // More useful results if we only pass down whether the ancestors had words in name not descriptions
    let found_word_copy=found_word;
    if (dict.hasOwnProperty(DESCRIPTION)) {
        word_list.forEach(function (word, i) {
            if (dict[DESCRIPTION].toLowerCase().includes(word.toLowerCase())){
                found_word_copy[i] = true;
                any_word = true;
            }
        });
    }
    // This is a better order for display
    if (any_word && check_all_true(found_word_copy)){
        stack.push(name);
    }

    if (dict_type === "object"){
        for (const new_key in dict[PROPERTIES]){
            find_word_in_dict(word_list,[...found_word],dict[PROPERTIES][new_key],new_key).forEach(function(suffix){
                stack.push(name + "." + PROPERTIES + "." + suffix)

            });
        }
    }else if(dict_type === "array"){
        find_word_in_dict(word_list,[...found_word],dict[ITEMS],ITEMS).forEach(function(suffix){
            stack.push(name + "." + suffix)
        });
    }

    return stack
}

function json_editor_path(path,dict){
    // Replaces keys in the config path with 'title' to match what the user sees in the editor
    const PROPERTIES = "properties";
    const TITLE = "title";
    let path_list = path.split(".")
    for (let index = 0; index < path_list.length; index++) {
        const field=path_list[index]
        if (index) {
            dict = dict[field];
        }

        if (field !== PROPERTIES && dict.hasOwnProperty(TITLE)){
            path_list[index]=dict[TITLE]
        }
    }
    //Performs a depth first search to match word
    // output is the path
    return path_list.join(".")
}

function get_description(path,dict){
    // given a path gets the relevant fields to show to the user
    const fields_to_display = [
        "title",
        "type",
        "pattern",
        "enum",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "minItems",
        "maxItems",
        "required",
        "default",
        "description",
        "examples"
    ]

    const getNestedObject = (pathArr,nestedObj) => {
    return pathArr.reduce((obj, key) =>
        (obj && obj[key] !== 'undefined') ? obj[key] : undefined, nestedObj);
    };
    const fields=getNestedObject(path.split(".").slice(1),dict);
    let field_list = [];
    fields_to_display.forEach(function(field) {
        if (fields.hasOwnProperty(field)){
            field_list.push(field+": "+String(fields[field]))
        }
    });
    return field_list.join("<br>")
}

 function new_editor(type,display_required_only,schema) {
    return new JSONEditor(document.getElementById('editor_holder_'.concat(type)),
        options={theme: 'bootstrap4',display_required_only: display_required_only, disable_edit_json:true,
            disable_array_delete_last_row:true, iconlib: 'fontawesome5', show_errors:'always' ,schema: schema });
}

