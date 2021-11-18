import rclpy
from rclpy.node import Node
from sensor_fusion.extended_kalman_filter import calc_input, ekf_estimation, jacob_h, observation

from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import JointState

import math
import numpy as np

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        
        self.pubIMU_ = self.create_subscription(JointState, '/position/IMU', self.IMU_callback, 10)
        self.pubIMU_ # prevent unused variable warning
        
        self.subGPS_ = self.create_subscription(Float32MultiArray, '/boat/velocity', self.GPS_callback, 10)
        self.subGPS_  # prevent unused variable warning

        self.publisher_ = self.create_publisher(Float32MultiArray, '/position/fusion', 10)

        self.prevTime_ = None

        # EKF
        self.xEst = np.zeros((4, 1)) #State vector [x y yaw v]
        self.PEst = np.eye(4)        #Covariance matrix of the state
    
    def IMU_callback(self, msg):
        message = Float32MultiArray()

        ypr = msg.position          #[yaw pitch roll]
        accel = msg.velocity        #[z y x]
        gyro = msg.effort           #[z y x]
        GPS = self.curr_GPS_        #[v x y]

        time = msg.header.stamp
        currTime = time.sec

        if self.prevTime_ != None:  #//Atleast two readings

            v = GPS[0]              #Speed from GPS
            x = GPS[1]              #Latitude
            y = GPS[2]              #Longitude
            z = np.array([[x],      #Observation vector
                            [y]])

            yaw = ypr[0]            #z-axis rotation
            yawrate = gyro[0]       #z-axis gyroscope value

            DT = currTime - self.prevTime_  #time tick [s]

            self.get_logger().info('v: %f, x: %f, y: %f, yaw: %f, yawrate: %f, DT: %f' % (v, x, y, yaw, yawrate, DT))

            self.xEst = np.array([[x],      #State vector
                                    [y],
                                    [yaw],
                                    [v]])

            u = np.array([[v], [yawrate]])  #Input vector

            self.xEst, self.PEst = ekf_estimation(self, self.xEst, self.PEst, z, u, DT)

            message.data = {float(self.xEst[3]), float(self.xEst[0]), float(self.xEst[1])} #[v x y]
            self.publisher_.publish(message)
            self.get_logger().info('v = %f, x = %f, y = %f' % (message.data[0], message.data[1], message.data[2]))
        
        self.prevTime_ = currTime

    def GPS_callback(self, msg):
        self.curr_GPS_ = msg.data


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
