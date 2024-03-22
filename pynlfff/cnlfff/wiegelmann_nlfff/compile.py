

def run(device="cpu"):
    
    import os

    # 获取当前脚本的相对路径
    script_relative_path = __file__

    # 获取当前脚本的绝对路径
    script_absolute_path = os.path.abspath(script_relative_path)

    print("当前脚本的绝对路径:", script_absolute_path)
    
    bash_script_absolute_dir=os.path.dirname(script_absolute_path)
    
    bash_gpu=os.path.join(bash_script_absolute_dir,"init_compile_ps.sh")
    bash_cpu=os.path.join(bash_script_absolute_dir,"init_compile.sh")
    
    if device=="cpu":
        os.system("bash {}".format(bash_cpu))
    else:
        os.system("bash {}".format(bash_gpu))
