clc
clear all

fprintf(strcat("Evaluation selection\n", ...
"Adaptation comparison or Adaptation evaluation ....... 1\n", ...
"Dataset comparison (CBR,VBR) ....... 2\n"))
sel0=input("Select Evaluation mode: ");



if sel0 == 2
    fprintf("Select adaptation:\n");
    files=dir('sim_results/cbr_result*');
    for i=1:length(files)
        filename=files(i).name;
        fprintf(strcat("--Adaptation-",string(filename(15)), ....
            ".......",string(filename(11)),"\n"))
    end
else
    fprintf("Select adaptation/s:\n");
    files=dir('sim_results/overall*');
    for i=1:length(files)
        filename=files(i).name;
        fprintf(strcat("--Adaptation-",string(filename(15)), ....
            ".......",string(filename(15)),"\n"))
    end
    fprintf("For multiple selection type [1,3] for first and third algorithm\n");
end

adapt_list=input('');


load('thr_range')
if sel0 == 2
    if length(adapt_list)>1
        error("Choose single adaptation for dataset comparison")
    else
        load(strcat('sim_results/cbr_result',string(adapt_list),'.mat'));
        sim_results(1)=eval(strcat('dict',string(adapt_list)));
        load(strcat('sim_results/vbr_result',string(adapt_list),'.mat'));
        sim_results(2)=eval(strcat('dict',string(adapt_list)));
        %From now on it is no different than comparing two
        %adaptations
        adapt_list=[1,2];
    end
else
    if length(adapt_list)==1
        load(strcat('sim_results/overall_result',string(adapt_list),'.mat'));
        sim_results=eval(strcat('dict',string(adapt_list)));
    else
    for i = 1:length(adapt_list)
        load(strcat('sim_results/overall_result',string(adapt_list(i)),'.mat'));
        sim_results(i)=eval(strcat('dict',string(adapt_list(i))));
    end
    end
end
        
fprintf(strcat("---------------\n", ...
"Output selection\n", ...
"Mean SSIM ...... 1\n", ...
"Variance SSIM ...... 2\n", ...
"Interrupt Time ...... 3\n", ...
"Omitted Chunk Size ...... 4\n", ...
"Low buffer Detection ...... 5\n"))
sel1=input("Select one of the outputs to display: ");

switch sel1
    case 1
        if length(adapt_list)==1
            output=sim_results.mean_ssim;
        else
        output=zeros([length(adapt_list),size(sim_results(1).mean_ssim)]);
        for i = 1:length(adapt_list)
            output(i,:,:,:,:)=sim_results(i).mean_ssim;
        end
        end
        output_label="Mean SSIM";
    case 2
        if length(adapt_list)==1
            output=sim_results.var_ssim;
        else
        output=zeros([length(adapt_list),size(sim_results(1).var_ssim)]);
        for i = 1:length(adapt_list)
            output(i,:,:,:,:)=sim_results(i).var_ssim;
        end
        end
        output_label="Variance SSIM";
    case 3
        if length(adapt_list)==1
            output=sim_results.interrupt_time;
        else
        output=zeros([length(adapt_list),size(sim_results(1).interrupt_time)]);
        for i = 1:length(adapt_list)
            output(i,:,:,:,:)=sim_results(i).interrupt_time;
        end
        end
        output_label="Interrupt time (s)";
    case 4
        if length(adapt_list)==1
            output=sim_results.omitted_chunk_size_kb;
        else
        output=zeros([length(adapt_list),size(sim_results(1).omitted_chunk_size_kb)]);
        for i = 1:length(adapt_list)
            output(i,:,:,:,:)=sim_results(i).omitted_chunk_size_kb;
        end
        end
        output_label="Omitted chunk size";
    case 5
        if length(adapt_list)>=2
            error("Only single adaptation mode is allowed for this output")
        end
        output=sim_results.low_buf_detect_num;
        output_label="Low buffer detection number";
        axis_tick_label2={};
        axis_label2="Buffer range (s)";
        axis_tick2=0:5;
        axis_val2=mean([axis_tick2(1:end-1);axis_tick2(2:end)]);
            for tick = axis_tick2
                axis_tick_label2{end+1}=strcat("(",num2str(tick-1),",",num2str(tick),")");
            end
    otherwise
        sel1=1;
        if length(adapt_list)==1
            output=sim_results.mean_ssim;
        else
        output=zeros([length(adapt_list),size(sim_results(1).mean_ssim)]);
        for i = 1:length(adapt_list)
            output(i,:,:,:,:)=sim_results(i).mean_ssim;
        end
        end
        output_label="Mean SSIM";
