classdef DDS_Config < hgsetget
    %DDS_CONFIG Backend for Controlling various DDS parameters
    %   DDS_Config holds both the settings that are needed to communicate
    %   to the DDS through the Arduino. But also relevant paremeters about
    %   the model of DDS eval board being used. 
    %   Written by Ben Bloom 10/4/2011
    
    properties
        myBoardAddress = 0;
        myBoardModel = 'AD9854'
        mySysClk = 200;
        myHWProps;
        myMode = 'Single Tone';
    end
    
    methods
        function obj = DDS_Config(boardAddress)
            obj.myBoardAddress = boardAddress;
            obj.setBoardModel(obj.myBoardModel);
        end
        
        function setBoardModel(obj, boardModel)
            obj.myBoardModel = boardModel;
            switch boardModel
                case 'AD9854'
                    %see ad9854 datasheet for data on this chip                       
                    keys = {'Resolution', ...
                        'ConfigReg', ...
                        'ConfigBytes', ...
                        'ConfigModePos', ...
                        'ClrACC2Pos', ...
                        'FTW1_Reg', ...
                        'FTW2_Reg', ...
                        'DeltaFW_Reg', ...
                        'RampRate_Reg', ...
                        'OSKI_Reg', ...
                        'AvailableModes', ...
                        'ModeCodes'};
                        
                    vals = {48, ...
                        '7', ...
                        '10140021', ...
                        [21:23], ...
                        18, ...
                        '2', ...
                        '3', ...
                        '4', ...
                        '6', ...
                        '8', ...
                        {'Single Tone', ...
                            'FSK', ...
                            'Ramped FSK', ...
                            'Chirp', ...
                            'BPSK'}, ...
                        {'000', ...
                            '001', ...
                            '010', ...
                            '011', ...
                            '100'}};
                    obj.myHWProps = containers.Map(keys, vals);
            end
        end
        
        function [outFreq, ftw] = calculateFTW(obj, desiredFrequency)
            %This function calculates the correct Frequency Tuning Word
            %needed to reach the desired frequency given the chips system
            %clock.
            q = quantizer('ufixed','round', [48 0]);
            ftwRAW = (desiredFrequency*2^48)/obj.mySysClk
            ftw = num2hex(q, ftwRAW)
            outFreq = hex2num(q, ftw)*(obj.mySysClk*10^6)/2^48;
        end
        
        function ampHex = calculateAmp(obj, ampNum)
            %This function calculates the correct Frequency Tuning Word
            %needed to reach the desired frequency given the chips system
            %clock.
            q = quantizer('ufixed','round', [16 0]);
            ampHex = num2hex(q, ampNum);
        end
        
        function [realSlope, RRW, DFTW] = calculateRRW(obj, desiredSlope)
%             % Here I will assume that we want the smallest DFTW possible
            DFTWp = '000000000001';
            DFTWn = 'FFFFFFFFFFFF';
            if desiredSlope > 0
                DFTW = DFTWp;
            else
                DFTW = DFTWn;
            end
            q = quantizer('fixed','round', [48 0]);
            stepRes = hex2num(q, DFTWp)*(obj.mySysClk*10^6)/2^48; %This gives the stepResolution in hertz
            desiredFrequency = (abs(desiredSlope)*10^-3)/ stepRes;
            desiredPeriod = 1/desiredFrequency;
            N = round(desiredPeriod*obj.mySysClk*10^6) - 1;
            if N < 1
                N = 1;
            elseif N > 2^20 - 1
                N = 2^20 - 1;
            end
                
            q = quantizer('ufixed','round', [24 0]);
            RRW = num2hex(q, N);
            rampRateReal = hex2num(q, RRW);
%             realSlope = sign(desiredSlope)*(rampRateRatio)*minSlope;
            realSlope = sign(desiredSlope)*stepRes*10^3*obj.mySysClk*10^6/(rampRateReal+1); % measured in mHz
            % GENETIC ALGORITHM FOR FINDING THE OPTIMAL DFTW and RRW
