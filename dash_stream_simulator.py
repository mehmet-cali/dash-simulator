import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random
import time
import os
import scipy.io
import timeit
import sys


start = timeit.default_timer()

# Parameters and variables that are needed during the streaming process of each adaptation
# An instance of this class should be created for each adaptation
class stream_parameters:
    def __init__(self,ssim,file_size):
        self.ssim=ssim
        self.file_size=file_size
        self.layerNum, self.segmentNum = ssim.shape
        self.downloadedSegments = np.zeros((self.layerNum, self.segmentNum), dtype=int)
        self.downloadedLastSegment = -1 * np.ones(self.layerNum, dtype=int)
        self.downloadedLastLayer = -1 * np.ones(self.segmentNum, dtype=int)
        # Units of the time varibles are seconds
        self.t_seg = 2
        self.t_buf = 0  # total buffered video time
        self.t_act = 0  # actual time from the start of first download(time at the throughput graph)
        self.t_int = 0  # total interrupt time
        self.low_buf_num_cur = np.zeros(5,
                                   dtype=int)  # current low buffer detection number, buffer measurement num between (index,index+1) seconds
        self.t_play = 0  # playback time
        self.t_st = 15  # initial buffering time
        self.S = 0  # steamed file size starting from the last actual time calculation
        self.ini = 0  # initial time index for search
        self.avg_bitrate = file_size.mean(axis=1)/self.t_seg
        self.avg_bitrate = np.cumsum(self.avg_bitrate)
        self.cumsum_filesize=file_size.cumsum(axis=0)

    def init_vars(self):
        self.t_buf = 0  # total buffered video time
        self.t_act = 0  # actual time from the start of first download(time at the throughput graph)
        self.t_int = 0
        self.low_buf_num_cur.fill(0)
        self.t_play = 0  # playback time
        self.S = 0  # steamed file size starting from the last actual time calculation
        self.ini = 0  # initial time index for search
        self.downloadedLastSegment.fill(-1)
        self.downloadedLastLayer.fill(-1)
        self.downloadedSegments.fill(0)

# Parameters and variables that are needed during the streaming process of each adaptation
# An instance of this class should be created for each adaptation
class evaluation_variables:
    def __init__(self):
        self.mean_ssim = np.zeros((5, 5, 4, 10))
        self.var_ssim = np.zeros((5, 5, 4, 10))
        self.omitted_chunk_size = np.zeros((5, 5, 4, 10))
        self.interrupt_time = np.zeros((5, 5, 4, 10))
        self.low_buf_detect_num = np.zeros((5, 5, 4, 10, 5), dtype=int)

    def save_results(self, sp, i1, i2, i3, i4, min_play):
        min_play_segment = int(min_play / sp.t_seg)  # final segment to evaluate
        ssimw = np.zeros(min_play_segment + 1)
        for i in range(min_play_segment + 1):
            ssimw[i] = sp.ssim[sp.downloadedLastLayer[i]][i]
        self.mean_ssim[i1, i2, i3, i4] = round((sum(ssimw) / len(ssimw)), 6)
        self.var_ssim[i1, i2, i3, i4] = round(np.var(ssimw), 6)
        self.interrupt_time[i1, i2, i3, i4] = sp.t_int
        self.low_buf_detect_num[i1, i2, i3, i4, :] = sp.low_buf_num_cur[:]
        self.omitted_chunk_size[i1, i2, i3, i4] = 0  # kbytes
        for j in range(min_play_segment + 1, sp.downloadedLastSegment[0]):
            for i in range(0, sp.layerNum):
                if sp.downloadedSegments[i, j] == 1:
                    self.omitted_chunk_size[i1, i2, i3, i4] += sp.file_size[i, j] // 1024

image_list = []
time_list = []

#Streaming process illusturation variables
figure_num = 0
figBorder = 25
figMargin = 9

debug=False
#debug=True
debug2=False
#debug2=True
debug3=False
#debug3=True
displayStreamingProcess=True


