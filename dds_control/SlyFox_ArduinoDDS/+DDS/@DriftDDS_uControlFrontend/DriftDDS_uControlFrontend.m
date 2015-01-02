classdef DriftDDS_uControlFrontend < DDS.DDS_uControlFrontend
    %DriftDDS_UCONTROLFRONTEND Frontend for Controlling 1 Drift DDS Board
    %   Subclass specifically built to control the DriftDDS
    
    
    methods
        function obj = DriftDDS_uControlFrontend(topFig, parentObj)
            obj = obj@DDS.DDS_uControlFrontend(topFig, parentObj, 1);
            set(obj.myPortListBox, 'String', {'COM7'});
            obj.openSerial_Callback();
        end
    end
    
end

