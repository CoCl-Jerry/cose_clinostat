def update_temperature(main_window, temperature):
    """
    Update the UI with the current temperature.
    """
    main_window.ambient_temperture_value_label.setText(f"{temperature:.1f} °C")

def update_humidity(main_window, humidity):
    """
    Update the UI with the current humidity.
    """
    main_window.ambient_humidity_value_label.setText(f"{humidity:.1f} %")

def update_pressure(main_window, pressure):
    """
    Update the UI with the current pressure.
    """
    main_window.ambient_pressure_value_label.setText(f"{pressure:.1f} hPa")

def update_ambient_graph(graph_widget, data_type, pen, recent_data_list):
    """
    Update the graph with the latest data.
    """
    if not recent_data_list:
        return

    # Get the elapsed times and values
    elapsed_times = [data["timestamp"] for data in recent_data_list]
    values = [data[data_type] for data in recent_data_list]

    graph_widget.clear()
    graph_widget.plot(elapsed_times, values, pen=pen)

def update_acceleration(main_window, acceleration):
    """
    Update the UI with the current acceleration.
    """
    main_window.motion_x_axis_value_label.setText(f"{acceleration[0]:.2f}")
    main_window.motion_y_axis_value_label.setText(f"{acceleration[1]:.2f}")
    main_window.motion_z_axis_value_label.setText(f"{acceleration[2]:.2f}")

def update_gyro(main_window, gyro):
    """
    Update the UI with the current gyro values.
    """
    main_window.motion_x_axis_value_label.setText(f"X: {gyro[0]:.2f}")
    main_window.motion_y_axis_value_label.setText(f"Y: {gyro[1]:.2f}")
    main_window.motion_z_axis_value_label.setText(f"Z: {gyro[2]:.2f}")

def update_motion_graph(graph_widget, data_type, recent_data_list, x_pen, y_pen, z_pen):
    """
    Update the graph with the latest acceleration or gyro data for all three axes.
    """
    if not recent_data_list:
        return

    # Get the elapsed times and values for each axis
    elapsed_times = [data["timestamp"] for data in recent_data_list]
    x_values = [data[data_type][0] for data in recent_data_list]
    y_values = [data[data_type][1] for data in recent_data_list]
    z_values = [data[data_type][2] for data in recent_data_list]

    graph_widget.clear()
    graph_widget.plot(elapsed_times, x_values, pen=x_pen, name="X Axis")
    graph_widget.plot(elapsed_times, y_values, pen=y_pen, name="Y Axis")
    graph_widget.plot(elapsed_times, z_values, pen=z_pen, name="Z Axis")
