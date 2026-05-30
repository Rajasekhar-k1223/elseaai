import json
import csv
import os
import argparse

def format_csv_to_jsonl(input_csv, output_jsonl):
    """
    Converts a CSV of health records into the conversational JSONL format required for fine-tuning.
    Expected CSV columns: 'patient_symptoms', 'diagnosis', 'treatment'
    """
    if not os.path.exists(input_csv):
        print(f"Error: Could not find {input_csv}")
        return
        
    formatted_data = []
    
    with open(input_csv, mode='r', encoding='utf-8') as csv_file:
        # Read the first line to analyze headers
        reader = csv.reader(csv_file)
        headers = next(reader, None)
        if not headers:
            print(f"Error: {input_csv} is empty.")
            return
            
        # Helper to find column matching aliases
        def find_column(headers, aliases):
            for alias in aliases:
                for header in headers:
                    h_norm = header.lower().strip().replace('_', ' ').replace('-', ' ')
                    a_norm = alias.lower().strip().replace('_', ' ').replace('-', ' ')
                    if h_norm == a_norm:
                        return header
            return None

        # Robust mapping
        symptoms_col = find_column(headers, ['patient_symptoms', 'patient symptoms', 'symptoms', 'symptom', 'description', 'patient_presentation', 'symptom_description'])
        diagnosis_col = find_column(headers, ['diagnosis', 'potential_diagnosis', 'potential diagnosis', 'disease', 'condition', 'assessment'])
        treatment_col = find_column(headers, ['treatment', 'treatment_plan', 'treatment plan', 'recommended_treatment', 'recommended treatment', 'recommendation', 'recommendations', 'plan'])

        # Fallbacks if columns are not perfectly matched
        if not symptoms_col or not diagnosis_col or not treatment_col:
            print(f"Note: Some columns did not map exactly. Attempting auto-detection among headers: {headers}")
            symptoms_col = symptoms_col or (headers[0] if len(headers) > 0 else 'patient_symptoms')
            diagnosis_col = diagnosis_col or (headers[1] if len(headers) > 1 else 'diagnosis')
            treatment_col = treatment_col or (headers[2] if len(headers) > 2 else 'treatment')
        
        print(f"Auto-mapped CSV columns:\n - Symptoms: '{symptoms_col}'\n - Diagnosis: '{diagnosis_col}'\n - Treatment: '{treatment_col}'\n")

        # Rewind and parse rows
        csv_file.seek(0)
        dict_reader = csv.DictReader(csv_file)
        
        for row in dict_reader:
            symptoms = row.get(symptoms_col, '')
            diagnosis = row.get(diagnosis_col, '')
            treatment = row.get(treatment_col, '')
            
            # Skip empty rows
            if not symptoms or not symptoms.strip():
                continue
                
            # Create a conversational interaction for the AI to learn
            conversation = {
                "messages": [
                    {"role": "system", "content": "You are a highly capable medical AI assistant trained on proprietary health records. Provide accurate diagnostic insights and treatment recommendations based on patient symptoms."},
                    {"role": "user", "content": f"Patient presents with the following symptoms and history:\n{symptoms}\n\nWhat is the potential diagnosis and recommended treatment?"},
                    {"role": "assistant", "content": f"Based on the provided health record, the potential diagnosis is:\n{diagnosis}\n\nRecommended Treatment Plan:\n{treatment}"}
                ]
            }
            formatted_data.append(conversation)
            
    # Write to JSONL
    with open(output_jsonl, 'w', encoding='utf-8') as jsonl_file:
        for item in formatted_data:
            jsonl_file.write(json.dumps(item) + '\n')
            
    print(f"Successfully converted {len(formatted_data)} records to {output_jsonl}!")
    print("This file is now ready for fine-tuning with MLX or Unsloth.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format Medical Records for AI Fine-Tuning")
    parser.add_argument("--input", default="health_records.csv", help="Input CSV file containing medical records")
    parser.add_argument("--output", default="training_data.jsonl", help="Output JSONL file for fine-tuning")
    
    args = parser.parse_args()
    format_csv_to_jsonl(args.input, args.output)
