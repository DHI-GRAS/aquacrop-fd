

def test_find_class_points(soil_map_file):
    from aquacrop_fd import data_in
    ixds = data_in.find_class_points(paths=[soil_map_file], class_values=[3], bounds=None)
    assert 'point' in ixds.coords
