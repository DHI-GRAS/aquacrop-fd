

def test_prepare_data_folder(sample_config, data_dict_10d, tmp_path):
    from aquacrop_fd import model_setup

    # replicate input files dict
    data = {name: data_dict_10d.copy() for name in model_setup.REQUIRED_CLIMATE_FILES}
    data['Climate.TMP']['arrs'] = data['Climate.TMP']['arrs'] * 2
    print(data)

    datadir = tmp_path / 'DATA'
    datadir.mkdir(exist_ok=True)

    # prepare data folder
    project_file = model_setup.prepare_data_folder(
        project_name='funny1',
        rundir=tmp_path,
        datadir=datadir,
        data_by_name=data,
        config=sample_config
    )

    assert project_file.is_file()
