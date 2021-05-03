
clear all
close all
clc

% slots:
% mu_final=[150 300] [300 450] [450 600] [600 750] [750 900]    5 intervals
% sigma_final= [0.1mu 0.2mu] [0.2mu 0.3mu] .. [0.5mu 0.6mu]   5 intervals
% stationarity_percentage_final= [0.15 0.3] .. [0.6 0.75]   4 intervl.
% Total 100 slots each of which will be filled with 100
% throughput waveform using the simulation


s_t=0;
win=30;
len=210;

gamma=0.5;
% occupancy of slots

%%%You can rerun the code if the slots are 
%%%not filled after commenting the section below
%%%%Uncomment this section for first run%%%%%%%
throughput_slots=zeros(5,5,4);
throughput=zeros(5,5,4,5,len-win);
%%initial parameter setting
thr_range=struct();
thr_range.mu_inc=150;
thr_range.mu_st=150;
thr_range.mu_end=900;
thr_range.mu=thr_range.mu_st:thr_range.mu_inc:thr_range.mu_end;
thr_range.sigma_coef_inc=0.1;
thr_range.sigma_coef_st=0.1;
thr_range.sigma_coef_end=0.6;
thr_range.sigma_coef=thr_range.sigma_coef_st:thr_range.sigma_coef_inc:thr_range.sigma_coef_end;
thr_range.stat_inc=0.15;
thr_range.stat_st=0.15;
thr_range.stat_end=0.75;
thr_range.stat=thr_range.stat_st:thr_range.stat_inc:thr_range.stat_end;
save('thr_range.mat','thr_range')

%%%%Uncomment section end%%%%%%%%%


y=zeros(1,len);
for trial=1:400 %increase trial number if slots are not filled
    for mu=thr_range.mu
        skip=0;
        maxLimit=mu*3;
        for sigma=thr_range.sigma_coef*mu
        
            pd = makedist('Normal','mu',mu,'sigma',sigma);
            t=truncate(pd,0,maxLimit);
            initial=random(t,[1,win]);
            y(1:win)=initial(:);
            t_w=y; %most recent throughput window
            [u,b,c,d,e] = adftest(t_w, 'model','ard', 'lags',0);
            %[alpha, ro] or [alpha, delta+1]
            alpha=e.coeff(1);
            ro=e.coeff(2);
            delta=ro-1;
            r=~u; %yodhida et al use the opposite convention

            for i=win+1:len
                sigma_e_sq=(1/(win-3))*sum((diff(t_w)-alpha-delta*t_w(1:end-1)).^2);
                Es=ro*t_w(end)+alpha;
                Vs=(sigma_e_sq)*(1+ro);
                En=t_w(end);
                Vn=sigma_e_sq;
                Emix=(1-r)*Es+r*En;
                Vmix=(1-r)*(Es^2+Vs)+r*(En^2+Vn)-Emix^2;
                Smix=(Vmix^0.5);
                try
                pd = makedist('Normal','mu',Emix,'sigma',Smix);
                t=truncate(pd,max(0,t_w(end)-3*sigma),min(maxLimit,t_w(end)+3*sigma));
                y(i)=int32(random(t));
                catch
                    skip=1;
                    break
                end


                %Update T_w and coeffs
                t_w=y(i-win+1:i);
                [u,b,c,d,e] = adftest(t_w, 'model','ard', 'lags',0);
                u=~u;
                %[alpha, ro] or [alpha, delta+1]
                alpha=e.coeff(1);
                ro=e.coeff(2);
                delta=ro-1;
                r=gamma*r+(1-gamma)*u;
                %---------------------
            end
            if skip==1
                continue
            end
            %eliminate initial part
            y(1:win)=[];
            [mean_final,var_final,st_final]=st_percent(y,win);
            
            %Checking intervals, slot occupancy and saving
            %throughputs
            i3=floor(st_final/thr_range.stat_inc);
            low_bound=round(thr_range.stat_st/thr_range.stat_inc)-1;
            high_bound=round(thr_range.stat_end/thr_range.stat_inc);
            if i3>low_bound && i3<high_bound
                i1=floor(mean_final/thr_range.mu_inc);
                low_bound=round(thr_range.mu_st/thr_range.mu_inc)-1;
                high_bound=round(thr_range.mu_end/thr_range.mu_inc);
                if i1>low_bound && i1<high_bound
                    i2=floor(var_final/(thr_range.sigma_coef_inc*mean_final));
                    low_bound=round(thr_range.sigma_coef_st/thr_range.sigma_coef_inc)-1;
                    high_bound=round(thr_range.sigma_coef_end/thr_range.sigma_coef_inc);
                    if i2>low_bound && i2<high_bound
                        i4=throughput_slots(i1,i2,i3)+1;
                        if i4<11
                           throughput_slots(i1,i2,i3)=i4;
                           throughput(i1,i2,i3,i4,:)=y;
                        end
                    end
                end
            end
                            
        end
    end
    if sum(throughput_slots)>999
        save('thr180.mat',throughput)
        break
    end
end

