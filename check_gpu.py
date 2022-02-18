# _*_ coding: UTF-8 _*_
# Author LBK
import pynvml

def check_gpu():
    output = {"type": "gpu_states", "data":[]}
    UNIT = 1024 * 1024

    pynvml.nvmlInit() #初始化
    # gpuDeriveInfo = pynvml.nvmlSystemGetDriverVersion()
    # print("Drive版本: ", str(gpuDeriveInfo, encoding='utf-8')) #显示驱动信息


    gpuDeviceCount = pynvml.nvmlDeviceGetCount()#获取Nvidia GPU块数
    # print("GPU个数：", gpuDeviceCount )


    for i in range(gpuDeviceCount):

        statu_tmp = {}

        handle = pynvml.nvmlDeviceGetHandleByIndex(i)#获取GPU i的handle，后续通过handle来处理

        memoryInfo = pynvml.nvmlDeviceGetMemoryInfo(handle)#通过handle获取GPU i的信息

        gpuName = str(pynvml.nvmlDeviceGetName(handle), encoding='utf-8')

        gpuTemperature = pynvml.nvmlDeviceGetTemperature(handle, 0)

        gpuFanSpeed = pynvml.nvmlDeviceGetFanSpeed(handle)

        gpuPowerState = pynvml.nvmlDeviceGetPowerState(handle)
        gpuPowerUsage = pynvml.nvmlDeviceGetPowerUsage(handle)
        gpuPowerCap = pynvml.nvmlDeviceGetEnforcedPowerLimit(handle)

        gpuUtilRate = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        gpuMemoryRate = pynvml.nvmlDeviceGetUtilizationRates(handle).memory

        statu_tmp["gpu"] = i + 1
        statu_tmp["name"] = gpuName
        statu_tmp["memory"] = str(memoryInfo.total//UNIT) + "MiB"
        statu_tmp["memory_usage"] = str(memoryInfo.used//UNIT) + "MiB"
        statu_tmp["power"] = str(gpuPowerUsage//1000) + "w"
        statu_tmp["power_cap"] = str(gpuPowerCap//1000) + "w"

        output["data"].append(statu_tmp)

    return output

if __name__ == "__main__":
    output = check_gpu()
    print(output)