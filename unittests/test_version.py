import spinn_utilities
import spinn_storage_handlers


def test_import_all():
    spinn_utilities_parts = spinn_utilities.__version__.split('.')
    spinn_storage_handlers_parts = spinn_storage_handlers.\
        __version__.split('.')

    assert (spinn_utilities_parts[0] == spinn_storage_handlers_parts[0])
    assert (spinn_utilities_parts[1] <= spinn_storage_handlers_parts[1])


if __name__ == '__main__':
    test_import_all()
