import csv

fasta_file = "test_sequences_gene.fa"
output_csv_file = "test_sequence.csv"


def parse_fasta(fname):
    with open(fname, "r") as fh:

        # Create variables for storing the identifiers and the sequence.
        identifier = None
        sequence = []

        for line in fh:
            line = line.strip()  # Remove trailing newline characters.
            if line.startswith(">"):
                if identifier is None:
                    # This only happens when the first line of the
                    # FASTA file is parsed.
                    identifier = line
                else:
                    # This happens every time a new FASTA record is
                    # encountered.

                    # Start by yielding the entry that has been built up.
                    yield identifier, ''.join(sequence)

                    # Then reinitialize the identifier and sequence
                    # variables to build up a new record.
                    identifier = line
                    sequence = []
            else:
                # This happens every time a sequence line is encountered.
                sequence.append(line)

        # Yield the last entry after the loop ends.
        if identifier is not None:
            yield identifier, ''.join(sequence)

# Write entries to CSV file
with open(output_csv_file, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Identifier', 'Sequence'])  # Write header
    for entry in parse_fasta(fasta_file):
        csv_writer.writerow(entry)