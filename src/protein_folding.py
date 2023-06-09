# Modified code from : https://github.com/plotly/dash-bio/blob/master/dash_bio/utils/mol3dviewer_styles_creator.py
from dash_bio.utils import PdbParser
import pandas as pd
import matplotlib.colors as mcolors

pd.set_option('display.width', 900)
pd.set_option('display.max_columns', 200)
pd.set_option("display.max_rows", None)


ATOM_COLORS = {
    "C": "#c8c8c8",
    "H": "#ffffff",
    "N": "#8f8fff",
    "S": "#ffc832",
    "O": "#f00000",
    "F": "#ffff00",
    "P": "#ffa500",
    "K": "#42f4ee",
    "G": "#3f3f3f",
}

CHAIN_COLORS = {
    "A": "#320000",
    "B": "#8a2be2",
    "C": "#ff4500",
    "D": "#00bfff",
    "E": "#ff00ff",
    "F": "#ffff00",
    "G": "#4682b4",
    "H": "#ffb6c1",
    "I": "#a52aaa",
    "J": "#ee82ee",
    "K": "#75FF33",
    "L": "#FFBD33",
    "M": "#400040",
    "N": "#004000",
    "O": "#008080",
    "P": "#008080",
    "R": "#9c6677",
    "S": "#b7c5c8",
}

RESIDUE_COLORS = {
    "ALA": "#C8C8C8",
    "ARG": "#145AFF",
    "ASN": "#00DCDC",
    "ASP": "#E60A0A",
    "CYS": "#E6E600",
    "GLN": "#00DCDC",
    "GLU": "#E60A0A",
    "GLY": "#EBEBEB",
    "HIS": "#8282D2",
    "ILE": "#0F820F",
    "LEU": "#0F820F",
    "LYS": "#145AFF",
    "MET": "#E6E600",
    "PHE": "#3232AA",
    "PRO": "#DC9682",
    "SER": "#FA9600",
    "THR": "#FA9600",
    "TRP": "#B45AB4",
    "TYR": "#3232AA",
    "VAL": "#0F820F",
    "ASX": "#FF69B4",
    "GLX": "#FF69B4",
    "A": "#A0A0FF",
    "DA": "#A0A0FF",
    "G": "#FF7070",
    "DG": "#FF7070",
    "I": "#80FFFF",
    "C": "#FF8C4B",
    "DC": "#FF8C4B",
    "T": "#A0FFA0",
    "DT": "#A0FFA0",
    "U": "#FF8080",
}

RESIDUE_TYPE_COLORS = {
    "hydrophobic": "#00ff80",
    "polar": "#ff00bf",
    "acidic": "#ff4000",
    "basic": "#0040ff",
    "aromatic": "#ffff00",
    "purine": "#A00042",
    "pyrimidine": "#4F4600",
}

AMINO_ACID_CLASSES = {
    "hydrophobic": ["GLY", "ALA", "LEU", "ILE", "VAL", "MET", "PRO"],
    "polar": ["ASN", "GLN", "SER", "THR", "CYS"],
    "acidic": ["ASP", "GLU"],
    "basic": ["LYS", "ARG", "HIS"],
    "aromatic": ["TRP", "TYR", "PHE"],
    "purine": ["A", "G", "DA", "DG"],
    "pyrimidine": ["DT", "DC", "U", "I", "C"],
}


def create_style_3d(
    df,colname_score, atoms, visualization_type="stick", color_element="atom", color_scheme=None
):
    """Function to create styles input for Molecule3dViewer
    @param atoms
    A list of atoms. Each atom should be a dict with keys: 'name', 'residue_name', 'chain'
    @param visualization_type
    A type of molecule visualization graphic: 'stick' | 'cartoon' | 'sphere'.
    @param color_element
    Elements to apply color scheme to: 'atom' | 'residue' | 'residue_type' | 'chain'.
    @param color_scheme
    Color scheme used to style moleule elements.
    This should be a dict with keys being names of atoms, residues, residue types or chains,
    depending on the value of color_element argument. If no value is provided, default color
    schemes will be used.
    """

    if visualization_type not in ['stick', 'cartoon', 'sphere']:
        raise Exception("Invalid argument type: visualization_type.\
Should be: 'stick' | 'cartoon' | 'sphere'.")

    if color_element not in ['atom', 'residue', 'residue_type', 'chain', "residue_score"]:
        raise Exception("Invalid argument type: color_element.\
Should be: 'atom' | 'residue' | 'residue_type' | 'chain'| residue_score.")

    if not isinstance(atoms, list):
        raise Exception("Invalid argument type: atoms. Should be a list of dict.")

    if color_scheme and not isinstance(color_scheme, dict):
        raise Exception("Invalid argument type: color_scheme. Should be a dict.")

    default_color = '#ABABAB'

    if color_scheme is None:
        color_scheme = {
            'atom': ATOM_COLORS,
            'residue': RESIDUE_COLORS,
            'residue_type': RESIDUE_TYPE_COLORS,
            'residue_score': ATOM_COLORS,
            'chain': CHAIN_COLORS
        }[color_element]

    if color_element == 'residue_type':
        residue_type_colors_map = {}
        for aa_class_name, aa_class_members in AMINO_ACID_CLASSES.items():
            for aa in aa_class_members:
                print(aa)
                residue_type_colors_map[aa] = color_scheme.get(aa_class_name, default_color)
        color_scheme = residue_type_colors_map

    atom_styles = []

    # create gradient color depending on score
    # define a white to red gradient
    colors = ['#FFFFFF', '#93272C']
    cmap = mcolors.LinearSegmentedColormap.from_list('my_cmap', colors)
    # convert the normalized values to HEX codes and add a new column
    df['color'] = df[colname_score].apply(lambda x: mcolors.to_hex(cmap(x)))

    for a in atoms:
        if color_element == 'atom':
            atom_color = color_scheme.get(a['name'], default_color)
        if color_element in ['residue', 'residue_type']:
            atom_color = color_scheme.get(a['residue_name'], default_color)
        if color_element == 'chain':
            atom_color = color_scheme.get(a['chain'], default_color)
        if color_element == 'residue_score':
            if a["residue_index"] in list(df['aa_pos']):
                subset_df = df.loc[df['aa_pos'] == a["residue_index"]]
                subset_df = subset_df.sort_values(colname_score, ascending=False)
                atom_color=subset_df['color'].to_list()[0]
            else:
                atom_color="#8098A4"


        atom_styles.append({
            'visualization_type': visualization_type,
            'color': atom_color
        })
    return atom_styles



#3D parser
# parser = PdbParser('/Users/terwagc/PycharmProjects/dataviz_brca1/VarEffectViz/df/AF-P38398-F1-model_v4.pdb')
# df = pd.read_csv("/Users/terwagc/PycharmProjects/dataviz_brca1/VarEffectViz/df/merged_brca1_sge_ukb_2023_04_21.csv")
# print(df.head())
# # from https://alphafold.ebi.ac.uk/entry/P38398
# data = parser.mol3d_data()
# styles = create_mol3d_style(
#     data['atoms'], visualization_type='cartoon', color_element='residue_score'
# )
