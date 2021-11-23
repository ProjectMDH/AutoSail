from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package="sensor_malfunction",
            namespace="position",
            executable="if_error",
            name="vessel_orientation",
            parameters=[
                {'my_topic': 'IMU'},
                {'my_DL': 5}
                ],
            output="screen",
            emulate_tty=True
        )
    ])
