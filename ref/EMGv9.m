%  updated in 8/25/19 
%  meanfreq feature added;

clc
close all
clear all

%% read data from file
Fs = 1000; %drop
fName = 'data/20022001/dynamic15lb.txt';
rawdata = table2array(readtable(fName));
real_time = rawdata(2:end,2); % extract real time 
EMG1 = rawdata(2:end,3); % useless data droping

%% plot the raw EEG
% plot(real_time,EMG1)
% xlabel('Time(s)');
% ylabel('Potential(mV)');

%% filter
[b1,a1] = butter(6,15/(Fs/2),'high'); % highpass filter cutoff at 15Hz
% figure();
% [h,f] = freqz(b1,a1,1024,1000);plot(f,abs(h)); % filter check

wo = 60/(Fs/2);  bw = wo/35; % 60 Hz filter
[b2,a2] = iirnotch(wo,bw); % 60 Hz filter
% figure();
% [h,f] = freqz(b2,a2,1024,1000);plot(f,abs(h)); % filter check

w1 = 120/(Fs/2);  bw1 = w1/35; % 120 Hz filter
[b3,a3] = iirnotch(w1,bw1); %  120 Hz filter
% figure();
% [h,f] = freqz(b3,a3,1024,1000);plot(f,abs(h)); % filter check

[b4,a4] = butter(31,140/(Fs/2),'low');
% figure();
% [h,f] = freqz(b4,a4,1024,1000);plot(f,abs(h)); % filter check

w2 = 180/(Fs/2);  bw2 = w2/35;
[b5,a5] = iirnotch(w2,bw2);
% figure();
% [h,f] = freqz(b5,a5,1024,1000);plot(f,abs(h)); % filter check


EMG2 = filter(b2,a2,filter(b1,a1,EMG1));
EMG3 = filter(b5,a5,filter(b4,a4,filter(b3,a3,EMG2)));
EMG3 = filter(b2,a2,filter(b3,a3,EMG3));    %twice filt


%% fft comparison
L=length(EMG3);
if mod(L,2)==1
    L=L-1;
end
T = 1/Fs; 
t = (0:L-1)*T; 

fft_raw=fft(EMG1);
P2 = abs(fft_raw/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs*(0:(L/2))/L;
figure(1);
plot(f,P1);
hold on;

fft_filted=fft(EMG3);
P2 = abs(fft_filted/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs*(0:(L/2))/L;
plot(f,P1);


%% Median frequency  and mean frequency
window_length = 1;
window_num = floor(real_time(end)/window_length);  % num s
t = 1:window_num;

for n = 0:window_num-1
    temp = EMG3(Fs*n+1:Fs*n+Fs);
    mdf(n+1) = medfreq(temp,Fs);
    mef(n+1) = meanfreq(temp,Fs);
end
mdf = filloutliers(mdf,'nearest','gesd');
mef = filloutliers(mef,'nearest','gesd');
temp_mdf = polyval(polyfit(t,mdf,1),t); 
temp_mef = polyval(polyfit(t,mef,1),t); 

figure();
scatter(t,mdf,5,'filled'); hold on;
plot(t,temp_mdf);hold off;
ylim([0 100]);
title('mdf');

figure();
scatter(t,mef,5,'filled'); hold on;
plot(t,temp_mef);hold off;
ylim([0 100]);
title('mef');
 %% ARV & RMS
for N = 1:window_num
    ARV(N) = sum(abs(EMG3(1:Fs*N,1)))/(N*Fs);
    RMS(N) = sqrt(EMG3(1:Fs*N,1)'*EMG3(1:Fs*N,1)/(N*Fs));
end
 figure();
 scatter(t,ARV,5,'filled');
 title('ARV');
 figure();
 scatter(t,RMS,5,'filled');
 title('RMS');



