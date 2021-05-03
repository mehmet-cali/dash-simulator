function [mu,sigma,stationarity] = st_percent(y,N)
%ST_PERCENT Summary of this function goes here
% N:window length, 
    hY=zeros(1,length(y)-N+1);
        for k = 1:length(y)-N+1
            y_s=y(k:k+N-1);
            hY(1,k) = adftest(y_s, 'model','ard', 'lags',0);
        end
        mu=mean(y);
        sigma=std(y);
        stationarity=sum(hY(:)==1)/length(hY);
end

