from ete4 import Tree, PhyloTree
from ete4.parser.newick import NewickError
from ete4.smartview import TreeStyle, NodeStyle, TreeLayout
from ete4.smartview.renderer.faces import RectFace, TextFace, AttrFace, CircleFace, SeqMotifFace, ScaleFace
from ete4.smartview.renderer.layouts.ncbi_taxonomy_layouts import LayoutLastCommonAncestor
from ete4 import GTDBTaxa, NCBITaxa
from ete4 import random_color
from collections import defaultdict
import csv
import sys

#NEWICK = '/home/deng/Projects/metatree_drawer/metatreedrawer/demo/tree_novel.nw' #phylotree.nw
METADATA = '/home/deng/Projects/metatree_drawer/metatreedrawer/demo/novelfam_itol_taxon.txt' #emapper_annotations.tsv
LAYOUTTEMPLATE = '/home/deng/Projects/metatree_drawer/metatreedrawer/ete4layout_template.txt'

NEWICK = sys.argv[1]
def ete4_parse(newick):
    try:
        tree = PhyloTree(newick)
    except NewickError:
        try:
            tree = PhyloTree(newick, format=1)            
        except NewickError:
            tree = PhyloTree(newick, format=1, quoted_node_names=True)

    # Correct 0-dist trees
    has_dist = False
    for n in tree.traverse(): 
        if n.dist > 0: 
            has_dist = True
            break
    if not has_dist: 
        for n in tree.iter_descendants(): 
            n.dist = 1

    return tree

def parse_metadata(metadata):
    metatable = []
    tsv_file = open(metadata)
    read_tsv = csv.DictReader(tsv_file, delimiter="\t")

    for row in read_tsv:
        metatable.append(row)
    tsv_file.close()
    return metatable, read_tsv.fieldnames

def load_metadata_to_tree(tree, metadata):
    annotations, columns = parse_metadata(metadata)
    for annotation in annotations:
        gene_name = next(iter(annotation.items()))[1] #gene name must be on first column
        #print(list(annotation.values())[0])
        try:
            target_node = tree.search_nodes(name=gene_name)[0]
            for _ in range(1, len(columns)):
                
                # if columns[_] == 'seed_ortholog': # only for emapper annotations
                #     taxid, gene = annotation[columns[_]].split('.', 1)
                #     target_node.add_prop('taxid', taxid)
                #     target_node.add_prop('gene', gene)

                target_node.add_prop(columns[_], annotation[columns[_]])
        except:
            pass

    return tree, columns

# add layouts to leaf
def get_level(node, level=1):
    if node.is_root():
        return level
    else:
        return get_level(node.up, level + 1)

def get_layout_text(prop, color, column):
    def layout_new(node):
        nstyle = NodeStyle()
        if node:
            # Modify the aspect of the root node
            #nstyle["fgcolor"] = "green" # yellow
            #level = get_level(node)
            #nstyle["size"] = 5
            node.set_style(nstyle)
            node.add_face(TextFace(f'{node.props.get(prop)}',
                        color=color), 
                        column=column, position='aligned')
    return layout_new

def get_layout_lca_rects(column):
    def layout_fn(node):
       
        if node.props.get('sci_name'):
            lca = node.props.get('sci_name')
            color = node.props.get('sci_name_color', 'lightgray')
            
            level = get_level(node, level=column)
            lca_face = RectFace(self.rect_width, float('inf'), 
                    color = color, 
                    text = lca,
                    fgcolor = "white",
                    padding_x = 1, padding_y = 1)
            lca_face.rotate_text = True
            node.add_face(lca_face, position='aligned', column=level)
            node.add_face(lca_face, position='aligned', column=level,
                collapsed_only=True)

    layout_fn.__name__ = 'Last common ancestor'
    layout_fn.contains_aligned_face = True
    return layout_fn

def get_layout_numeric():
    return

def set_layouts(props, aligned_faces=True):
    layouts = []
    column = 0 
    column_colors = random_color(num=len(props))
    for prop in props:
        print(prop)
        layout = TreeLayout(name=prop, ns=get_layout_text(prop, column_colors[column], column), aligned_faces=True)
        layouts.append(layout)
        column += 1
    return layouts

def annotate_tree(newick, sp_delimiter=None, sp_field=0):
    gtdb = GTDBTaxa()
    
    def return_spcode(leaf):
        try:
            return leaf.name.split(sp_delimiter)[sp_field]
        except IndexError:
            return leaf.name

    tree = PhyloTree(newick)
    # extract sp codes from leaf names
    #tree.set_species_naming_function(return_spcode)
    
    gtdb.annotate_tree(tree, taxid_attr="name")

    # Annotate tree for smartview visualization
    set_sci_names = set()
    for n in tree.traverse():
        set_sci_names.add(n.props.get('sci_name'))

    colors = random_color(num=len(set_sci_names), l=0.5, s=0.5)
    sci_name2colors = defaultdict()

    for ele in set_sci_names:
        if ele in sci_name2colors.keys():
            continue
        else:
            sci_name2colors[ele] = colors.pop()

    all_props = set()
    name2n = {}
    for n in tree.traverse():
        name2n[n.name] = n
        sci_name = n.props.get('sci_name')
        sci_name_color = sci_name2colors[sci_name]
        n.add_prop('sci_name_color', sci_name_color)
        all_props.update(set(n.props.keys()))


    all_props.discard("_speciesFunction")
    return tree

tree = ete4_parse(NEWICK)
# gtdb= GTDBTaxa()
# gtdb.annotate_tree(tree, taxid_attr="name")
tree = annotate_tree(tree.write(properties=[]))

if METADATA:
    tree, columns = load_metadata_to_tree(tree, METADATA)
    #print(tree.write(format=1, properties=[]))
    layouts = set_layouts(columns[1:])
#layouts = []
layouts.append(LayoutLastCommonAncestor())
tree.explore(tree_name='example',layouts=layouts)