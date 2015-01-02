classdef DDS_uControlFrontend < hgsetget
    %DDS_UCONTROLFRONTEND Frontend for Controlling 2 DDS Boards
    %   This a GUI frontend for 1 microController that controls 2 DDS
    %   boards. It will instantiate two DDS_Frontend Objects. One could
    %   conceivably instantiate this multiple times if you had multiple
    %   different microcontrollers.
    
    properties
        myTopFigure = [];
        myPanel = [];
        myDDSs;
        mySerial;
        myPortListBox;
    end
    
    methods
        function obj = DDS_uControlFrontend(topFig, parentObj, numDDS)
            obj.myTopFigure = topFig;
            obj.myPanel = uiextras.Grid('Parent', parentObj, ...
                'Spacing', 5, ...
                'Padding', 5);
            
            uCbuttonVB = uiextras.VBox('Parent', obj.myPanel);
                uicontrol(...
                            'Parent', uCbuttonVB, ...
                            'Style', 'text', ...
                            'String', 'Arduino Control', ...
                            'FontWeight', 'bold', ...
                            'FontUnits', 'normalized', ...
                            'FontSize', 0.1);
                comPortListHB = uiextras.HBox('Parent', uCbuttonVB);
                    uiextras.Empty('Parent', comPortListHB);
                    a = instrhwinfo('serial');
                    obj.myPortListBox = uicontrol(...
                                'Parent', comPortListHB,...
                                'Style', 'popupmenu', ...
                                'Tag', 'comPortListMenu',...
                                'String', a.SerialPorts);
                    uicontrol(...
                                'Parent', comPortListHB,...
                                'Style', 'pushbutton', ...
                                'Tag', 'refreshComPortList',...
                                'String', 'Refresh',...
                                'Callback', @obj.refreshComPortList_Callback);        
                    uiextras.Empty('Parent', comPortListHB);
                    set(comPortListHB, 'Sizes', [-0.2 -4 -1 -0.2]);
                uicontrol(...
                                'Parent', uCbuttonVB,...
                                'Style', 'pushbutton', ...
                                'Tag', 'openSerial',...
                                'String', 'FOpen',...
                                'Callback', @obj.openSerial_Callback);
                uicontrol(...
                                'Parent', uCbuttonVB,...
                                'Style', 'pushbutton', ...
                                'Tag', 'closeSerial',...
                                'String', 'FClose',...
                                'Enable', 'off', ...
                                'Callback', @obj.closeSerial_Callback);
                uiextras.Empty('Parent', uCbuttonVB);
            uCbuttonVB.Sizes = [-2 -1 -1 -1 -2];

%             uiextras.Empty('Parent', obj.myPanel);
            for i=1:numDDS
                obj.myDDSs{i} = DDS.DDS_Frontend(obj.myTopFigure, obj.myPanel, i-1);
            end
%             set(obj.myPanel, 'ColumnSizes', [-1 -1 -1, -1], 'RowSizes', [-1, -1]);
%             set(obj.myPanel, 'RowSizes', [-1, -1]);

            
            myHandles = guihandles(obj.myTopFigure);
            set(myHandles.sendCommand, 'Enable', 'off');
            guidata(obj.myTopFigure, myHandles);
        end
        
        function refreshComPortList_Callback(obj, src, eventData)
            myHandles = guidata(obj.myTopFigure);
            a = instrhwinfo('serial');
            set(myHandles.comPortListMenu, 'String', a.SerialPorts);
            guidata(obj.myTopFigure, myHandles);
        end
        
        function openSerial_Callback(obj, src, eventData)
            myHandles = guidata(obj.myTopFigure);
            mySerialPortList = get(myHandles.comPortListMenu, 'String');
            myVal = get(myHandles.comPortListMenu, 'Value');
            mySerialAddr = mySerialPortList{myVal};
            obj.mySerial = serial(mySerialAddr);
            
            success = 0;
            try
                fopen(obj.mySerial);
                success = 1;
                disp('Open Success!')
            catch
                disp('Error: Open Failed');
            end
            
            if success
                set(myHandles.closeSerial, 'Enable', 'on');
                set(myHandles.openSerial, 'Enable', 'off');
                for i=1:length(obj.myDDSs)
                    temp = obj.myDDSs{i};
                    temp.mySerial = obj.mySerial;
                end
                set(myHandles.sendCommand, 'Enable', 'on');
                set(myHandles.comPortListMenu, 'Enable', 'off');
            end
            guidata(obj.myTopFigure, myHandles);
        end
        
        function closeSerial_Callback(obj, src, eventData)
            myHandles = guidata(obj.myTopFigure);            
            success = 0;
            try
                fclose(obj.mySerial);
                success = 1;
                delete(obj.mySerial);
                for i=1:length(obj.myDDSs)
                    temp = obj.myDDSs{i};
                    temp.mySerial = [];
                end
                disp('Close Success!')
            catch
                disp('Error: Close Failed');
            end
            
            if success
                set(myHandles.closeSerial, 'Enable', 'off');
                set(myHandles.openSerial, 'Enable', 'on');
                set(myHandles.sendCommand, 'Enable', 'off');
                set(myHandles.comPortListMenu, 'Enable', 'on');
            end
            guidata(obj.myTopFigure, myHandles);
        end
        
        function setDriftMode(obj, num)
            obj.myDDSs{num}.setDriftMode();
        end
        function quit(obj)
            myHandles = guidata(obj.myTopFigure);
            success = 0;
            try
                fclose(obj.mySerial);
                success = 1;
                delete(obj.mySerial);
                for i=1:length(obj.myDDSs)
                    temp = obj.myDDSs{i};
                    temp.mySerial = [];
                end
                disp('Close Success!')
            catch
                disp('Error: Close Failed');
            end
        end
    end
    
end

