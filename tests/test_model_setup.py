

def test_prepare_data_folder(sample_config, data_dict_10d, tmp_path):
    from model_setup.prepare_data_folder import prepare_data_folder
    prepare_data_folder(
        outdir=tmp_path,
        data=data_dict_10d,
        config=sample_config
    )
