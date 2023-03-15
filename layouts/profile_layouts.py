from ete4.smartview import TreeStyle, NodeStyle, TreeLayout, PieChartFace
from ete4.smartview  import (RectFace, CircleFace, SeqMotifFace, TextFace, OutlineFace, \
                            SelectedFace, SelectedCircleFace, SelectedRectFace, LegendFace,
                            SeqFace, Face, ScaleFace, AlignmentFace)
from ete4.smartview.renderer.draw_helpers import *
from ete4 import SeqGroup
from layouts.general_layouts import get_piechartface, get_heatmapface, color_gradient 
from collections import OrderedDict, namedtuple
import re

Box = namedtuple('Box', 'x y dx dy')  # corner and size of a 2D shape

profilecolors = {
    'A':"#C8C8C8" ,
    'R':"#145AFF" ,
    'N':"#00DCDC" ,
    'D':"#E60A0A" ,
    'C':"#E6E600" ,
    'Q':"#00DCDC" ,
    'E':"#E60A0A" ,
    'G':"#EBEBEB" ,
    'H':"#8282D2" ,
    'I':"#0F820F" ,
    'L':"#0F820F" ,
    'K':"#145AFF" ,
    'M':"#E6E600" ,
    'F':"#3232AA" ,
    'P':"#DC9682" ,
    'S':"#FA9600" ,
    'T':"#FA9600" ,
    'W':"#B45AB4" ,
    'Y':"#3232AA" ,
    'V':"#0F820F" ,
    'B':"#FF69B4" ,
    'Z':"#FF69B4" ,
    'X':"#BEA06E",
    '.':"#FFFFFF",
    '-':"#FFFFFF",
    }

class LayoutProfile(TreeLayout):
    def __init__(self, name="Profile",
            alignment=None, format='compactseq', profiles=None, width=700, height=15,
            column=0, range=None, summarize_inner_nodes=False):
        super().__init__(name)
        self.alignment = SeqGroup(alignment) if alignment else None
        self.width = width
        self.height = height
        self.column = column
        self.aligned_faces = True
        self.format = format
        self.profiles = profiles

        self.length = len(next(self.alignment.iter_entries())[1]) if self.alignment else None
        self.scale_range = range or (0, self.length)
        self.summarize_inner_nodes = summarize_inner_nodes

    def set_tree_style(self, tree, tree_style):
        if self.length:
            face = TextScaleFace(width=self.width, scale_range=self.scale_range, 
                                headers=self.profiles, padding_y=0)
            #face = ScaleFace(width=self.width, scale_range=self.scale_range, padding_y=0)
            tree_style.aligned_panel_header.add_face(face, column=self.column)
    
    def _get_seq(self, node):
        if self.alignment:
            return self.alignment.get_seq(node.name)
        return node.props.get("seq", None)

    def get_seq(self, node):
        if node.is_leaf():
            return self._get_seq(node)

        if self.summarize_inner_nodes:
            # TODO: summarize inner node's seq
            return None
        else:
            first_leaf = next(node.iter_leaves())
            return self._get_seq(first_leaf)
    
    def set_node_style(self, node):
        
        seq = self.get_seq(node)
        if len(self.profiles) > 1:
            poswidth = self.width / (len(self.profiles)-1 )
        else:
            poswidth = self.width
        if seq:
            seqFace = ProfileAlignmentFace(seq, gap_format='line', seqtype='aa', 
            seq_format=self.format, width=self.width, height=self.height, 
            poswidth=poswidth,
            fgcolor='black', bgcolor='#bcc3d0', gapcolor='gray',
            gap_linewidth=0.2,
            max_fsize=12, ftype='sans-serif', 
            padding_x=0, padding_y=0)
            node.add_face(seqFace, column=self.column, position='aligned', 
                    collapsed_only=(not node.is_leaf())) 

class LayoutGOslim(TreeLayout):
    def __init__(self, name=None, column=1, color='red', go_propfile=[], goslim_prop=None, padding_x=2, padding_y=2, legend=True):
        super().__init__(name)
        self.aligned_faces = True
        self.go_propfile = go_propfile
        self.goslim_prop = goslim_prop
        self.column = column
        self.color = color
        self.padding_x = padding_x
        self.padding_y = padding_y
        self.legend = legend
        self.width = 70
        self.height = 50

    def set_tree_style(self, tree, tree_style):
        super().set_tree_style(tree, tree_style)
        header = f'{self.go_propfile[1]}({self.go_propfile[0]})'
        text = TextFace(header, min_fsize=5, max_fsize=10, padding_x=self.padding_x, width=70, rotation=315)
        tree_style.aligned_panel_header.add_face(text, column=self.column)
    
    def set_node_style(self, node):
        entry, desc = self.go_propfile
        if node.is_leaf() and node.props.get(self.goslim_prop):
            goslims = node.props.get(self.goslim_prop)
            if entry in goslims[0]:
                prop_face = RectFace(width=self.width, height=self.height, color=self.color,  padding_x=self.padding_x, padding_y=self.padding_y)
                node.add_face(prop_face, column=self.column, position = "aligned")
            # if entry in goslims[0]:
            #     index = goslims[0].index(entry)
            #     relative_count = goslims[2][index]
            #     c1 = 'white'
            #     c2 = self.color
            #     gradient_color = color_gradient(c1, c2, mix=relative_count)
            #     prop_face = RectFace(width=self.width, height=self.height, color=gradient_color,  padding_x=self.padding_x, padding_y=self.padding_y)
            #     node.add_face(prop_face, column=self.column, position = "aligned")
                
