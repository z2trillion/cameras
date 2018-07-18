import numpy as np
import svgwrite


origin = np.array([20.0, 20.0])


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


def rectangle(height, width):
    vertices = [
        origin,
        origin + np.array([0, width]),
        origin + np.array([height, width]),
        origin + np.array([height, 0]),
    ]
    return map(tuple, vertices)


def symmetric_trapezoid(height, wide_width, narrow_width):
    vertices = [
        origin,
        origin + np.array(
            [float(wide_width - narrow_width) / 2.0, height]
        ),
        origin + np.array(
            [wide_width - float(wide_width - narrow_width) / 2.0, height]
        ),
        origin + np.array([wide_width, 0]),
    ]
    return map(tuple, vertices)


def open_frustrum(closed_rectangle, open_rectangle, depth,
                  front_height_fudge=0, front_width_fudge=0):
    front_height, front_width = closed_rectangle

    width_closed, height_closed = closed_rectangle
    width_open, height_open = open_rectangle

    return [
        rectangle(front_height - front_height_fudge,
                  front_width - front_width_fudge),
        symmetric_trapezoid(
            np.sqrt(depth**2 + (float(height_open - height_closed) / 2.0)**2),
            width_open,
            width_closed),
        symmetric_trapezoid(
            np.sqrt(depth**2 + (float(width_open - width_closed) / 2.0)**2),
            height_open,
            height_closed)
    ]


front_height_fudge = 2
front_width_fudge = 2
polygons = open_frustrum((64.0, 64.0), (178.0, 128.0), 150.0,
                         front_height_fudge, front_width_fudge)

phases = [
    [True, True, True, True],
    [True, True, True, True],
    [False, False, False, False],
]

draw_circle = True

for polygon_count, (polygon, phases) in enumerate(zip(polygons, phases)):
    dwg = svgwrite.Drawing('%i.svg' % polygon_count, size=('240mm', '240mm'),
                           viewBox=('0 0 240 240'))

    segments = []
    for (start, end), phase in zip(zip(polygon, np.roll(polygon, -1, axis=0)),
                                   phases):
        segments.append(
            subdivide_line(np.array(start), np.array(end), 8, phase)
        )
        # dwg.add(dwg.line(start, end, stroke=svgwrite.rgb(0, 0, 0, '%'),
        #                  stroke_width=1))

    for segment in segments:
        for i in range(len(segment) - 1):
            dwg.add(dwg.line(segment[i], segment[i+1],
                             stroke=svgwrite.rgb(255, 0, 0, '%'),
                             stroke_width=1))
    if draw_circle:
        dwg.add(dwg.circle((51, 51), 34.6 / 2.0,
                           stroke=svgwrite.rgb(255, 0, 0),
                           stroke_width=1, fill='none'))
    dwg.save()
    draw_circle = False
