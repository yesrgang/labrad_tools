function ArduinoDDSMain(numDDS )
%ARDUINODDSMAIN Main Function for Arduino DDS Program
%   This constructs the relevant objects and creates an Arduino DDS
%   GUI. 
%   All this code is licensed under the 
%   By Ben Bloom 10/14/2011 11:13

    f = figure('Menubar', 'none', 'Toolbar', 'none', 'NumberTitle', 'off', 'Name', 'Frequency Sweeper');
    tp = uiextras.Panel('Parent', f, 'Tag', 'topPanelDDS');
    setappdata(gcf, 'topPanel', tp);
    set(f, 'ResizeFcn', @resizeTopPanel);
    myDDSFrontend = DDS.DDS_uControlFrontend(f,tp, numDDS);

    mm = uimenu('Label', 'File');
    sm = uimenu(mm, 'Label', 'Save...');
    lm = uimenu(mm, 'Label', 'Load...');

    function windowClose(src,event)
        myDDSFrontend.quit();
        
        delete(myDDSFrontend);
        delete(tp);
        delete(f);
    end
    
    set(f,'CloseRequestFcn',@windowClose);
end