class TextScaleFace(Face):
    def __init__(self, name='', width=None, color='black',
            scale_range=(0, 0), headers=None, tick_width=100, line_width=1,
            formatter='%.0f', 
            min_fsize=10, max_fsize=10, ftype='sans-serif',
            padding_x=0, padding_y=0):

        Face.__init__(self, name=name,
                padding_x=padding_x, padding_y=padding_y)

        self.width = width
        self.height = None
        self.range = scale_range
        self.headers = headers

        self.color = color
        self.min_fsize = min_fsize
        self.max_fsize = max_fsize
        self._fsize = max_fsize
        self.ftype = ftype
        self.formatter = formatter

        self.tick_width = tick_width
        self.line_width = line_width

        self.vt_line_height = 10

    def __name__(self):
        return "ScaleFace"

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if drawer.TYPE == 'circ':
            pos = swap_pos(pos, point[1])

        box = super().compute_bounding_box(
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, _, dy = box
        zx, zy = self.zoom

        self.viewport = (drawer.viewport.x, drawer.viewport.x + drawer.viewport.dx)

        self.height = (self.line_width + 10 + self.max_fsize) / zy

        height = min(dy, self.height)

        if pos == "aligned_bottom":
            y = y + dy - height

        self._box = Box(x, y, self.width / zx, height)
        return self._box

    def draw(self, drawer):
        x0, y, _, dy = self._box
        zx, zy = self.zoom

        p1 = (x0, y + dy - 5 / zy)
        p2 = (x0 + self.width, y + dy - self.vt_line_height / (2 * zy))
        if drawer.TYPE == 'circ':
            p1 = cartesian(p1)
            p2 = cartesian(p2)
        # yield draw_line(p1, p2, style={'stroke-width': self.line_width,
        #                                'stroke': self.color})


        #nticks = round((self.width * zx) / self.tick_width)
        if len(self.headers) > 1:
            nticks = len(self.headers)
        else:
            nticks = 1
        dx = self.width / nticks
        range_factor = (self.range[1] - self.range[0]) / self.width

        if self.viewport:
            sm_start = round(max(self.viewport[0] - self.viewport_margin - x0, 0) / dx)
            sm_end = nticks - round(max(x0 + self.width - (self.viewport[1] +
                self.viewport_margin), 0) / dx)
        else:
            sm_start, sm_end = 0, nticks
            
        for i in range(sm_start, sm_end + 1):
            x = x0 + i * dx + dx/2 
            
            number = range_factor * i * dx
            if number == 0:
                text = "0"
            else:
                text = self.formatter % number if self.formatter else str(number)

            #text = text.rstrip('0').rstrip('.') if '.' in text else text
            try:
                text = self.headers[i]
                self.compute_fsize(self.tick_width / len(text), dy, zx, zy)
                text_style = {
                    'max_fsize': self._fsize,
                    'text_anchor': 'left', # left, middle or right
                    'ftype': f'{self.ftype}, sans-serif', # default sans-serif
                    }

                text_box = Box(x,
                        y,
                        # y + (dy - self._fsize / (zy * r)) / 2,
                        dx, dy)
                yield draw_text(text_box, text, style=text_style,rotation=270)

                # p1 = (x, y + dy - self.vt_line_height / zy)
                # p2 = (x, y + dy)

                # yield draw_line(p1, p2, style={'stroke-width': self.line_width,
                #                                'stroke': self.color})
            except IndexError:
                break
class ProfileAlignmentFace(Face):
    def __init__(self, seq, bg=None,
            gap_format='line', seqtype='aa', seq_format='[]',
            width=None, height=None, # max height
            fgcolor='black', bgcolor='#bcc3d0', gapcolor='gray',
            gap_linewidth=0.2,
            max_fsize=12, ftype='sans-serif', poswidth=5,
            padding_x=0, padding_y=0):

        Face.__init__(self, padding_x=padding_x, padding_y=padding_y)

        self.seq = seq
        self.seqlength = len(self.seq)
        self.seqtype = seqtype

        self.autoformat = True  # block if 1px contains > 1 tile

        self.seq_format = seq_format
        self.gap_format = gap_format
        self.gap_linewidth = gap_linewidth
        self.compress_gaps = False

        self.poswidth = poswidth
        self.w_scale = 1
        self.width = width    # sum of all regions' width if not provided
        self.height = height  # dynamically computed if not provided

        total_width = self.seqlength * self.poswidth
        if self.width:
            self.w_scale = self.width / total_width
        else:
            self.width = total_width
        self.bg = profilecolors
        # self.fgcolor = fgcolor
        # self.bgcolor = bgcolor
        self.gapcolor = gapcolor

        # Text
        self.ftype = ftype
        self._min_fsize = 8
        self.max_fsize = max_fsize
        self._fsize = None

        self.blocks = []
        self.build_blocks()

    def __name__(self):
        return "AlignmentFace"

    def get_seq(self, start, end):
        """Retrieves sequence given start, end"""
        return self.seq[start:end]

    def build_blocks(self):
        pos = 0
        for reg in re.split('([^-]+)', self.seq):
            if reg:
                if not reg.startswith("-"):
                    self.blocks.append([pos, pos + len(reg) - 1])
                pos += len(reg)

        self.blocks.sort()

    def compute_bounding_box(self,
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before):

        if pos != 'branch_right' and not pos.startswith('aligned'):
            raise InvalidUsage(f'Position {pos} not allowed for SeqMotifFace')

        box = super().compute_bounding_box(
            drawer,
            point, size,
            dx_to_closest_child,
            bdx, bdy,
            bdy0, bdy1,
            pos, row,
            n_row, n_col,
            dx_before, dy_before)

        x, y, _, dy = box

        zx, zy = self.zoom
        zx = 1 if drawer.TYPE != 'circ' else zx

            # zx = drawer.zoom[0]
            # self.zoom = (zx, zy)

        if drawer.TYPE == "circ":
            self.viewport = (0, drawer.viewport.dx)
        else:
            self.viewport = (drawer.viewport.x, drawer.viewport.x + drawer.viewport.dx)

        self._box = Box(x, y, self.width / zx, dy)
        return self._box

    def draw(self, drawer):
        def get_height(x, y):
            r = (x or 1e-10) if drawer.TYPE == 'circ' else 1
            default_h = dy * zy * r
            h = min([self.height or default_h, default_h]) / zy
            # h /= r
            return y + (dy - h) / 2, h

        # Only leaf/collapsed branch_right or aligned
        x0, y, dx, dy = self._box
        zx, zy = self.zoom
        zx = drawer.zoom[0] if drawer.TYPE == 'circ' else zx


        if self.gap_format in ["line", "-"]:
            p1 = (x0, y + dy / 2)
            p2 = (x0 + self.width, y + dy / 2)
            if drawer.TYPE == 'circ':
                p1 = cartesian(p1)
                p2 = cartesian(p2)
            yield draw_line(p1, p2, style={'stroke-width': self.gap_linewidth,
                                           'stroke': self.gapcolor})
        vx0, vx1 = self.viewport
        too_small = (self.width * zx) / (self.seqlength) < 1

        posw = self.poswidth * self.w_scale
        viewport_start = vx0 - self.viewport_margin / zx
        viewport_end = vx1 + self.viewport_margin / zx
        sm_x = max(viewport_start - x0, 0)
        sm_start = round(sm_x / posw)
        w = self.seqlength * posw
        sm_x0 = x0 if drawer.TYPE == "rect" else 0
        sm_end = self.seqlength - round(max(sm_x0 + w - viewport_end, 0) / posw)

        if too_small or self.seq_format == "[]":
            
            for start, end in self.blocks:
                if end >= sm_start and start <= sm_end:
                    bstart = max(sm_start, start)
                    bend = min(sm_end, end)
                    bx = x0 + bstart * posw
                    by, bh = get_height(bx, y)
                    box = Box(bx, by, (bend + 1 - bstart) * posw, bh)
                    
                    yield [ "pixi-block", box ]

        else:
            seq = self.get_seq(sm_start, sm_end)
            sm_x = sm_x if drawer.TYPE == 'rect' else x0
            y, h = get_height(sm_x, y)
            sm_box = Box(x0, y, posw * len(seq), h)
            if self.seq_format == 'compactseq' or posw * zx < self._min_fsize:
                aa_type = "notext"
            else:
                aa_type = "text"
            yield [ f'pixi-aa_{aa_type}', sm_box, seq ]
            