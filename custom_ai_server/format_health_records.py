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
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            symptoms = row.get('patient_symptoms', '')
            diagnosis = row.get('diagnosis', '')
            treatment = row.get('treatment', '')
            
            # Skip empty rows
            if not symptoms:
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
