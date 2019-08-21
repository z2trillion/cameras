import numpy as np
import svgwrite

from main import (
    subdivide_line,
    rectangle,
    open_frustrum,
)

origin = np.array([20.0, 20.0])

front_height_fudge = 1.0
front_width_fudge = 1.0
film_hole_length = 121.5
film_hole_width = 98
lens_frustrum_length = 90.0
polygons = open_frustrum((60.0, 60.0), (film_hole_length, film_hole_width),
                         lens_frustrum_length, front_height_fudge,
                         front_width_fudge)

phases = [
    [True, True, True, True],
    [True, False, True, True],
    [False, False, False, False],
]

for polygon_count, (polygon, phases) in enumerate(zip(polygons, phases)):
    dwg = svgwrite.Drawing('%i_4x5.svg' % polygon_count,
                           size=('240mm', '240mm'), viewBox=('0 0 240 240'))

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

        tooth_length = 3.0
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
            (origin[0] + 30 - front_height_fudge / 2.0,
             origin[1] + 30 - front_width_fudge / 2.0),
            34.6 / 2.0, stroke=svgwrite.rgb(255, 0, 0),
            stroke_width=1, fill='none'))
    dwg.save()

film_holder_length = 159.5
film_holder_width = 119.5

distance_to_exposure_field = 15

backplate_depth = 12.5

backplate_polygons = [
    rectangle(film_holder_length, film_holder_width),
    rectangle(film_hole_length, film_hole_width),
]
backplate_phases = [
    [True, True, True, True],
    [False, True, False, True],
]

backplate = svgwrite.Drawing('backplate_4x5.svg', size=('300mm', '260mm'),
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
        if 4 <= line_count:
            offset = np.array([
                distance_to_exposure_field,
                float(film_holder_width - film_hole_width) / 2.0
            ])

        midpoint_offset = 0.0
        if line_count in [8, 19]:
            midpoint_offset = -2.0
        elif line_count in [12, 17]:
            midpoint_offset = 2.0

        if line_count < 4:
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
