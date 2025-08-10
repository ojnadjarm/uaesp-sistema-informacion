# ingesta/forms/upload.py
import json
import os
from django import forms
from globalfunctions.string_manager import get_string

# Load configuration from JSON files
def load_process_config():
    config = {}
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_structure')
    
    for subsecretaria in os.listdir(base_path):
        subsecretaria_path = os.path.join(base_path, subsecretaria)
        if os.path.isdir(subsecretaria_path):
            config[subsecretaria] = {
                'nombre': get_string(f'subsecretaria.{subsecretaria}', 'ingesta'),
                'procesos': {}
            }
            
            for file in os.listdir(subsecretaria_path):
                if file.endswith('.json'):
                    with open(os.path.join(subsecretaria_path, file), 'r') as f:
                        process_config = json.load(f)
                        config[subsecretaria]['procesos'].update(process_config)
    
    return config

PROCESO_DATA = load_process_config()

# Generate grouped choices for Process Types
def get_grouped_choices():
    choices = [('', get_string('forms.select_default', 'ingesta'))]
    for sub_key, sub_data in PROCESO_DATA.items():
        subsecretaria_name = sub_data['nombre']
        process_choices = []
        for proc_key, proc_data in sub_data.get('procesos', {}).items():
            process_choices.append((proc_key, proc_data.get('nombre', proc_key)))
        if process_choices:
            choices.append((subsecretaria_name, process_choices))
    return choices

def get_process_to_subsecretaria_map():
    mapping = {}
    for sub_key, sub_data in PROCESO_DATA.items():
        for proc_key in sub_data.get('procesos', {}).keys():
            mapping[proc_key] = sub_key
    return mapping

PROCESS_TO_SUBSECRETARIA = get_process_to_subsecretaria_map()

class UploadFileForm(forms.Form):
    tipo_proceso = forms.ChoiceField(
        label=get_string('forms.tipo_proceso_label', 'ingesta'),
        choices=get_grouped_choices(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )
    file = forms.FileField(
        label=get_string('forms.file_label', 'ingesta'),
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx'})
    )
