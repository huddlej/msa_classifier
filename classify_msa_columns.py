"""
Given a multiple sequence alignment, classify each column by the relative
contents of each row (e.g., all rows are equal, all rows are different, etc.)
and report the type of column per position.

This information can be used to resolve breakpoints between paralogous sequences
as reported in Antonacci and Dennis et al. 2014.
"""
import argparse
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
import csv


def enumerate_bases(bases):
    """
    Convert the given tuple of multiple sequence alignment bases (any
    characters) into a tuple of integers such that all rows with the same base
    share the same integer based on the order each base was seen.

    >>> enumerate_bases(("A", "A", "C", "C"))
    (0, 0, 1, 1)
    >>> enumerate_bases(("C", "C", "A", "A"))
    (0, 0, 1, 1)
    >>> enumerate_bases(("C", "-", "T", "C"))
    (0, 1, 2, 0)
    >>> enumerate_bases(("A", "C", "T", "G"))
    (0, 1, 2, 3)
    >>> enumerate_bases(("A", "A", "A", "A"))
    (0, 0, 0, 0)
    """
    current_index = 0
    base_to_index = {}
    integers = []
    for base in bases:
        if base not in base_to_index:
            base_to_index[base] = current_index
            current_index += 1

        integers.append(base_to_index[base])

    return tuple(integers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("alignment", help="Multiple sequence alignment input in FASTA format")
    parser.add_argument("classified_alignment_positions", help="Tab-delimited output file reporting alignment position, type of column per position, and column bases per position.")
    parser.add_argument("--types", nargs="*", help="Space-delimited list of column bases to report in the output table (e.g., '--types 000 001' reports positions where all rows have the same base and where the last row differs from the first two rows)")
    args = parser.parse_args()

    # If the user specified types to keep in the output, convert the shorthand
    # string of integers to a tuple of integer tuples.
    if args.types is not None and len(args.types) > 0:
        types = tuple([tuple(map(int, t)) for t in args.types])
    else:
        types = None

    # Load the multiple sequence alignment and sort records by name in ascending
    # order.
    original_alignment = AlignIO.read(args.alignment, "fasta")
    alignment = MultipleSeqAlignment(sorted([record for record in original_alignment], key=lambda record: record.name))

    index_by_column_type = {}
    current_index = 0

    with open(args.classified_alignment_positions, "w") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(("position", "column_type", "bases"))

        for i in xrange(alignment.get_alignment_length()):
            # First enumerate bases in the given column to determine the column's
            # "type" (e.g., all bases are the same, all bases are different, etc.).
            enumerated_bases = enumerate_bases([alignment[j][i] for j in xrange(len(alignment))])

            # Then enumerate this type of column in the context of the alignment
            # such that each column type gets its own integer that summarizes that
            # alignment position.
            if enumerated_bases not in index_by_column_type:
                index_by_column_type[enumerated_bases] = current_index
                current_index += 1

            if types is None or enumerated_bases in types:
                writer.writerow((i, index_by_column_type[enumerated_bases], enumerated_bases))
