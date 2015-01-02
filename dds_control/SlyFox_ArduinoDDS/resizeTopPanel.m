function resizeTopPanel(src, event)
%RESIZETOPPANEL Maximizes Top Panel of figure upon resize request
    figpos = get(src, 'Position');
    try
        tp = getappdata(src, 'topPanel');
        set(tp, 'Position', [1 1 figpos(3) figpos(4)])
    catch
    end
end

