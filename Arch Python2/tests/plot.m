% Copy and paste the output from an SSH data dump into sin.data
% and run this script in GNU OCTAVE to plot it.

load sins.dat;

clf();
figure(1);

for channel = 0 : 3

    subplot(4, 1, channel + 1);
    ylim([min(min(sins)), max(max(sins))]);

    hold on;
    plot(sins(:, 2 * channel + 1)', '-x'); % I
    plot(sins(:, 2 * channel + 2)', '-x'); % Q
    hold off;

end

legend("I", "Q");
