import spinn_utilities
import spinn_machine


def test_compare_versions():
    spinn_utilities_parts = spinn_utilities.__version__.split('.')
    spinn_machine_parts = spinn_machine.__version__.split('.')

    assert (spinn_utilities_parts[0] == spinn_machine_parts[0])
    assert (spinn_utilities_parts[1] <= spinn_machine_parts[1])


if __name__ == '__main__':
    test_compare_versions()
