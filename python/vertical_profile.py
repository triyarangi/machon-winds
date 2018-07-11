from collections import OrderedDict

################################################
# This class defines a vertical profile
#
#

class VerticalProfile:


    def __init__(self, samples, station):
        self.samples = samples
        self.station = station


    # given a list of height levels (m),
    # interpolate or integrate sonde data to them
    def rescale(self, levels_msl_m):

        rescaled_samples = OrderedDict()

        for i in range(0, len(levels_msl_m)-0):

            # pick range for integration:
            low_level = None
            high_level = None
            curr_level = levels_msl_m[i]
            if i == 0:
                low_level = curr_level
            else:
                low_level = (levels_msl_m[i-1]+curr_level)/2

            if i == len(levels_msl_m)-1:
                high_level = curr_level
            else:
                high_level = (levels_msl_m[i+1]+curr_level)/2

            range_samples = []
            for (sonde_level, sonde_sample) in self.samples.iteritems():
                if high_level >= sonde_level >= low_level:
                    range_samples.append(sonde_sample)

            rescaled_sample = None
            if len(range_samples) >= 2:
                rescaled_sample = self.integrate( range_samples )
            else:
                rescaled_sample = self.interpolate( curr_level )
            rescaled_samples[curr_level] = rescaled_sample

        return VerticalProfile(rescaled_samples, self.station)


    def integrate(self, samples ):

        return sum(samples)/len(samples)

    def interpolate(self, x):
        x0 = None
        y0 = None
        x1 = None
        y1 = None
        for (sonde_level, sonde_sample) in self.samples.iteritems():
            if sonde_level == x:
                return sonde_sample
            if sonde_level > x:
                x0 = sonde_level
                y0 = sonde_sample
            else:
                x1 = sonde_level
                y1 = sonde_sample
                break

        if x0 is None or x1 is None: return None

        y = y0 + (x - x0)*(y1-y0)/(x1-x0)

        return y

