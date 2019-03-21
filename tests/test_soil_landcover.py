

def test_find_class_points(soil_map_file):
    from aquacrop_fd import soil_landcover
    ixds = soil_landcover.find_class_points(
        paths=[soil_map_file],
        class_values=[3],
        bounds=(0, -0.4, 0.4, 0)
    )
    assert 'point' in ixds.coords
