

def test_prepare_data_folder(sample_config, data_dict_10d, tmp_path):
    from aquacrop_fd import model_setup

    datadir = tmp_path / 'DATA'
    datadir.mkdir(exist_ok=True)

    # prepare data folder
    project_file, project_config = model_setup.prepare_data_folder(
        project_name='funny1',
        listdir=tmp_path,
        datadir=datadir,
        data_by_name=data_dict_10d,
        config=sample_config
    )

    assert project_file.is_file()
    assert project_config