#Saves downloaded segments to image list (called after each download if desired)
def saveDownloadedSegments(sp):
    global image_list
    global time_list
    time_list.append(sp.t_play)
    playSegment = sp.t_play/sp.t_seg
    reverse = sp.downloadedSegments[::-1]
    reverse2 = np.array(reverse)
    lowerbound = int(playSegment/(figBorder-figMargin))*(figBorder-figMargin)
    upperbound = lowerbound + figBorder
    reverse3 = reverse2[:, lowerbound:upperbound].copy()
    image = reverse3.copy()
    image_list.append(image)

#Cumulative sum of throughput waveform
def cumulative(b):
    sum=0
    B=np.zeros(len(b)+1)
    for i in range(len(b)+1):
        for j in range(i):
            sum=sum+b[j]
        B[i]=sum
        sum=0
    return B

#Searches the cumulative throughput waveform and returns the current position in the waveform
def searchThr(ini,S): #returns the index a
    # ini: initial time index to start the search
    for i in range(ini,len(cumulative_throughput)):
        if cumulative_throughput[i]>S:
            return i-1

#Simulates downloading a segment
def download(sp,l,s,playing):
    if sp.segmentNum<=s:
        return False
    sp.S = sp.S + sp.file_size[l, s]
    if l==0:
        sp.t_buf=sp.t_buf+sp.t_seg
    ##########################
    if not(p2a_time(sp, sp.S, playing)):
        if l == 0:
            sp.t_buf = sp.t_buf - sp.t_seg
        return False
    if sp.downloadedLastSegment[l]<s:
        sp.downloadedLastSegment[l] = s
    if sp.downloadedLastLayer[s]<l:
        sp.downloadedLastLayer[s] = l
    sp.downloadedSegments[l,s] = 1

    if debug2:
        print("seg:" + str(s))
        print("layer="+str(l))
        print("segment=" + str(s))
        print("-----------------")
    if displayStreamingProcess:
        saveDownloadedSegments(sp)
    return True



def p2a_time(sp,S,playing): #conversion of playback to actual time
    i=searchThr(sp.ini,S)
    if i==None:
        return False
    # residual time calculation using interpolation
    if debug2:
        print("S="+str(S))
        print("cumulative_throughput="+str(cumulative_throughput[i]))
        print(i)
    inc=i+(S-cumulative_throughput[i])/(cumulative_throughput[i+1]-cumulative_throughput[i])-sp.t_act #increment from previous t_act
    sp.t_act=sp.t_act+inc
    sp.ini=int(sp.t_act)
    if playing:
        sp.t_play=sp.t_play+inc
        sp.t_buf=sp.t_buf-inc
        if sp.t_buf < 0:
            sp.t_int = sp.t_int - sp.t_buf
            sp.t_play = sp.t_play + sp.t_buf
            sp.t_buf=0
        elif sp.t_buf<5:
            sp.low_buf_num_cur[int(sp.t_buf)]+=1

    if debug:
        print("inc=" + str(inc))
        print("t_buf="+str(sp.t_buf))
        print("t_play=" + str(sp.t_play))
        print("t_act=" + str(sp.t_act))
        print("videoplaysegment=" + str(int(sp.t_play/sp.t_seg)))
    return True

def adjust_omit_param(error,par):
    #par is the parameter to control
    k=0.01*par
    ki=0.02
    kd=0.01
    #Used to equalize omitted chunk size of both algorithms
    try:
        adjust_omit_param.error_sum+=error
    except AttributeError:
        adjust_omit_param.error_sum = 0
    try:
        d_error=error-adjust_omit_param.last_error
    except AttributeError:
        d_error = 0
    adjust_omit_param.last_error = error
    #Since the variable is desired buffer related constant
    return k*error+ki*adjust_omit_param.error_sum-kd*d_error


def ssimWaveform(sp):
    ssimw=np.zeros(sp.downloadedLastSegment[0]+1)
    for i in range(sp.downloadedLastSegment[0]+1):
        ssimw[i]=sp.ssim[sp.downloadedLastLayer[i]][i]
    #print(ssimw.shape)
    print(round((sum(ssimw)/len(ssimw)),6))
    print(round(np.var(ssimw),6))

