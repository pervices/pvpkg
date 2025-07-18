from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args
from retrying import retry
import matplotlib.pyplot as plt
import sys


#Setup argument parsing
targs = test_args.TestArgs(testDesc="Tx Rx Stacked Commands Test")

report = pdf_report.ClassicShipTestReport("tx_rx_stacked_commands", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_tables = []
attempt_num = 0

@retry(stop_max_attempt_number = 3)
def test(it, data):
    global test_fail
    global attempt_num
    attempt_num += 1
    gen.dump(it)

    # Collect.
    # First frame of TX/RX stack is gold standard (sample_count samples in middle of 1 second of TX).
    tx_stack = [ (5.0, it["sample_count" ]), (8.0, it["sample_count"]), (11.0, it["sample_count"]), (14.0, it["sample_count"]) ]
    rx_stack = [ (5.0, it["sample_count"]), (8.0, it["sample_count"]), (11.0, it["sample_count"]), (14.0, it["sample_count"]) ]
    try:
        vsnk = engine.run(targs.channels, it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        raise Exception("debugging exception")
    except Exception as err:
        # if attempt_num >= 3: build_report()
        print(attempt_num)
        sys.exit(1)

    center_freq = "{:.1e}".format(it["center_freq"])
    wave_freq = "{:.1e}".format(it["wave_freq"])
    title_line1 = "Center freq: {}, Wave freq: {},".format(center_freq, wave_freq)
    title_line2 = "Sample Rate: {}".format(it["sample_rate"])
    test_info = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                        [center_freq, wave_freq, it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"]]]

    report.buffer_put("text_large", title_line1)
    report.buffer_put("text_large", title_line2)
    report.buffer_put("table_wide", test_info, "")
    report.buffer_put("text", " ")
    images = []

    # Process.
    # Stacked commands vsnk channel extensions and must be indexed manually with sample_count.
    for ch, channel in enumerate(vsnk):

        print("channel %d" % targs.channels[ch])
        areas = []
        res = "pass"
        plt.figure()
        plt.title("Channel {}".format(targs.channels[ch]))
        frame_results = []
        for i, frame in enumerate(rx_stack):
            sample_count = frame[1]
            a = int(i * sample_count)
            b = int(a + sample_count)
            frame_data = channel.data()[a : b]

            area = sigproc.absolute_area(frame_data)
            areas.append(area)

            # Area likeness is relative to gold standard (first stack frame).
            likeness = area / areas[0]
            frame_results.append(round(likeness, 8))

            print("\tframe %d: aboslute area: likeness %f" % (i, likeness))

            plt.plot(frame_data, label="Frame {}".format(i))

            try:
                assert likeness > 0.5 and likeness < 1.5, "tx_rx_stacked_commands fail comparison"
            except:
                test_fail = 1
                res = "fail"

        plt.legend()
        s = report.get_image_io_stream()
        plt.savefig(s, format='png')
        plt.close()
        img = report.get_image_from_io_stream(s)
        images.append(img)
        data.append([str(center_freq), str(wave_freq), it["sample_rate"], str(targs.channels[ch]), frame_results[1], frame_results[2], frame_results[3], res])

    report.buffer_put("image_list_dynamic", images, "")
    report.buffer_put("pagebreak")
    return data


def main(iterations, desc):
    global attempt_num
    data  = [["Centre Freq", "Wave Freq", "Sample Rate", "Channel", "Frame 1/Frame 0","Frame 2/Frame 0", "Frame 3/Frame 0", "Result"]]
    for it in iterations:
        attempt_num = 0
        test(it, data)
        print("After test")
    summary_tables.append([desc, data])


def add_summary_table(title, data):
    report.insert_text_large("{} Testing Summary".format(title))
    report.insert_text("")
    report.insert_table(data)
    report.new_page()

def build_report():
    report.insert_title_page("Stacked Commands Test")
    for summary in summary_tables:
        add_summary_table(summary[0], summary[1])
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())

## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    main(gen.lo_band_basic(), "Low Band")
    main(gen.hi_band_basic(), "High Band")
elif(targs.product == "Tate"):
    main(gen.cyan.lo_band.basic(), "Low Band")
    main(gen.cyan.mid_band.basic(), "Mid Band")
    main(gen.cyan.hi_band.basic(), "High Band")
elif(targs.product == "Lily"):
    main(gen.chestnut.lo_band.basic(), "Low Band")
    main(gen.chestnut.mid_band.basic(), "Mid Band")
    main(gen.chestnut.hi_band.basic(), "High Band")

build_report()
sys.exit(test_fail)
