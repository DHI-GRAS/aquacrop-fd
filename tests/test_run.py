import pytest


@pytest.mark.skiplinux
def test_run_single(sample_config, data_dict_10d, tmp_path):
    from aquacrop_fd import model_setup
    from aquacrop_fd import run

    # replicate input files dict
    data = {name: data_dict_10d.copy() for name in model_setup.REQUIRED_CLIMATE_FILES}
    data['Climate.TMP']['arrs'] = data['Climate.TMP']['arrs'] * 2

    run.run_single(
        project_name='silly1',
        rundir=tmp_path,
        datadir=tmp_path / 'DATA',
        data_by_name=data,
        config=sample_config
    )