# if you run this you need to manually stop the execution because it lasts very long (just to see the download process)
def save_fig(sp,i,filename):
    global figure_num
    figure_num = figure_num +1

    image = image_list[i]
    segment = time_list[i]/sp.t_seg
    fig = plt.figure(figsize=(15, 7))
    ax = fig.add_subplot(1, 1, 1)

    # Major ticks every 20, minor ticks every 5
    major_ticks = np.arange(0, 500, 1)
    minor_ticks = np.arange(0.5, 505, 1)
    minor_ticks_y = np.arange(0.5, 4.5, 1)

    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.set_yticks(major_ticks)
    ax.set_yticks(minor_ticks_y, minor=True)

    # And a corresponding grid
    ax.grid(which='both')

    # Or if you want different settings for the grids:
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0)
    ax.tick_params(axis='both', labelsize=13)

    plt.grid(color='r', linestyle='-', linewidth=1, which='minor', alpha=0.2)

    lowerbound = int(segment/(figBorder-figMargin))*(figBorder-figMargin)
    upperbound = lowerbound +figBorder

    plt.imshow(image, extent=(-0.5+lowerbound, upperbound- 0.5, -0.5, sp.layerNum+ -0.5))
    '''plt.annotate('Playback position', xy=(segment, 1), xycoords='data',
                 xytext=(0.5, 0.5), textcoords='figure fraction',
                 arrowprops=dict(arrowstyle="->"))'''
    #plt.scatter(25, 2, s=500, c='red', marker='o')
    plt.xlabel('Segments',fontsize=18)
    plt.ylabel('Layers',fontsize=18)
    if segment != 0:
        plt.axvline(x=segment,linewidth=1.5, label='Playback Position')
        plt.legend(loc='upper left',fontsize=16)
    # f.show()
    plt.savefig(filename+'/figures/fig'+str(figure_num).zfill(3)+'.png')
    plt.close(fig)


# Functions of Adaptation Algorithm ###########################################
# doi: 10.1007/s11760-020-01646-y #############################################
def averageBaseSSIM(sp):
    sum=0
    for i in range(sp.segmentNum):
        sum=sum+sp.ssim[0,i]
    return sum/float(sp.segmentNum)

def setbminbmax(sp,b_min_init,b_max_init):
    b_min = b_min_init + b_min_init * (sp.t_seg - 1) * 0.6
    b_max = b_max_init + b_max_init * (sp.t_seg - 1) * 0.6
    return b_min,b_max

def averageBufferQF(sp, ssimCoef, d_marg):
    qfSum=0
    counter=0
    for i in range(int(sp.t_play/sp.t_seg)+int(d_marg/sp.t_seg)+1,sp.downloadedLastSegment[0]+1):
        for j in range(sp.layerNum-1,-1,-1):
            if sp.downloadedSegments[j,i]==1:
                counter=counter+1
                qfSum=qfSum+ssimCoef*sp.ssim[j,i]+j
                if debug3:
                    print("qfSum="+str(qfSum))
                    print("counter="+str(counter))
                break
    return qfSum/(counter+0.00001)

def segmentLayerwithMaxPF(sp, d_marg):
    segmentMin=0
    layerMin=0
    pFMargin=0.001
    layerCoef=0.2
    priorityFactor=0
    maxPriorityFactor=priorityFactor
    for i in range(int(sp.t_play/sp.t_seg)+int(d_marg/sp.t_seg)+1,sp.downloadedLastSegment[0]+1):
        for j in range(1,sp.layerNum):
            if(sp.downloadedSegments[j,i])==0:
                priorityFactor=sp.ssim[j,i]-sp.ssim[j-1,i]+layerCoef/j
                if priorityFactor>maxPriorityFactor+pFMargin:
                    maxPriorityFactor=priorityFactor
                    segmentMin=i
                    layerMin=j
                break
    return segmentMin,layerMin

