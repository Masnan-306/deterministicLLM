import csv
import json
import argparse

def read_tsv(file_path):
    """Reads a TSV file and returns a list of rows."""
    with open(file_path, 'r') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        return list(reader)

def compare_tsv(file1, file2):
    """Compares two TSV files and prints the differences."""
    data1 = read_tsv(file1)
    data2 = read_tsv(file2)

    if len(data1) != len(data2):
        print(f"Files have different number of rows: {len(data1)} vs {len(data2)}")
        return

    differences = []
    for i, (row1, row2) in enumerate(zip(data1, data2)):
        if row1 != row2:
            try:
                # Attempt to decode JSON strings for better comparison
                decoded_row1 = [json.loads(cell) if i > 0 else cell for i, cell in enumerate(row1)]
                decoded_row2 = [json.loads(cell) if i > 0 else cell for i, cell in enumerate(row2)]
                if decoded_row1 != decoded_row2:
                    differences.append((i + 1, row1, row2))
            except json.JSONDecodeError:
                # If decoding fails, compare raw rows
                differences.append((i + 1, row1, row2))

    if not differences:
        print("The TSV files are identical.")
    else:
        print(f"Found {len(differences)} differences:")
        for diff in differences:
            row_number, row1, row2 = diff
            print(f"\nDifference in row {row_number}:")
            print(f"File 1: {row1}")
            print(f"File 2: {row2}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Compare two TSV files for differences.")
    parser.add_argument('file1', type=str, help="Path to the first TSV file.")
    parser.add_argument('file2', type=str, help="Path to the second TSV file.")
    args = parser.parse_args()

    # Compare the TSV files
    compare_tsv(args.file1, args.file2)

if __name__ == "__main__":
    main()