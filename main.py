import numpy as np
import svgwrite


def subdivide_line(start, end, division_length, is_innie):
    midpoint = (start + end) / 2.0
    step = division_length * (end - start) / np.linalg.norm(end - start)
    cuts = []
    position = step / 2.0
    exclusion = 10
    while (np.linalg.norm(midpoint - start) -
            exclusion > np.linalg.norm(position)):
        cuts.append(np.copy(position))
        position += step

    positions = midpoint + np.vstack((-np.array(list(reversed(cuts))),
                                      np.array(cuts)))
    indices = range(-len(cuts), len(cuts))

    tooth_length = 4
    offset = (
        tooth_length *
        np.array([start[1] - end[1], end[0] - start[0]]) /
        np.linalg.norm(end - start)
    )

    overshoot = 1.0

    result = []
    for index, position in zip(indices, positions):
        if index % 2 == is_innie:
            if not result:
                result.append(start + offset - overshoot * step)
            result.append(position + offset)
            result.append(position)
        else:
            if not result:
                result.append(start - overshoot * step)
            result.append(position)
            result.append(position + offset)
    if index % 2 == is_innie:
        result.append(end + overshoot * step)
    else:
        result.append(end + offset + overshoot * step)

    return np.array(result)


def rectangle(origin, height, width):
    vertices = [
        np.array(origin) + np.array([0, width]),
        np.array(origin) + np.array([height, width]),
        np.array(origin) + np.array([height, 0]),
        np.array(origin),
    ]
    return map(tuple, vertices)


def symmetric_trapezoid(origin, height, wide_width, narrow_width):
    vertices = [
        np.array(origin),
        np.array(origin) + np.array([wide_width, 0]),
        np.array(origin) + np.array(
            [wide_width - float(wide_width - narrow_width) / 2.0, height]
        ),
        np.array(origin) + np.array(
            [float(wide_width - narrow_width) / 2.0, height]
        ),
    ]
    return map(tuple, vertices)


def open_frustrum(closed_rectangle, open_rectangle, depth):
    origin = (20, 20)
    result = [rectangle(origin, *closed_rectangle)]

    width_closed, height_closed = closed_rectangle
    width_open, height_open = open_rectangle

    result.append(symmetric_trapezoid(
        origin,
        np.sqrt(depth**2 + (float(height_open - height_closed) / 2.0)**2),
        width_open,
        width_closed)
    )
    result.append(symmetric_trapezoid(
        origin,
        np.sqrt(depth**2 + (float(width_open - width_closed) / 2.0)**2),
        height_open,
        height_closed)
    )
    return result


polygons = open_frustrum((64, 64), (178, 128), 150)

phases = [
    [True, True, True, True],
    [True, False, True, False],
    [True, False, True, False],
    [True, True, True, True],
    [True, True, True, True],
]

draw_circle = True

for polygon_count, (polygon, phases) in enumerate(zip(polygons, phases)):
    segments = []
    for (start, end), phase in zip(zip(polygon, np.roll(polygon, -1, axis=0)),
                                   phases):
        segments.append(
            subdivide_line(np.array(start), np.array(end), 8, phase)
        )

    dwg = svgwrite.Drawing('%i.svg' % polygon_count, size=('240mm', '240mm'),
                           viewBox=('0 0 240 240'))
    for segment in segments:
        for i in range(len(segment) - 1):
            dwg.add(dwg.line(segment[i], segment[i+1],
                             stroke=svgwrite.rgb(0, 0, 0, '%'),
                             stroke_width=1))
    if draw_circle:
        dwg.add(dwg.line((20, 20), (20, 84),
                         stroke=svgwrite.rgb(100, 0, 0, '%'), stroke_width=1))
        dwg.add(dwg.circle((52, 52), 34.6 / 2.0, stroke=svgwrite.rgb(0, 0, 0),
                           stroke_width=1, fill='none'))
    dwg.save()
    draw_circle = False