def minimumBufferLevel(sp,b_min,b_max,d_marg):
    ssimCoef=2.0
    qf_max=ssimCoef+sp.layerNum-1
    qf_min=averageBaseSSIM(sp)*ssimCoef
    if debug3:
        print("1:" + str((b_max - b_min)))
        print("2:" + str((averageBufferQF(sp,ssimCoef,d_marg) - qf_min)))
        print("3:"+str((b_max-b_min)*(averageBufferQF(sp,ssimCoef,d_marg)-qf_min)))
        print("4:" + str((qf_max - qf_min)))
        print("5:" + str(((b_max - b_min) * (averageBufferQF(sp,ssimCoef,d_marg) - qf_min)) / (qf_max - qf_min)))
    minBufferTime=b_min+((b_max-b_min)*(averageBufferQF(sp,ssimCoef,d_marg)-qf_min))/(qf_max-qf_min)
    if minBufferTime<b_min:
        return b_min
    else:
        return minBufferTime

#############################################################################



#Test Adaptation Algorithm###################################################
# doi: 10.1007/s11760-020-01646-y ###########################################
def adaptation1(sp):
    d_marg = 6 #6 seconds margin to ensure the downloading segment will not be played
    b_min,b_max=setbminbmax(sp,9,20)
    # Adaptation loop
    while 1:
        if (sp.t_buf < minimumBufferLevel(sp,b_min,b_max,d_marg)) and (sp.downloadedLastSegment[0] < sp.segmentNum - 1):
            segment = sp.downloadedLastSegment[0] + 1
            layer = 0
            if not (download(sp, layer, segment, playing=True)):
                break #End of throughput
        else:  # for enhancement
            segment, layer = segmentLayerwithMaxPF(sp, d_marg)
            if layer != 0 and segment != 0:
                if not (download(sp, layer, segment, playing=True)):
                    break #End of throughput
            else:
                # Buffer overflow condition may be added here if desired
                segment = sp.downloadedLastSegment[0] + 1
                layer = 0
                if not (download(sp, layer, segment, playing=True)):
                    break #End of throughput

########################################################################
# Second adaptation algorithm to test #####################################
def adaptation2(sp): #Minimum buffer parameter is selected to equalize omitted chunk sizes if needed
    try:
        adaptation2.buf_pid
        # print("buf_pid......: "+str(adaptation2.buf_pid))
    except AttributeError:
        adaptation2.buf_pid = 20.17
    while 1:
        if sp.t_buf<adaptation2.buf_pid:
            segment = sp.downloadedLastSegment[0] + 1
            layer = 0
            if not (download(sp, layer, segment, playing=True)):
                break #End of throughput
        else:
            segment=sp.downloadedLastSegment[0]
            if sp.downloadedLastLayer[segment]<sp.layerNum-1:
                layer=sp.downloadedLastLayer[segment]+1
                if not (download(sp, layer, segment, playing=True)):
                    break  # End of throughput
            else:
                segment+=1
                layer=0
                if not (download(sp, layer, segment, playing=True)):
                    break  # End of throughput



