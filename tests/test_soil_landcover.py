

def test_select_extract_class_points(soil_map_file):
    from aquacrop_fd import soil_landcover
    ixds = soil_landcover.select_extract_class_points(
        select_path=soil_map_file,
        select_class=3,
        extract_path=soil_map_file,
        bounds=(0, -0.4, 0.4, 0)
    )
    assert 'point' in ixds.coords
    assert 'extracted' in ixds
