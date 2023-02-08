from .prepare_base import PrepareWorker




### demo test ###
def demo_fun_use_Bptr():
    # config
    p_raw_path = r"/media/zander/Data/now/work-inner/sun/LINFF/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bp.fits"
    t_raw_path = r"/media/zander/Data/now/work-inner/sun/LINFF/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bt.fits"
    r_raw_path = r"/media/zander/Data/now/work-inner/sun/LINFF/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Br.fits"
    sroot=r"/public1/home/sc81826/temp/out"
    # create object
    pre_worker = PrepareWorker()
    # pre
    pre_worker.prepare_from_fits_Bprt(p_raw_path,t_raw_path,r_raw_path,sroot)
    print("finish demo_fun_use_Bptr_local")

def demo_fun_use_afi():
    save_dir = r"/public1/home/sc81826/temp/out"
    dd=r"/public1/home/sc81826/archive/selAR/2019/hmi.sharp_720s.7334.20190124_124800_TAI"
    a=dd+"/hmi.sharp_720s.7334.20190124_124800_TAI.azimuth.fits"
    f=dd+"/hmi.sharp_720s.7334.20190124_124800_TAI.field.fits"
    i=dd+"/hmi.sharp_720s.7334.20190124_124800_TAI.inclination.fits"
    pre_worker = PrepareWorker()
    pre_worker.prepare_from_fits_afi(a,f,i,save_dir)
    print("finish demo_fun_use_afi_local")

def demo_fun_use_afid():
    save_dir = r"/public1/home/sc81826/temp/out"
    dd=r"/public1/home/sc81826/run/linff-main/run_space/tool/data"
    a=dd+"/hmi.sharp_720s.7300.20180823_173600_TAI.azimuth.fits"
    f=dd+"/hmi.sharp_720s.7300.20180823_173600_TAI.field.fits"
    i=dd+"/hmi.sharp_720s.7300.20180823_173600_TAI.inclination.fits"
    d=dd+"/hmi.sharp_720s.7300.20180823_173600_TAI.disambig.fits"
    pre_worker = PrepareWorker()
    pre_worker.prepare_from_fits_afid(a,f,i,d,save_dir)
    print("finish demo_fun_use_afi_local")


if __name__=="__main__":
    demo_fun_use_Bptr()
    demo_fun_use_afi()
    demo_fun_use_afid()




