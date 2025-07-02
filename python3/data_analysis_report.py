import csv
import statistics
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Data Analysis Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def analyze_data(filename):
    data = []
    headers = []
    
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        for row in csv_reader:
            data.append(row)
    
    df = pd.DataFrame(data, columns=headers)
    
    numeric_cols = []
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
            numeric_cols.append(col)
        except ValueError:
            pass
    
    analysis = {
        'columns': headers,
        'numeric_cols': numeric_cols,
        'row_count': len(data),
        'stats': {}
    }
    
    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            analysis['stats'][col] = {
                'mean': statistics.mean(col_data),
                'median': statistics.median(col_data),
                'stddev': statistics.stdev(col_data),
                'min': min(col_data),
                'max': max(col_data)
            }
    
    return analysis

def create_plots(analysis):
    plots = []
    
    for col in analysis['numeric_cols']:
        plt.figure()
        data = [float(v) for v in analysis['stats'][col].values()]
        plt.hist(data, bins=5, alpha=0.7, edgecolor='black')
        plt.title(f'Histogram of {col}')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        
        hist_file = os.path.abspath(f'hist_{col}.png')
        plt.savefig(hist_file)
        plt.close()
        
        if os.path.exists(hist_file):
            print(f"Histogram saved successfully: {hist_file}")
        else:
            print(f"Failed to save histogram: {hist_file}")
            continue
        
        plots.append({
            'type': 'histogram',
            'column': col,
            'file': hist_file
        })
        
    return plots

def generate_pdf(analysis, output_file='report.pdf'):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    
    pdf.cell(40, 10, f'Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    pdf.ln(15)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(40, 10, f'Dataset contains {analysis["row_count"]} rows and {len(analysis["columns"])} columns')
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Numeric Columns Analysis:', 0, 1)
    
    for col, stats in analysis['stats'].items():
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 7, col, 0, 0)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 9)
        for stat, value in stats.items():
            pdf.cell(30, 5, f'{stat.capitalize()}: {value:.2f}', 0, 0)
            pdf.ln(5)
        pdf.ln(5)
    
    pdf.output(output_file)
    print(f"Report successfully generated: {output_file}")

def main():
    print("Starting the report generation process...")
    input_file = 'sample_data.csv'
    
    try:
        print("Analyzing data...")
        analysis = analyze_data(input_file)
        
        print("Generating visualizations...")
        plots = create_plots(analysis)
        
        print("Creating PDF report...")
        generate_pdf(analysis)
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")

if __name__ == "__main__":
    main()