end

if length(sel1)~=1
    error("Select one of the outputs")
end
fprintf(strcat("--------------\n", ...
"Throughut parameters:\n", ...
"Mean 1\n", ...
"Variance 2\n", ...
"Stationarity 3\n"))
if length(adapt_list)==1 && sel1~=4
    sel2=input("Select one or two of the throughut parameters: ");
else
    sel2=input("Select one or two of the throughut parameters: ");
end
if (sel1==4 && length(sel2)>1) || (length(adapt_list)==2 && length(sel2)>1)
    fprintf(strcat("Multiple parameter selection is not allowed in this mode\n", ...
        "only the first element will be used"))
    sel2=sel2(1);
end

%Set X axis properties for single and double parameter disp.
if length(sel2)==1 || length(sel2)==2
    bar_width=0.5;
    switch sel2(1)
        case 1
            axis_tick=thr_range.mu;
            axis_tick_label=0;
            axis_label="Mean throughput (kbit/s)";
        case 2
            axis_tick=thr_range.sigma_coef;
            axis_tick_label={};
            for tick = axis_tick
                axis_tick_label{end+1}=strcat(num2str(tick),"\mu");
            end
            axis_label="Standard deviation of throughput";
        case 3
            axis_tick=thr_range.stat;
            axis_tick_label=0;
            axis_label="Stationarity of throughput";
        otherwise
            sel2=1;
            axis_tick=thr_range.mu;
            axis_tick_label=0;
            axis_label="Mean throughput (kbit/s)";
    end
    axis_val=mean([axis_tick(1:end-1);axis_tick(2:end)]);
else
    error("Select one of two of the options(Ex: 1 [2,3] 3 etc.)")
end
% Set Y axis properties for double feature parameter display
if length(sel2)==2
    bar_width=0.3;
    switch sel2(2)
        case 1
            axis_tick2=thr_range.mu;
            axis_tick_label2=0;
            axis_label2="Mean throughput";
        case 2
            axis_tick2=thr_range.sigma_coef;
            axis_tick_label2={};
            for tick2 = axis_tick2
                axis_tick_label2{end+1}=strcat(num2str(tick2),"\mu");
            end
            axis_label2="Standard deviation of throughput";
        case 3
            axis_tick2=thr_range.stat;
            axis_tick_label2=0;
            axis_label2="Stationarity throughput";
    end
    axis_val2=mean([axis_tick2(1:end-1);axis_tick2(2:end)]);
elseif sel1==5
       bar_width=0.3;
end

%Sum the output over selected parameter axes
thr_list=[1,2,3,4];
[values,idx] = intersect(thr_list,sel2,'stable');
thr_list=thr_list(setdiff(1:end,idx))

if length(adapt_list)==1
    for i = 1:length(thr_list)
        output=mean(output,thr_list(i));
    end
    output=squeeze(output);
else
    output_temp=squeeze(output(1,:,:,:,:));
    for i = 1:length(thr_list)
        output_temp=mean(output_temp,thr_list(i));
    end
    o1=squeeze(output_temp)
