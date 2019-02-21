import numpy as np
import svgwrite


def draw_circle(center, radius, drawing):
    drawing.add(drawing.circle(center=center, r=radius, stroke='red',
                               fill='none'))


def draw_rectangle(origin, width, height, drawing):
    x, y = origin
    vertices = [
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height)
    ]

    for i in range(len(vertices)):
        drawing.add(drawing.line(vertices[i - 1], vertices[i],
                                 stroke=svgwrite.rgb(255, 0, 0, '%'),
                                 stroke_width=1))


def draw_rectangle_with_gores(origin, width, height, overlap, n_gores,
                              drawing):
    gore_bottom_width = width / float(n_gores)
    gore_top_width = (width - 2*np.pi*overlap) / float(n_gores)
    gore_offset = (gore_bottom_width - gore_top_width) / 2.0

    x, y = origin

    gore_vertices = []
    for i in range(n_gores):
        gore_vertices.append((x + i * gore_bottom_width, y))
        gore_vertices.append((x + i * gore_bottom_width + gore_offset,
                              y - overlap))
        gore_vertices.append((x + (i + 1) * gore_bottom_width - gore_offset,
                              y - overlap))
    gore_vertices.append((x + width, y))

    gore_vertices.append((x + width + overlap, y))
    gore_vertices.append((x + width + overlap, y + height))
    gore_vertices.append((x + width, y + height))

    for i in range(n_gores)[::-1]:
        gore_vertices.append((x + (i + 1) * gore_bottom_width - gore_offset,
                              y + height + overlap))
        gore_vertices.append((x + i * gore_bottom_width + gore_offset,
                              y + height + overlap))
        gore_vertices.append((x + i * gore_bottom_width, y + height))

    for i in range(len(gore_vertices)):
        drawing.add(drawing.line(gore_vertices[i - 1], gore_vertices[i],
                                 stroke=svgwrite.rgb(255, 0, 0, '%'),
                                 stroke_width=1))


dwg = svgwrite.Drawing('sewing_1.svg', size=('600mm', '300mm'),
                       viewBox=('0 0 600 300'))

mm_per_inch = 25.4

diameter = 6 * mm_per_inch
length = 8 * mm_per_inch
overlap = .5 * mm_per_inch

draw_rectangle((5, 5), np.pi * (2*overlap + diameter),
               length + 2 * overlap, dwg)
dwg.save()

dwg = svgwrite.Drawing('sewing_2.svg', size=('600mm', '300mm'),
                       viewBox=('0 0 600 300'))

draw_circle((100, 90), diameter / 2.0 + overlap, dwg)
draw_circle((300, 90), diameter / 2.0 + overlap, dwg)
dwg.save()



dwg = svgwrite.Drawing('cf.svg', size=('450mm', '300mm'),
                       viewBox=('0 0 450 300'))

draw_circle((85, 55), 50, dwg)
draw_circle((230, 55), 50, dwg)

draw_rectangle_with_gores((5, 140), 2*np.pi*50, 100, 12.7, 40, dwg)
dwg.save()

dwg = svgwrite.Drawing('delrin.svg', size=('450mm', '300mm'),
                       viewBox=('0 0 450 300'))
draw_rectangle((5, 5), 12.7, 120, dwg)
draw_rectangle((30, 5), 12.7, 120, dwg)

center_1 = (100, 55)
draw_circle(center_1, 50, dwg)
draw_circle(center_1, 50 - 12.7, dwg)

center_2 = (220, 55)
draw_circle(center_2, 50, dwg)
draw_circle(center_2, 50 - 13.2, dwg)


# draw_rectangle((0, 0), 450, 300, dwg)

dwg.save()
