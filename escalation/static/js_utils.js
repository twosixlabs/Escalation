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
    if (modification!='add_page' || add_page_form[0].webpage_label.value) {
        add_page_form[0].page_id.value = page_id;
        add_page_form[0].graphic.value = graphic;
        add_page_form[0].modification.value = modification;
        add_page_form[0].title.value = graphic_form[0].title.value;
        add_page_form[0].brief_desc.value = graphic_form[0].brief_desc.value;
        add_page_form[0].data_backend.value = graphic_form[0].data_backend.value;
        add_page_form.submit();
    }
}

function send_json_in_post_request(url, data, webpage){
    let xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function () {
        let success_text = document.querySelector('#feedback_message');
        if (xhr.readyState === 4 && xhr.status === 200) {
            if (webpage) {window.location.href = webpage}
            success_text.innerHTML = "Applied"
        } else {
            success_text.innerHTML = "Failed"
        }
        // Message disappears after 5 secs
        setTimeout(function() {
              success_text.innerHTML="";
            }, 5000);
        };
    xhr.send(data);
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