%     new_output=zeros([size(o1'),length(adapt_list)]);
%     if sum(size(o1)>1)==1
%         new_output(:,1)=o1';
%     elseif sum(size(o1)>1)==2
%         new_output(:,:,1)=o1';
%     end
    if isrow(o1)
        new_output=o1';
    else
        new_output=o1;
    end
    for a = 2:length(adapt_list)
        output_temp=squeeze(output(a,:,:,:,:));
        for i = 1:length(thr_list)
            output_temp=mean(output_temp,thr_list(i));
        end
        o1=squeeze(output_temp)
%         if sum(size(o1)>1)==1
%             new_output(:,a)=o1';
%         elseif sum(size(o1)>1)==2
%             new_output(:,:,a)=o1';
%         end
        if isrow(o1)
            new_output=[new_output,o1'];
        else
            new_output=[new_output,o1];
        end
        
    end
    output=new_output;
end




% output_temp=output(a,:,:,:,:);
% for i = 1:length(thr_list)
%     output_temp=mean(output_temp,thr_list(i));
% end
% o=squeeze(output_temp);
% s
% for a = adapt_list
%     
% end
% sq_size=size(squeeze(output(a)));
% str=":";
% if length(size(sq_size))>1
%     for s = sq_size
%         str=strcat(str,",:");
%     end
% end
% o=zeros([max(adapt_list),sq_size]);
% for a = adapt_list
%     eval(strcat("o(a,",str,")=squeeze(output(a))"));
% end
% if length(adapt_list)>1
%     if isrow(o(adapt_list(1)))
%         for a = adapt_list
%             eval(strcat("o(a,",str,")=o(a,",str,")'"));
%         end
%     end
%     output=eval(strcat("o(1,",str,")"));
%     for a = 2:length(adapt_list)
%         output=[output,eval(strcat("o(a,",str,")"))];
%     end
% else
%     output=o(adapt_list);
% end


if length(sel2)==1 && sel1~=5 %single parameter plot options
    b=bar(axis_val,output,bar_width);
    xticks(axis_tick)
    if sel2(1)==2
        xticklabels(axis_tick_label)
    end
    xlabel(axis_label)
    ylabel(output_label)
    if sel2==1 %if mean ssim
        axis([min(axis_tick)*0.95,max(axis_tick)*1.03,min(output(:))/1.2,max(output(:))*1.01])
    else
        %axis([-inf,inf,min(output(:))/1.2,max(output(:))*1.01])
        axis([min(axis_tick)*0.95,max(axis_tick)*1.03,-inf,max(output(:))*1.01])
    end
else %double parameter plot options
    bar3d=bar3(axis_val,output,bar_width);
    %yticks(axis_tick)
    set(gca,'YTick',axis_tick)
    set(gca,'YTickLabel',axis_tick)
    if sel2(1)==2
        set(gca,'YTickLabel',axis_tick_label)
    end
    ylabel(axis_label)
    %xticks(axis_tick2)
    %set(gca,'XTick',axis_tick2)
    set(gca,'XTickLabel',axis_tick2)
    if length(sel2)==2
        if sel2(2)==2
            set(gca,'XTickLabel',axis_tick_label2)
        end
    end
%     if sel1==5
%         set(gca,'XTickLabel',axis_tick_label2)
%     end
    xdata=get(bar3d,'XData');
    xL = get(gca,'XLim');
    axis tight
    for ii=1:length(xdata)
        xdata{ii}=xdata{ii}+(0.5*(xL(2)-xL(1))/length(axis_val2))*ones(size(xdata{ii}));
        set(bar3d(ii),'XData',xdata{ii});
    end
    xlabel(axis_label2)
    zlabel(output_label)
    xL = get(gca,'XLim');
     axis([xL(1)-0.5*(xL(2)+xL(1))/length(axis_val2),xL(2)+0.5*(xL(2)-xL(1))/length(axis_val2), ...
         axis_tick(1),axis_tick(end), ...
         min(output(:))/1.4,max(output(:))*11/10])
    %axis([-0.1,inf,-inf,inf,min(output(:))/1.4,max(output(:))*11/10])
end