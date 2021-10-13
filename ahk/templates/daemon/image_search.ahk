CoordMode, Pixel, {{ coord_mode }}
ImageSearch,xpos,ypos,{{ x1 }},{{ y1 }},{{ x2 }},{{ y2 }},{% if options %}{% for option in options %}*{{ option }} {% endfor %}{% endif %}{{ image_path }}