#Test Start######################################################
# a parameter of adapt_list=[1,3] simulates functions named "adaptation1" "adaptation3" but make sure the functions exist
# and make sure the reference adaptation (adaptation whose desired buffer size keeps the same and the others' buffer
# related parameter keeps changing according to PID controler) is the first element in the list here: "adaptation1"
def simulate(adapt_list=[1,2], ssim_file="ssim.csv", size_file="sizes.csv",out_file="sim_results"):
    global cumulative_throughput
    mat = scipy.io.loadmat('thr180.mat')
    #Default omitted video size equaliztion iteration option
    omit_iter=10
    des_omit_dif=0.5 #percentage to the streamed video size
    cycle_counter=0
    #python dash_stream_simulator.py <number_of_adaptation> <ssimpath> <filesizepath>


    ssim = np.genfromtxt(ssim_file, delimiter=";").transpose()
    filesize = np.genfromtxt(size_file, delimiter=";").transpose()
    cumulative_throughput = []


    #list of streaming parameters and evaluation variables objects
    sp = []
    ev = []
    for adapt in range(len(adapt_list)):
        sp.append(stream_parameters(ssim,filesize))
        ev.append(evaluation_variables())

    for o in range(omit_iter):
        cycle_counter+=1
        for i1 in range(5):
            for i2 in range(5):
                for i3 in range(4):
                    for i4 in range(10):
                        b_16bit = mat['throughput'][i1][i2][i3][i4][:]
                        b = b_16bit.astype('uint32')
                        b = b * 125  # kbit/s to byte/s conversion
                        cumulative_throughput = cumulative(b)

                        t_play_end=[]
                        for a in range(len(adapt_list)):
                            sp[a].init_vars()
                            # Initial buffering
                            for i in range(int(sp[a].t_st / sp[a].t_seg) + 1):
                                # Download from lowest layer for initial buffering
                                download(sp[a], 0, i, playing=False)
                            # playback starts
                            sp[a].t_play = 0
                            #make sure the adapt_list only include the function numbers that exist in this document
                            adaptation = globals()['adaptation'+str(adapt_list[a])]
                            adaptation(sp[a])
                            t_play_end.append(sp[a].t_play)
                        t_play_end_min = min(t_play_end)
                        for a in range(len(adapt_list)):
                            ev[a].save_results(sp[a], i1, i2, i3, i4, t_play_end_min)

        for a in range(len(adapt_list)):
            # print("omit instance: " + str(ev1.omitted_chunk_size[i1, i2, i3, i4]))
            dict = {'mean_ssim': ev[a].mean_ssim, 'var_ssim': ev[a].var_ssim, 'interrupt_time': ev[a].interrupt_time,
                    'omitted_chunk_size_kb': ev[a].omitted_chunk_size,
                    'low_buf_detect_num': ev[a].low_buf_detect_num}
            scipy.io.savemat(out_file + str(adapt_list[a]) + ".mat", {'dict'+str(adapt_list[a]): dict})
            v = sp[a].downloadedSegments[:, 0:sp[a].downloadedLastSegment[0] + 2].transpose()
            np.savetxt(out_file + "-downloadedSegments" + str(a+1) + ".csv", v, fmt='%d', delimiter=";")


        #print("cumulative throughput: " + str(cumulative_throughput[len(cumulative_throughput) - 1] / 1024))
        if len(adapt_list)>=2:
            omit_mean = []
            for a in range(len(adapt_list)):
                omit_mean.append(np.mean(ev[a].omitted_chunk_size))
            #As the first element in adapt_list stands for id of the reference adaptation the PID control is set
            # according to first one
            cur_omit_dif=[]
            pid_flag=True # if all of the adaptations reach des_omit_dif
            for a in range(1,len(adapt_list)):
                cur_omit_dif.append((omit_mean[0] - omit_mean[a]) * 100 / (
                        cumulative_throughput[len(cumulative_throughput) - 1] / 1024))
                print("cur_omit_dif of adaptation" + str(adapt_list[a]) + ": " + str(cur_omit_dif[a - 1]))
                print("des_omit_dif: " + str(des_omit_dif))
                if abs(cur_omit_dif[a - 1]) < des_omit_dif:
                    continue
                else:
                    pid_flag = False
                    adaptation = globals()['adaptation' + str(adapt_list[a])]
                    omit_param = adjust_omit_param(cur_omit_dif[a - 1], adaptation.buf_pid)
                    adaptation.buf_pid += omit_param
                    print("current omit param for adaptation " + str(adapt_list[a]) + ": " + str(adaptation.buf_pid))
            if pid_flag:
                break
        else:
            break


    end = timeit.default_timer()
    print("Cycle num: "+str(cycle_counter))
    print("Run time: "+ str(end - start))

def main():
    arguments=[]
    for i in range(len(sys.argv)-1):
        arguments.append(sys.argv[i+1])
    if not arguments:
        simulate()
    else:
        simulate(*arguments)

if __name__=="__main__":
    main()