import numpy as np
import svgwrite


origin = np.array([20.0, 20.0])


def subdivide_line(start, end, division_length, is_innie, midpoint_offset=0.0,
                   overshoot=1.0, exclusion=10.0, tooth_length=4.0):
    unit_vector = (end - start) / np.linalg.norm(end - start)

    midpoint = (start + end) / 2.0 + midpoint_offset * unit_vector
    step = division_length * unit_vector
    cuts = []
    position = step / 2.0
    while (np.linalg.norm(midpoint - start) -
            exclusion > np.linalg.norm(position)):
        cuts.append(np.copy(position))
        position += step

    positions = midpoint + np.vstack((-np.array(list(reversed(cuts))),
                                      np.array(cuts)))
    indices = range(-len(cuts), len(cuts))

    offset = (
        tooth_length *
        np.array([start[1] - end[1], end[0] - start[0]]) /
        np.linalg.norm(end - start)
    )

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
            0.5 + np.sqrt(depth**2 + (float(height_open -
                                            height_closed) / 2.0)**2),
            width_open,
            width_closed),
        symmetric_trapezoid(
            np.sqrt(depth**2 + (float(width_open - width_closed) / 2.0)**2),
            height_open,
            height_closed)
    ]


front_height_fudge = 1.0
front_width_fudge = 1.0
# The length of the opening is actually only 171mm!
polygons = open_frustrum((64.0, 64.0), (178.0, 128.0), 150.0,
                         front_height_fudge, front_width_fudge)

phases = [
    [True, True, True, True],
    [True, False, True, True],
    [False, False, False, False],
]

for polygon_count, (polygon, phases) in enumerate(zip(polygons, phases)):
    dwg = svgwrite.Drawing('%i.svg' % polygon_count, size=('240mm', '240mm'),
                           viewBox=('0 0 240 240'))

    segments = []
    line_count = 0
    for (start, end), phase in zip(zip(polygon, np.roll(polygon, -1, axis=0)),
                                   phases):
        midpoint_offset = 0
        if polygon_count == 1:
            offset_magnitude = 0.5
            if line_count == 0:
                midpoint_offset = -offset_magnitude
            elif line_count == 2:
                midpoint_offset = offset_magnitude

        tooth_length = 4.0
        if polygon_count != 0 and line_count == 3:
            tooth_length = 2.5
        segments.append(
            subdivide_line(np.array(start), np.array(end), 8, phase,
                           midpoint_offset=midpoint_offset,
                           tooth_length=tooth_length)
        )
        line_count += 1

    for segment in segments:
        for i in range(len(segment) - 1):
            dwg.add(dwg.line(segment[i], segment[i+1],
                             stroke=svgwrite.rgb(255, 0, 0, '%'),
                             stroke_width=1))
    if polygon_count == 0:
        dwg.add(dwg.circle(
            (origin[0] + 32 - front_height_fudge / 2.0,
             origin[1] + 32 - front_width_fudge / 2.0),
            34.6 / 2.0, stroke=svgwrite.rgb(255, 0, 0),
            stroke_width=1, fill='none'))
    dwg.save()

film_holder_length = 220
film_holder_width = 150 + 0.25

film_hole_length = 177.5
film_hole_width = 127.5

distance_to_exposure_field = 17.5

backplate_depth = 12.5

backplate_polygons = [
    rectangle(film_holder_length, film_holder_width),
    rectangle(film_hole_length, film_hole_width),
    rectangle(film_holder_length, backplate_depth),
    rectangle(film_holder_length, backplate_depth),
    rectangle(backplate_depth, film_holder_width),
]
backplate_phases = [
    [True, True, True, True],
    [False, True, False, True],
    [False, True, False, False],
    [False, False, False, False],
    [False, True, False, True],
]

backplate = svgwrite.Drawing('backplate.svg', size=('300mm', '260mm'),
                             viewBox=('0 0 300 260'))
line_count = 0
for polygon, phases in zip(backplate_polygons, backplate_phases):
    segments = []
    for start, end, phase in zip(polygon, np.roll(polygon, -1, axis=0),
                                 phases):
        start = np.array(start)
        end = np.array(end)
        offset = np.zeros(2)
        exclusion = 10.0
        overshoot = 0.0
        if 4 <= line_count < 8:
            offset = np.array([
                distance_to_exposure_field,
                float(film_holder_width - film_hole_width) / 2.0
            ])
        elif 8 <= line_count < 12:
            offset = np.array([0, film_holder_width + 8])
        elif 12 <= line_count < 16:
            offset = np.array([0, 178])
        elif 16 <= line_count:
            offset = np.array([230, 0])

        if line_count in [8, 10, 12, 14, 16, 17, 19]:
            exclusion = 0
            overshoot = 0.5
        if line_count == 18:
            overshoot = 0.5

        midpoint_offset = 0.0
        if line_count in [8, 19]:
            midpoint_offset = -2.0
        elif line_count in [12, 17]:
            midpoint_offset = 2.0

        if line_count in [2, 9, 10, 14, 15, 16]:
            step = 8 * (end - start) / np.linalg.norm(end - start)
            segments.append(np.array([start - overshoot * step + offset,
                                      end + overshoot * step + offset]))
        else:
            segments.append(
                subdivide_line(np.array(start) + offset,
                               np.array(end) + offset, 8, phase,
                               overshoot=overshoot, exclusion=exclusion,
                               midpoint_offset=midpoint_offset)
            )
        line_count += 1

    for segment in segments:
        for i in range(len(segment) - 1):
            backplate.add(backplate.line(segment[i], segment[i + 1],
                                         stroke=svgwrite.rgb(255, 0, 0, '%'),
                                         stroke_width=1))
    backplate.save()
