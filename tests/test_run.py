

def test_run_single(sample_config, data_dict_10d, tmp_path):
    from aquacrop_fd import model_setup
    from aquacrop_fd import run

    # replicate input files dict
    data = {name: data_dict_10d.copy() for name in model_setup.REQUIRED_CLIMATE_FILES}

    run.run_single(rundir=tmp_path, data=data, config=sample_config)
    raise RuntimeError()
