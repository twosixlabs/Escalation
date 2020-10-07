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


function edit_graphic(page_id,graphic,graphic_status) {
    //This allows the web page to focus where the plot was updated instead of starting at the top of the web page
    let graphic_form=$('#form_button_click');
    graphic_form[0].page_id.value=page_id;
    graphic_form[0].graphic.value=graphic;
    graphic_form[0].graphic_status.value=graphic_status;
    graphic_form.submit();
}

function modify_config(modification, page_id=-1,graphic=''){
    let graphic_form=$('#form_button_click');
    let add_page_form = $('#form_add_page');
    let name = document.getElementById("webpage_label_".concat(page_id)).value;
    if ((!modification.includes('delete') || confirm('Confirm deletion')) && ((modification!='add_page' && modification!='rename_page') || name)) {
        add_page_form[0].page_id.value = page_id;
        add_page_form[0].graphic.value = graphic;
        add_page_form[0].modification.value = modification;
        add_page_form[0].title.value = graphic_form[0].title.value;
        add_page_form[0].brief_desc.value = graphic_form[0].brief_desc.value;
        add_page_form[0].data_backend.value = graphic_form[0].data_backend.value;
        add_page_form[0].webpage_label.value = name;
        add_page_form.submit();
    }
}

function get_main_data_sources(data_source_dict){
    let data_sources = new Set();
    data_sources.add(data_source_dict['main_data_source']['data_source_type']);
    let additional_data_source;
    if ('additional_data_sources' in data_source_dict) {
        for (additional_data_source of data_source_dict['additional_data_sources']) {
            data_sources.add(additional_data_source['data_source_type'])
        }
    }
    return data_sources
}

function any_identifiers_active(data_source) {
    let web_form=$('#form_'.concat(data_source));
    const table_data=$(`#table_${data_source}`).bootstrapTable('getData')
    let flag=0;
    function active_table_data_to_form(dict) {
        web_form[0][dict['upload_id']].value=(dict['active'] ? 'active' : 'inactive');
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