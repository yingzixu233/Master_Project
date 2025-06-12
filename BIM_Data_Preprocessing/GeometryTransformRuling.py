import GraphDataQuery


objective_houses = []

for house in GraphDataQuery.houses_1_source:
    print(house)
    house_obj = list(filter(lambda ho: ho['house_door'] == house['house_door'], GraphDataQuery.house_objective))
    angles_tr = []
    angles_rc90 = []
    angles_rc180 = []
    angles_rc270 = []
    angles_hmi = []
    angles_vmi = []
    angles_rc90_hmi = []
    angles_rc90_vmi = []
    if len(house['house_modules']) > 1:
        for s in house['surrounding']:
            angle = s['angle']
            angle_tr = 0
            angle_rc90 = 0
            angle_rc180 = 0
            angle_rc270 = 0
            angle_hmi = 0
            angle_vmi = 0
            angle_rc90_hmi = 0
            angle_rc90_vmi = 0

            if -180 < angle <= 180:
                angle_tr = angle

            if -180 < angle < 0:
                angle_hmi = - angle - 180
            if 0 <= angle <= 180:
                angle_hmi = - angle + 180

            if -180 < angle < 180:
                angle_vmi = -angle
            if angle == 180:
                angle_vmi = 180

            if -180 < angle <= 0:
                angle_rc180 = angle + 180
            if 0 < angle <= 180:
                angle_rc180 = angle - 180

            if -180 < angle <= 90:
                angle_rc90 = angle + 90
                angle_rc270 = angle + 270
            if 90 < angle <= 180:
                angle_rc90 = angle - 270
                angle_rc270 = angle - 90

            if -180 < angle < 90:
                angle_rc90_hmi = - angle - 270
                angle_rc90_vmi = - angle - 90
            if 90 <= angle <= 180:
                angle_rc90_hmi = - angle + 90
                angle_rc90_vmi = - angle + 270

            angles_tr.append(angle_tr)
            angles_rc90.append(angle_rc90)
            angles_rc180.append(angle_rc180)
            angles_rc270.append(angle_rc270)
            angles_hmi.append(angle_hmi)
            angles_vmi.append(angle_vmi)
            angles_rc90_hmi.append(angle_rc90_hmi)
            angles_rc90_vmi.append(angle_rc90_vmi)

        for h in house_obj:
            transform = ''
            angles_obj = []
            for s in h['surrounding']:
                angles_obj.append(s['angle'])
            if set(angles_obj) == set(angles_tr):
                transform = "Translation"
            elif set(angles_obj) == set(angles_rc90):
                transform = "Translation + 90-degree Counterclockwise Rotation"
            elif set(angles_obj) == set(angles_rc180):
                transform = "Translation + 180-degree Counterclockwise Rotation"
            elif set(angles_obj) == set(angles_rc270):
                transform = "Translation + 270-degree Counterclockwise Rotation"
            elif set(angles_obj) == set(angles_hmi):
                transform = "Translation + Horizontal Mirror"
            elif set(angles_obj) == set(angles_vmi):
                transform = "Translation + Vertical Mirror"
            elif set(angles_obj) == set(angles_rc90_vmi):
                transform = "Translation + 90-degree Counterclockwise Rotation + Vertical Mirror"
            elif set(angles_obj) == set(angles_rc90_hmi):
                transform = "Translation + 90-degree Counterclockwise Rotation + Horizontal Mirror"
            h['transform'] = transform
            objective_houses.append(h)
    elif len(house['house_modules']) == 1:
        for h in house_obj:
            transform = 'Any'
            h['transform'] = transform
            objective_houses.append(h)

