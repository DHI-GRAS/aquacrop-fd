import pytest


@pytest.mark.skiplinux
def test_run_single(sample_config, data_dict_10d, tmp_path):
    from aquacrop_fd import run

    run.run_single(
        project_name='silly1',
        rundir=tmp_path,
        datadir=tmp_path / 'DATA',
        data_by_name=data_dict_10d,
        config=sample_config
    )
