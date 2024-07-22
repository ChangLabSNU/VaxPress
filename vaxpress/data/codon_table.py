STOP_CODON = '*'

standard_forward_table = {
  'UUU': 'F', 'UUC': 'F', 'UUA': 'L', 'UUG': 'L', 'UCU': 'S', 'UCC': 'S',
  'UCA': 'S', 'UCG': 'S', 'UAU': 'Y', 'UAC': 'Y', 'UGU': 'C', 'UGC': 'C',
  'UGG': 'W', 'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L', 'CCU': 'P',
  'CCC': 'P', 'CCA': 'P', 'CCG': 'P', 'CAU': 'H', 'CAC': 'H', 'CAA': 'Q',
  'CAG': 'Q', 'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R', 'AUU': 'I',
  'AUC': 'I', 'AUA': 'I', 'AUG': 'M', 'ACU': 'T', 'ACC': 'T', 'ACA': 'T',
  'ACG': 'T', 'AAU': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K', 'AGU': 'S',
  'AGC': 'S', 'AGA': 'R', 'AGG': 'R', 'GUU': 'V', 'GUC': 'V', 'GUA': 'V',
  'GUG': 'V', 'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A', 'GAU': 'D',
  'GAC': 'D', 'GAA': 'E', 'GAG': 'E', 'GGU': 'G', 'GGC': 'G', 'GGA': 'G',
  'GGG': 'G', 'UGA': STOP_CODON, 'UAG': STOP_CODON, 'UAA': STOP_CODON,
}

standard_backward_table = {
  'A': ['GCU', 'GCC', 'GCA', 'GCG'],
  'C': ['UGU', 'UGC'],
  'D': ['GAU', 'GAC'],
  'E': ['GAA', 'GAG'],
  'F': ['UUU', 'UUC'],
  'G': ['GGU', 'GGC', 'GGA', 'GGG'],
  'H': ['CAU', 'CAC'],
  'I': ['AUU', 'AUC', 'AUA'],
  'K': ['AAA', 'AAG'],
  'L': ['UUA', 'UUG', 'CUU', 'CUC', 'CUA', 'CUG'],
  'M': ['AUG'],
  'N': ['AAU', 'AAC'],
  'P': ['CCU', 'CCC', 'CCA', 'CCG'],
  'Q': ['CAA', 'CAG'],
  'R': ['CGU', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
  'S': ['UCU', 'UCC', 'UCA', 'UCG', 'AGU', 'AGC'],
  'T': ['ACU', 'ACC', 'ACA', 'ACG'],
  'V': ['GUU', 'GUC', 'GUA', 'GUG'],
  'W': ['UGG'],
  'Y': ['UAU', 'UAC'],
  STOP_CODON: ['UAA', 'UAG', 'UGA'],
}

forward_table = {
  'Homo sapiens': standard_forward_table,
}

backward_table ={
  'Homo sapiens': standard_backward_table,
}