%             
%             %x = ga(fitnessfcn,nvars,A,b,[],[],LB,UB,nonlcon,IntCon)
%             %Needs to be simplified 
%             %fun = @(x) (abs(desiredSlope - x(1)*(obj.mySysClk*10^6)/2^48*10^3*obj.mySysClk*10^6/(x(2)+1)))
%             fun = @(x) abs(desiredSlope - x(1)*(obj.mySysClk^2*10^15)/(2^48*(x(2)+1)));
%             LB = [-(2^47 - 1); 1];
%             UB = [(2^47-1); (2^20-1)];
%             x = ga(fun,2,[],[],[],[],LB,UB,[],[1 2]) % variables 1 and 2 are integers
%             stepRes2 = x(1)*(obj.mySysClk*10^6)/2^48
%             realSlope2 = stepRes2*10^3*obj.mySysClk*10^6/(x(2)+1)
%             updatePeriod2 = (obj.mySysClk*10^6/(x(2)+1))^-1
%             updatePeriod = (obj.mySysClk*10^6/(rampRateReal+1))^-1
        end
        
        function instrCell = createInstructionSet(obj, selectedMode, params)
            %Creates instructionSet for the selectedMode
            instrCell = {};
            instrSet = [];
            setCount = 1;
            switch selectedMode
                case 'Single Tone'
                    instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                    instrSet = [instrSet; uint8(obj.myBoardAddress)]; %which board to use
                    instrSet = [instrSet; 7]; %Number of Bytes in Instruction after this point
                    instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('FTW1_Reg')))]; %Address of register on the DDS to write to.
                    FTW1 = params.FTW1;
                    for i=1:2:length(FTW1)
                        instrSet = [instrSet; uint8(hex2dec(FTW1(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                    end

                    checkSumLow = obj.createCheckSum(instrSet);
                    instrSet = [instrSet; uint8(checkSumLow)];
                    instrCell{1} = instrSet;
                case 'FSK'
                    if params.WriteMode == 1 || params.WriteMode == 2
                        instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 7]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('FTW1_Reg')))]; %Address of register on the DDS to write to.
                        FTW1 = params.FTW1;
                        for i=1:2:length(FTW1)
                            instrSet = [instrSet; uint8(hex2dec(FTW1(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                        end

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                        setCount = setCount + 1;
                    end
                    if params.WriteMode == 1 || params.WriteMode == 3
                        instrSet = [];
                        instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 7]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('FTW2_Reg')))]; %Address of register on the DDS to write to.
                        FTW2 = params.FTW2;
                        for i=1:2:length(FTW2)
                            instrSet = [instrSet; uint8(hex2dec(FTW2(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                        end

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                        setCount = setCount + 1;
                    end
                    if params.WriteMode == 4
                        instrSet = [];
                        instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 7]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec(obj.myHWProps(params.WriteRegister)))]; %Address of register on the DDS to write to.
                        FTW = params.FTW;
                        for i=1:2:length(FTW)
                            instrSet = [instrSet; uint8(hex2dec(FTW(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                        end

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                        setCount = setCount + 1;
                        
                        instrSet = [];
                        instrSet = [instrSet; uint8(';')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 2]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec('01'))]; %Command Code for Switch FSK
                        if strcmp(params.WriteRegister, 'FTW1_Reg')
                            instrSet = [instrSet; uint8(0)]; %FSK set to FTW1
                        else
                            instrSet = [instrSet; uint8(1)]; %FSK set to FTW2
                        end

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                    end
                case 'Chirp'
                    if params.WriteMode == 1 %If you are setting the Base Frequency
                        instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 7]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('FTW1_Reg')))]; %Address of register on the DDS to write to.
                        FTW1 = params.FTW1;
                        for i=1:2:length(FTW1)
                            instrSet = [instrSet; uint8(hex2dec(FTW1(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                        end

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                        setCount = setCount + 1;
                        
                        instrSet = [];
                        instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 5]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('ConfigReg')))]; %Address of register on the DDS to write to.

                        q = quantizer('ufixed','round', [32 0]);
                        configNum = hex2num(q, obj.myHWProps('ConfigBytes'));
                        configBin = num2bin(q, configNum);
                        a = obj.myHWProps('AvailableModes');
                        modeIdx = find(cellfun(@(x) strcmp(x, selectedMode), a));
                        mCodes = obj.myHWProps('ModeCodes');
                        newModeBin = mCodes{modeIdx};
                        configBin(obj.myHWProps('ConfigModePos')) = newModeBin;
                        configBin(obj.myHWProps('ClrACC2Pos')) = '1';
                        newConfig = bin2num(q, configBin);
                        configHex = num2hex(q, newConfig)

                        for i=1:2:length(configHex)
                            instrSet = [instrSet; uint8(hex2dec(configHex(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                        end

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                        
                        setCount = setCount +  1; 
                        
                        instrSet = [];
                        instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 5]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('ConfigReg')))]; %Address of register on the DDS to write to.
                        
                        configBin(obj.myHWProps('ClrACC2Pos')) = '0';
                        newConfig = bin2num(q, configBin);
                        configHex = num2hex(q, newConfig)
                        
                        for i=1:2:length(configHex)
                            instrSet = [instrSet; uint8(hex2dec(configHex(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                        end

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                        
                        setCount = setCount +  1; 
                        
                        obj.myMode = selectedMode;
                    else %set slope mode
                        instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 7]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('DeltaFW_Reg')))]; %Address of register on the DDS to write to.
                        DFTW = params.DFTW;
                        for i=1:2:length(DFTW)
                            instrSet = [instrSet; uint8(hex2dec(DFTW(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                        end

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                        setCount = setCount + 1;
                        
                        instrSet = [];
                        instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 4]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('RampRate_Reg')))]; %Address of register on the DDS to write to.
                        RRW = params.RRW;
                        for i=1:2:length(RRW)
                            instrSet = [instrSet; uint8(hex2dec(RRW(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                        end

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                        setCount = setCount + 1;
                        
                        instrSet = [];
                        instrSet = [instrSet; uint8(';')]; %tells the microprocessor to enter passthrough mode
                        instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                        instrSet = [instrSet; 2]; %Number of Bytes in Instruction after this point
                        instrSet = [instrSet; uint8(hex2dec('01'))]; %Command Code for Switch FSK/HOLD
                        
                        instrSet = [instrSet; uint8(0)]; %Set Hold to zero

                        checkSumLow = obj.createCheckSum(instrSet);
                        instrSet = [instrSet; uint8(checkSumLow)];
                        instrCell{setCount} = instrSet;
                    end
                    
                case 'CHANGEMODE'
                    disp('ChangeMode')
                    instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                    instrSet = [instrSet; obj.myBoardAddress]; %which board to use
                    instrSet = [instrSet; 5]; %Number of Bytes in Instruction after this point
                    instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('ConfigReg')))]; %Address of register on the DDS to write to.
                    
                    q = quantizer('ufixed','round', [32 0]);
                    configNum = hex2num(q, obj.myHWProps('ConfigBytes'));
                    configBin = num2bin(q, configNum);
                    a = obj.myHWProps('AvailableModes');
                    modeIdx = find(cellfun(@(x) strcmp(x, params.NEWMODE), a));
                    params.NEWMODE
                    mCodes = obj.myHWProps('ModeCodes');
                    newModeBin = mCodes{modeIdx};
                    configBin(obj.myHWProps('ConfigModePos')) = newModeBin;
                    newConfig = bin2num(q, configBin);
                    configHex = num2hex(q, newConfig);
                    
                    for i=1:2:length(configHex)
                        instrSet = [instrSet; uint8(hex2dec(configHex(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                    end
                    
                    checkSumLow = obj.createCheckSum(instrSet);
                    instrSet = [instrSet; uint8(checkSumLow)];
                    instrCell{1} = instrSet;
                    
                    configHex
                    obj.myMode = params.NEWMODE;
                case 'Amplitude'
                    instrSet = [instrSet; uint8(':')]; %tells the microprocessor to enter passthrough mode
                    instrSet = [instrSet; uint8(obj.myBoardAddress)]; %which board to use
                    instrSet = [instrSet; 3]; %Number of Bytes in Instruction after this point
                    instrSet = [instrSet; uint8(hex2dec(obj.myHWProps('OSKI_Reg')))]; %Address of register on the DDS to write to.
                    ampHex = params.ampHex;
                    for i=1:2:length(ampHex)
                        instrSet = [instrSet; uint8(hex2dec(ampHex(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                    end

                    checkSumLow = obj.createCheckSum(instrSet);
                    instrSet = [instrSet; uint8(checkSumLow)];
                    instrCell{1} = instrSet;
                case 'Defaults'
                    instrSet = [instrSet; uint8(';')]; %tells the microprocessor that this is an arduino CMD not at DDS cmd
                    instrSet = [instrSet; uint8(obj.myBoardAddress)]; %which board to use
                    instrSet = [instrSet; 9]; %Number of Bytes in Instruction after this point
                    instrSet = [instrSet; uint8('D')]; %Instruction D
                    ampHex = params.ampHex;
                    for i=1:2:length(ampHex)
                        instrSet = [instrSet; uint8(hex2dec(ampHex(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                    end
                    
                    FTW1 = params.FTW1;
                    for i=1:2:length(FTW1)
                        instrSet = [instrSet; uint8(hex2dec(FTW1(i:i+1)))]; %Yea I know its sloppy, but come on did that last 2 uS cost you that much time
                    end

                    checkSumLow = obj.createCheckSum(instrSet);
                    instrSet = [instrSet; uint8(checkSumLow)];
                    instrCell{1} = instrSet;
                case 'Reinitialize'
                    instrSet = [instrSet; uint8(';')]; %tells the microprocessor that this is an arduino CMD not at DDS cmd
                    instrSet = [instrSet; uint8(obj.myBoardAddress)]; %which board to use
                    instrSet = [instrSet; 1]; %Number of Bytes in Instruction after this point
                    instrSet = [instrSet; uint8('R')]; %Instruction R for Reinitialize
                    
                    checkSumLow = obj.createCheckSum(instrSet);
                    instrSet = [instrSet; uint8(checkSumLow)];
                    instrCell{1} = instrSet;
            end
        end
        
        function cSum = createCheckSum(obj, iSet)
               checkSum = sum(iSet(2:end));
               q = quantizer('ufixed','round', [48 0]);
               checkSumBIN = num2bin(q, checkSum);
               lowByteCheckSumBIN = checkSumBIN(41:end);
               cSum = bin2num(q, lowByteCheckSumBIN);
        end
            
    end
    
end

