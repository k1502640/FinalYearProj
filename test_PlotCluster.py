from unittest import TestCase
import PlotCluster
import coverage

cov = coverage.Coverage()
cov.start()

class TestOpenFile(TestCase):
    def test_openfile(self):
        if __name__ == '__main__':
            # london coordinates
            self.assertEqual(PlotCluster.openfile(), '-0.12351 51.50368')
            # london coordinates outside of range
            self.assertNotEqual(PlotCluster.openfile(), '-0.42351 51.80368')
            # new york coordinates
            self.assertNotEqual(PlotCluster.openfile(), '-73.9866136 40.7306458')

    def test_getXY(self):
        if __name__ == '__main__':
            # picks up london coordinates separately
            self.assertEqual(PlotCluster.getXY(), '-0.12351', '51.50368')
            # does not include london coordinates outside of range separately
            self.assertNotEqual(PlotCluster.openfile(), '-0.42351', '51.80368')
            # does not pick up and separate new york coords
            self.assertNotEqual(PlotCluster.getXY(), '-73.9866136', '40.7306458')


    def test_Cluster(self):
        if __name__ == '__main__':
            # clusters two close points in london
            self.assertEqual(PlotCluster.Cluster(), ['-0.12351' '51.50368'], ['-0.123521 51.508041'])
            # does not include two points outside of the range.
            self.assertNotEqual(PlotCluster.Cluster(), ['-0.42351' '51.80368'], ['-0.423521 51.808041'])
            # does not cluster points in london and new york together
            self.assertNotEqual(PlotCluster.Cluster(), ['-73.9866136 40.7306458'], ['-0.123521 51.508041'])
            # check whether two random points are not included
            self.assertNotEqual(PlotCluster.Cluster(), ['-0.12351' '51.50368'], ['-0.423521 51.808041'])


    def test_get_centermost_point(self):
        if __name__ == '__main__':
            # returns centremost point of london cluster
            self.assertEqual(PlotCluster.get_centermost_point(), ['-0.143639 51.496028'])
            # does not return centremost point from outside of london safe zone
            self.assertNotEqual(PlotCluster.get_centermost_point(), ['-0.343639 51.796028'])
            # does not return centremost point from new york
            self.assertNotEqual(PlotCluster.get_centermost_point(), ['-73.993649  40.752166'])

    cov.stop()
    cov.save()

    cov.html_report()