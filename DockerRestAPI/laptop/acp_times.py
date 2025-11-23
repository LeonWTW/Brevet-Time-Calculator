"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An arrow date-time object indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    # Validate brevet distance (for nose test case, the test_invalid_brevet_distance need this)
    valid_distances = [200, 300, 400, 600, 1000]
    if brevet_dist_km not in valid_distances:
        raise ValueError(f"Invalid brevet distance: {brevet_dist_km}. Must be one of {valid_distances}")
    


    # Handle start control (0 km)
    if control_dist_km <= 0:
        return arrow.get(brevet_start_time)
    
    # If control distance exceeds brevet distance, cap it at brevet distance
    actual_dist = min(control_dist_km, brevet_dist_km)

    # Speed table for opening times (maximum speeds in km/h)
    # Format: (distance_threshold, speed)
    speed_table = [
        (200, 34),
        (400, 32),
        (600, 30),
        (1000, 28),
        (1300, 26)
    ]

    # Calculate time by segments
    total_minutes = 0
    remaining_dist = actual_dist
    prev_threshold = 0
    
    for threshold, speed in speed_table:
        if remaining_dist <= 0:
            break


        # Calculate distance in this segment
        segment_dist = min(remaining_dist, threshold - prev_threshold)
        
        # Calculate time for this segment in minutes
        segment_time = (segment_dist / speed) * 60
        total_minutes += segment_time
        
        remaining_dist -= segment_dist
        prev_threshold = threshold


    # Convert to hours and minutes
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    
    # Add time to start time
    result = arrow.get(brevet_start_time).shift(hours=hours, minutes=minutes)
    return result




def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An arrow date-time object indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    # Validate brevet distance (For nose test: test_invalid_brevet_distance)
    valid_distances = [200, 300, 400, 600, 1000]
    if brevet_dist_km not in valid_distances:
        raise ValueError(f"Invalid brevet distance: {brevet_dist_km}. Must be one of {valid_distances}")
    

    # Handle start control (0 km) - closes after 1 hour
    if control_dist_km <= 0:
        return arrow.get(brevet_start_time).shift(hours=1)
    
    # If control distance exceeds brevet distance, cap it at brevet distance
    actual_dist = min(control_dist_km, brevet_dist_km)
    
    # Special rule: controls under 60km
    if actual_dist < 60:
        hours = (actual_dist / 20) + 1
        result = arrow.get(brevet_start_time).shift(hours=hours)
        return result
    
    # Special rule: 200km brevet finish is 13:30 (not 13:20)
    if actual_dist == 200 and brevet_dist_km == 200:
        result = arrow.get(brevet_start_time).shift(hours=13, minutes=30)
        return result
    
    # Special rule: 400km brevet finish is 27:00 (not 26:40)
    if actual_dist == 400 and brevet_dist_km == 400:
        result = arrow.get(brevet_start_time).shift(hours=27)
        return result
    
    # Speed table for closing times (minimum speeds in km/h)
    speed_table = [
        (600, 15),
        (1000, 11.428),
        (1300, 13.333)
    ]
    
    # Calculate time by segments
    total_minutes = 0
    remaining_dist = actual_dist
    prev_threshold = 0
    
    for threshold, speed in speed_table:
        if remaining_dist <= 0:
            break
            
        # Calculate distance in this segment
        segment_dist = min(remaining_dist, threshold - prev_threshold)
        
        # Calculate time for this segment in minutes
        segment_time = (segment_dist / speed) * 60
        total_minutes += segment_time
        
        remaining_dist -= segment_dist
        prev_threshold = threshold
    
    # Convert to hours and minutes
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    
    # Add time to start time
    result = arrow.get(brevet_start_time).shift(hours=hours, minutes=minutes)
    return result