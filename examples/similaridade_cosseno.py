import math as m

def cosseno(rating1, rating2):

    xy = 0
    sum_x2 = 0
    sum_y2 = 0

    for key in rating1:
        if key in rating2:
            sum_x2 += pow(rating1[key],2)
            sum_y2 += pow (rating2[key],2)

            xy += rating1[key] * rating2[key]

    if xy == 0:
        return 0
    else:
        return (xy / (m.sqrt(sum_x2) * m.sqrt(sum_y2)))
    
