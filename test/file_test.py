
from pynlfff.pyproduct import file

if __name__=="__main__":
    print("test")
    bout_bin_path = r"C:\Users\Zander\PycharmProjects\pynlfff\test_data\product\product0\Bout.bin"
    grid_path = r"C:\Users\Zander\PycharmProjects\pynlfff\test_data\product\product0\grid3.ini"
    h5_path = r"C:\Users\Zander\PycharmProjects\pynlfff\test_data\product\product0\Bxyz.h5"

    r = file.NlfffFile()
    s = r.get_size_from_grid(grid_path)
    print(s)

    s = r.read_bin(bout_bin_path, grid_path)
    print(s)

    print(s.shape)
    # z准确
    # z可以确定大概
    r.tran_bin2hdf5(bout_bin_path, grid_path, h5_path)