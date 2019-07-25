from copy import copy
import json

file_names = {
    "shap_gbc_importances.json": {'method': 'shap', 'metric': 'general',},
    "shap_gbc_importances_heldout.json": {'method': 'shap', 'metric': 'heldout',},
    "bba_gbc_importances.json": {'method': 'bba', 'metric': 'general',},
    "bba_gbc_importances_heldout.json": {'method': 'bba', 'metric': 'heldout', },

}

paired_filenames_to_combine = {
    "bba_feature_importance_combined.json": ("bba_gbc_importances.json", "bba_gbc_importances_heldout.json"),
    "shap_feature_importance_combined.json": ("shap_gbc_importances.json", "shap_gbc_importances_heldout.json")

}


if __name__ == '__main__':
    for file_name in copy(list(file_names.keys())):
        with open(file_name, 'r') as fin:
            j_ = json.load(fin)
        edited_json = copy(j_)

        ### EDITS TO CORRECT FILE FORMATTING
        if file_name == "shap_gbc_importances_heldout.json":
            edited_json['method'] = 'shap'

        # these structs are flipped in order between files
        if file_name == "bba_gbc_importances_heldout.json":
            for chem, chem_struct in j_["chem_heldout"].items():
                edited_json["chem_heldout"][chem] = {'rank': chem_struct[1], 'value': chem_struct[0]}
        if file_name == "shap_gbc_importances_heldout.json":
            for chem, chem_struct in j_["chem_heldout"].items():
                edited_json["chem_heldout"][chem] = {'rank': chem_struct[1], 'value': chem_struct[0]}


        file_names[file_name]['json'] = edited_json

    for combined_filename, pair in paired_filenames_to_combine.items():
        json_1 = file_names[pair[0]]['json']
        json_2 = file_names[pair[1]]['json']
        combined_json = json_1
        # todo: this is a lie
        combined_json['crank'] = '0038'
        # add the heldout chem data key/value pair to the other all_chem dict.
        combined_json["chem_heldout"] = json_2["chem_heldout"]
        with open(combined_filename, 'w') as fout:
            json.dump(combined_json, fout, indent=4)


