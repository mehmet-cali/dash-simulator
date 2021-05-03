# DASH Stream Simulator with Throughput Generator

In this project, a fast DASH simulator that works on scalable DASH datasets is designed. Also, a throughput generator is designed to produce waveforms according to desired mean, variance and stationarity. The throughput generator and function that graphically demonstrates the results are written in Matlab, wheras the simulator code is writen in Python.
 
## Instructions

### Project execution order

 The simulator needs three main inputs which are,
 
 * SSIM values of each video chunk (stored in a file named ssim.csv where rows represent segments, columns represent layers)
 * File size of each video chunk (stored in a file named sizes.csv where rows represent segments, columns represent layers) (values are in bytes)
 * Throughput waveforms which are obtained from monte_throughput_gen.m (stored in a file named 'thr180.mat')
 
 Since there exist a default throughput dataset in the repository which is named as thr180.mat, the simulator can be executed directly from "dash_steam_simulator.py" file. In addition, waveform dataset with desired parameter variation can be generated from "monte_throughput_gen.m" to replace thr180.mat.
 
 To simulate the algorithms for overall dataset simulate_dataset.py should be executed. It basicly calls simulate function in dash_steam_simulator.py for both encoding type (CBR and VBR) and for all videos (Big Buck Bunny, Sintel and Tears of Steel) which located in /dataset_info. It stores the output in /sim_results folder. Again, which adaptations to simulate can be chosen from the main function of simulate_dataset.py.
 
 To display the results stored in /sim_results, displayResults.m file should be run.
 
#### Adding a new adaptation algorithm

 New adaptation algorithms can be added by generating a new function to "dash_stream_simulator.py" file with a name "adaptation#". The program will test the adaptations that are in the variable "test_list", so the # sign should be replaced with an unused number and the "test_list" variable sould be arranged accordingly. 
 <br/> If multiple adaptation mode will be used, one of the adaptation should be selected as reference and the rest of them requires a parameter to adjust their desired buffer size according to PID controller. As the number of segments and the amount of bandwidth utilized are equilized using the PID controller and this enables much more reliable and fair testing of adaptation algorithms. The parameter that will be fed to PID controller should be initialized in an exception block as shown below:
````python
   try:
       adaptation2.buf_pid
   except AttributeError:
       adaptation2.buf_pid = 20
````
Inside the custom adaptation loop, the decisions can be made using the information gathered from the object of "stream_parameters" class (sp). This object includes variables of streaming process such as layerNum, segmentNum, ssim, downloadedSegments, downloadedLastSegment, downloadedLastLayer and some parameters that describes the playback position, segment duration etc. After adjusting the adaptation loop to make its decision according to stream_parameters object, downloading the selected video chunk should be simulated by calling the function named "download" with the arguments of sp, l, s, playing. Here sp, l, s, playing stand for stream_parameters object, selected layer index, selected segment index and playback state. Since the initial buffering process of all of the test adaptation algorithms are common, parameter playing should always be set to True while calling from the adaptation loop. When the total downloaded file size exceeds the cumulative throughput, "download" function returns False, which represents end of simulation. Therefore, this condition should be used as exit condition of adaptation loop.

#### Citation

If you use this project on your research, we kindly ask you to cite our following paper:
* Çalı, M., Özbek, N. Time-efficient evaluation of adaptation algorithms for DASH with SVC: dataset, throughput generation and stream simulator. SIViP (2021). https://doi.org/10.1007/s11760-021-01880-y

Also the adaptation1 in dash_steam_simulator.py belongs to:
* Çalı, M., & Özbek, N. (2020). SSIM-based adaptation for DASH with SVC in mobile networks. Signal, Image and Video Processing, 1-8.
