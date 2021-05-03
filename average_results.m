%This code averages the performance metric results of
%selected algorithms for selected dataset parts
%Alternatively, you could copy individual simulation results
%( sim_results\cbr\bbb\sim_results1 and
%sim_results\cbr\bbb\sim_results1) and save as
%sim_results/overall_result1 and sim_results/overall_result1
%to compare the results of first two algorithm for big buck
%bunny constant bitrate only.
%In the next step you should run displayResults.m file
clc
clear all

adapt_list=[1,2];
vbr_dir=["sim_results/vbr/bbb/","sim_results/vbr/tos/","sim_results/vbr/sintel/"];
cbr_dir=["sim_results/cbr/bbb/","sim_results/cbr/tos/","sim_results/cbr/sintel/"];
overall_dir=[vbr_dir cbr_dir];
sim_name="sim_results";
output_dir=["sim_results/overall_result","sim_results/vbr_result","sim_results/cbr_result"];


for adapt = adapt_list
    for vbr = 1:length(vbr_dir)
        vbr_files(vbr)=strcat(vbr_dir(vbr),sim_name,string(adapt),".mat");
    end
    for cbr = 1:length(cbr_dir)
        cbr_files(cbr)=strcat(cbr_dir(cbr),sim_name,string(adapt),".mat");
    end
    overall_files=[vbr_files,cbr_files];
    
    file_group={overall_files,vbr_files,cbr_files};
    
    for cycle=1:3
        files=file_group{cycle};
        load(files(1));
        mat_files=eval(strcat('dict',string(adapt)));
        
        for i=2:length(files)
            load(files(i));
            mat_files = [mat_files eval(strcat('dict',string(adapt)))];
        end

        names =  fieldnames(mat_files(1));
        for i = 1:numel(names)
            for j=1:length(files)
                if j==1
                    avg_mat{i}=getfield(mat_files(1),names{i});
                end
                value{i,j} = getfield(mat_files(j),names{i});
            end
        end

        for i = 1:numel(names)
            for j=2:length(files)
                avg_mat{i} = avg_mat{i} + value{i,j};
            end
        end

        for i = 1:numel(names)
            avg_mat{i}=avg_mat{i}/length(files);
        end

        names =  fieldnames(mat_files(1));
        for i = 1:numel(names)
            %dict1 = setfield(dict1,names{i},avg_mat{i});
            command=strcat("dict",string(adapt)," = setfield(dict",string(adapt),",names{i},avg_mat{i})");
            eval(command);
        end
        out_file_name=strcat(output_dir(cycle),string(adapt),".mat");
        %save(out_file_name,dict1)
        command=strcat("save(out_file_name,'dict",string(adapt),"')");
        eval(command);
    end
end
      
