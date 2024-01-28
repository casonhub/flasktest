from flask import Flask, render_template, request, jsonify
import pandas as pd
from itertools import combinations

app = Flask(__name__)

# JSON object with sample data sets
data_sets = {
    'ADHD': [],
    'ASD': [],
    'Alzheimer': [],
    'Bipolar Disorder': [],
    
    # Add more options and data sets as needed
}

def read_biomarkers(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path, index_col=0)
    return df

def is_combination_unique(combination, disorder, df):
    # Check if the combination of biomarkers is unique to the disorder
    for other_disorder in df.columns:
        if other_disorder != disorder:
            if all(df.loc[biomarker, other_disorder] == df.loc[biomarker, disorder] for biomarker in combination):
                return False
    return True

def get_unique_combinations(df, disorder):
    # Get all biomarkers associated with the specified disorder
    associated_biomarkers = df.index[df[disorder].notnull()].tolist()

    # Generate all possible combinations of these biomarkers
    unique_combinations = []
    for r in range(len(associated_biomarkers), 0, -1):
        for combination in combinations(associated_biomarkers, r):
            if is_combination_unique(combination, disorder, df):
                unique_combinations.append(combination)
                if len(unique_combinations) >= 100:  # Stop if 100 unique combinations are found
                    return unique_combinations[:100]

    return unique_combinations

@app.route('/')
def index():
    options = list(data_sets.keys())
    return render_template('index.html', options=options)

@app.route('/get_data', methods=['POST'])
def get_data():

    file_path = "D:\Python\data\\biomarkers.xlsx"
    df = read_biomarkers(file_path)

    while True:
        disorder = request.form.get('selected_option') #input("Enter the mental disorder (or type 'done' to exit): ").strip()
        if disorder.lower() == 'done':
            break

        if disorder not in df.columns:
            print("Disorder not found in the file. Please try again.")
            continue

        unique_combinations = get_unique_combinations(df, disorder)

        selected_option = request.form.get('selected_option')
        selected_data = []

        if unique_combinations:
                #print(f"Top 100 unique sets of biomarkers for {disorder}:")
                for i, biomarkers in enumerate(unique_combinations, start=1):
                        selected_data.append(f"Set {i}: {','.join(biomarkers)}")
                        
                return jsonify({'success': True, 'data': selected_data})
                        #print(f"Set {i}: {', '.join(biomarkers)}")
        else:
                        print(f"No unique biomarkers found for {disorder}.")

    
    else:
        return jsonify({'success': False, 'error': 'Invalid option'})

if __name__ == '__main__':
    app.run(debug=True)
