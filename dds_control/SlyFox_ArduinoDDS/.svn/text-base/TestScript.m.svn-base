%% Testing Script for DDS stuff
dds = DDS.DDS_Config(1)
dds.myMode = 'Single Tone'
[oFreq, ftw] = dds.calculateFTW(50.000000)
params = struct('FTW1', ftw);
iSet = dds.createInstructionSet('Single Tone', params)
% fwrite(s, iSet)
% fscanf(s)


%% Testing Frontend
f = figure;
tp = uiextras.Panel('Parent', f, 'Tag', 'topPanelDDS');
setappdata(gcf, 'topPanel', tp);
set(f, 'ResizeFcn', @resizeTopPanel);
DDS.DDS_uControlFrontend(f,tp);