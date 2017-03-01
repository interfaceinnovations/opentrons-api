import time
from threading import Thread
import unittest

from opentrons import Robot
from opentrons.util.vector import Vector


class OpenTronsTest(unittest.TestCase):

    def setUp(self):

        self.robot = Robot.get_instance()

        # set this to True if testing with a robot connected
        # testing while connected allows the response handlers
        # and serial handshakes to be tested

        self.motor = self.robot._driver

        options = {
            'limit_switches': True,
            'config': {
                'alpha_steps_per_mm': 80.0,
                'beat_steps_per_mm': 80.0
            }
        }

        myport = self.robot.VIRTUAL_SMOOTHIE_PORT
        self.robot.disconnect()
        success = self.robot.connect(port=myport, options=options)
        self.assertTrue(success)

    def tearDown(self):
        pass

    def test_reset(self):
        self.motor.reset()
        self.assertEquals(self.motor.connection, None)

    def test_write_with_lost_connection(self):
        self.motor.connection.is_open = False
        old_method = getattr(self.motor, 'is_connected')

        def _temp():
            return True
        setattr(self.motor, 'is_connected', _temp)
        self.assertTrue(self.motor.is_connected())
        self.assertRaises(RuntimeError, self.motor.calm_down)
        setattr(self.motor, 'is_connected', old_method)

    def test_write_after_disconnect(self):
        self.motor.disconnect()
        self.assertRaises(RuntimeError, self.motor.calm_down)

    def test_version_compatible(self):
        self.robot.disconnect()
        self.robot.connect()
        res = self.motor.versions_compatible()
        self.assertEquals(res, {
            'firmware': True,
            'config': True,
            'ot_version': True
        })
        self.robot.disconnect()

        kwargs = {
            'options': {
                'firmware': 'v2.0.0',
                'config': {
                    'version': 'v3.1.2',
                    'ot_version': 'hoodie'
                }
            }
        }
        self.assertRaises(RuntimeError, self.robot.connect, **kwargs)

    def test_invalid_coordinate_system(self):
        self.assertRaises(ValueError, self.motor.set_coordinate_system, 'andy')

    def test_message_timeout(self):
        from opentrons.drivers.motor import SerialTimeout
        self.assertRaises(SerialTimeout, self.motor.wait_for_response)

    def test_set_plunger_speed(self):
        self.motor.set_plunger_speed(400, 'a')
        self.assertRaises(ValueError, self.motor.set_plunger_speed, 400, 'x')

    def test_set_head_speed(self):
        self.motor.set_head_speed(4000)
        self.assertEquals(self.motor.head_speed, 4000)

    def test_get_connected_port(self):
        res = self.motor.get_connected_port()
        self.assertEquals(res, self.robot.VIRTUAL_SMOOTHIE_PORT)
        self.motor.disconnect()
        res = self.motor.get_connected_port()
        self.assertEquals(res, None)

    def test_get_dimensions(self):
        self.motor.ot_version = None
        res = self.motor.get_dimensions()
        self.assertEquals(res, Vector(400.00, 400.00, 100.00))

    def test_pause_resume(self):
        self.motor.home()

        self.motor.pause()

        def _move_head():
            self.motor.move_head(x=100, y=0, z=0)

        thread = Thread(target=_move_head)
        thread.start()

        self.motor.resume()
        thread.join()

        coords = self.motor.get_head_position()
        expected_coords = {
            'target': (100, 0, 0),
            'current': (100, 0, 0)
        }
        self.assertDictEqual(coords, expected_coords)

    def test_stop(self):
        self.motor.home()

        self.motor.pause()

        def _move_head():
            self.assertRaises(
                RuntimeWarning,
                self.motor.move_head,
                **{'x': 100, 'y': 0, 'z': 0}
            )

        thread = Thread(target=_move_head)
        thread.start()

        self.motor.stop()

        thread.join()

        coords = self.motor.get_head_position()
        expected_coords = {
            'target': (0, 400, 100),
            'current': (0, 400, 100)
        }
        self.assertDictEqual(coords, expected_coords)

        self.motor.move_head(x=100, y=0, z=0)
        coords = self.motor.get_head_position()
        expected_coords = {
            'target': (100, 0, 0),
            'current': (100, 0, 0)
        }
        self.assertDictEqual(coords, expected_coords)

    def test_halt(self):
        self.motor.home()

        self.motor.pause()

        def _move_head():
            self.assertRaises(
                RuntimeWarning,
                self.motor.move_head,
                **{'x': 100, 'y': 0, 'z': 0}
            )

        thread = Thread(target=_move_head)
        thread.start()

        self.motor.halt()

        thread.join()

        coords = self.motor.get_head_position()
        expected_coords = {
            'target': (0, 400, 100),
            'current': (0, 400, 100)
        }
        self.assertDictEqual(coords, expected_coords)

        self.motor.move_head(x=100, y=0, z=0)
        coords = self.motor.get_head_position()
        expected_coords = {
            'target': (100, 0, 0),
            'current': (100, 0, 0)
        }
        self.assertDictEqual(coords, expected_coords)

    def test_get_position(self):
        self.motor.home()
        self.motor.ot_version = None
        self.motor.move_head(x=100)
        coords = self.motor.get_head_position()
        expected_coords = {
            'target': (100, 400, 100),
            'current': (100, 400, 100)
        }
        self.assertDictEqual(coords, expected_coords)

    def test_home(self):

        success = self.motor.home('x', 'y')
        self.assertTrue(success)

        success = self.motor.home('ba')
        self.assertTrue(success)

    def test_limit_hit_exception(self):
        self.motor.home()
        try:
            self.motor.move_head(x=-100)
            self.motor.wait_for_arrival()
        except RuntimeWarning as e:
            self.assertEqual(str(RuntimeWarning('X limit switch hit')), str(e))

        self.motor.home()

    def test_move_x(self):
        self.motor.ot_version = None
        success = self.motor.move_head(x=100)
        self.assertTrue(success)

    def test_move_y(self):
        self.motor.ot_version = None
        success = self.motor.move_head(y=100)
        self.assertTrue(success)

    def test_move_z(self):
        self.motor.ot_version = None
        success = self.motor.move_head(z=30)
        self.assertTrue(success)

    def test_send_command(self):
        success = self.motor.send_command('G0 X1 Y1 Z1')
        self.assertTrue(success)

    def test_send_command_with_kwargs(self):
        success = self.motor.send_command('G0', x=1, y=2, z=3)
        self.assertTrue(success)

    def test_wait(self):
        # set connection to be something other than VirtualSmoothie
        self.motor.connection = int()
        start_time = time.time()
        success = self.motor.wait(1.234)
        end_time = time.time()
        self.assertAlmostEquals(end_time - start_time, 1.234, places=1)
        self.assertTrue(success)

        self.motor.connection = int()
        start_time = time.time()
        success = self.motor.wait(1.0)
        end_time = time.time()
        self.assertAlmostEquals(end_time - start_time, 1.0, places=1)
        self.assertTrue(success)

    def test_wait_for_arrival(self):
        self.motor.home()
        self.motor.move_head(x=200, y=200)
        self.motor.move_head(z=30)
        success = self.motor.wait_for_arrival()
        self.assertTrue(success)

    def test_move_relative(self):
        self.motor.home()
        self.motor.move_head(x=100, y=100, z=100)
        self.motor.move_head(x=0, mode='relative')
        self.motor.move_head(x=100, mode='absolute')

    def test_calibrate_steps_per_mm(self):
        self.motor.home()
        self.motor.set_steps_per_mm('x', 80.0)
        self.motor.set_steps_per_mm('y', 80.0)
        self.motor.set_steps_per_mm('z', 1068.7)
        self.motor.move_head(x=200, y=200)

        self.motor.calibrate_steps_per_mm('x', 200, 198)
        self.motor.calibrate_steps_per_mm('y', 200, 202)
        self.motor.calibrate_steps_per_mm('z', 100, 101)

        new_x_steps = self.motor.get_steps_per_mm('x')
        new_y_steps = self.motor.get_steps_per_mm('y')
        new_z_steps = self.motor.get_steps_per_mm('z')

        exptected_x = round((200 / 198) * 80.0, 2)
        exptected_y = round((200 / 202) * 80.0, 2)
        exptected_z = round((100 / 101) * 1068.7, 2)

        self.assertEqual(exptected_x, new_x_steps)
        self.assertEqual(exptected_y, new_y_steps)
        self.assertEqual(exptected_z, new_z_steps)

        self.assertRaises(ValueError, self.motor.get_steps_per_mm, 'a')
        self.assertRaises(ValueError, self.motor.set_steps_per_mm, 'a', 80.0)

        self.motor.set_steps_per_mm('x', 80.0)
        self.motor.set_steps_per_mm('y', 80.0)
        self.motor.set_steps_per_mm('z', 1068.7)

    def test_get_endstop_switches(self):
        res = self.motor.get_endstop_switches()
        expected = {
            'x': False,
            'y': False,
            'z': False,
            'a': False,
            'b': False
        }
        self.assertEquals(res, expected)
        try:
            self.motor.move_head(x=-100)
            self.motor.move_head(x=-101)
        except Exception:
            pass
        res = self.motor.get_endstop_switches()
        expected = {
            'x': True,
            'y': False,
            'z': False,
            'a': False,
            'b': False
        }
        self.assertEquals(res, expected)

    def test_set_mosfet(self):
        res = self.motor.set_mosfet(0, True)
        self.assertTrue(res)

        res = self.motor.set_mosfet(5, False)
        self.assertTrue(res)

        self.assertRaises(IndexError, self.motor.set_mosfet, 6, True)

    def test_power_on_off(self):
        res = self.motor.power_on()
        self.assertTrue(res)

        res = self.motor.power_off()
        self.assertTrue(res)
