

from pynlfff.pyplot import plot3d


if __name__=="__main__":
    print("start test")
    di = {
        "figsize": (6, 6)
    }
    # d3_drawer = NlfffPlotD3CutCake(**di)
    d3_drawer = plot3d.NlfffPlotD3CutCake(figsize=(6, 6))
    data_hdf_path = r"C:\Users\Zander\PycharmProjects\pynlfff\test_data\product\product1\Bxyz.h5"
    picture_path = r"C:\Users\Zander\PycharmProjects\pynlfff\test_data\product\product1\NlfffPlotD3CutCake.png"
    load_result = d3_drawer.load_data_hdf(data_hdf_path)
    if load_result:
        d3_drawer.colormap_mirror = True
        # d3_drawer.colormap_alpha = 0.5
        d3_drawer.add_cut("Bz", "Nx")
        d3_drawer.add_cut("Bz", "Ny")
        d3_drawer.add_cut("Bz", "Nz")
        d3_drawer.add_cut("Bz", "Nz", cut_num=0)
        d3_drawer.add_cut("Bz", "Nx", cut_percent=0.3)
        d3_drawer.add_cut("Bz", "Nz", cut_percent=0.2)
        d3_drawer.run_cut()
        d3_drawer.savefig(picture_path)
        d3_drawer.show()
        d3_drawer.close_data_hdf()