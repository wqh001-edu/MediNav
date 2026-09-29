# Mission status broadcast
std_msgs/Header header
string order_id
string ward
string state          # IDLE / TO_PHARMACY / WAIT_LOAD / TO_WARD / WAIT_UNLOAD / RETURNING / DONE / ERROR
float32 progress      # 0..1
float32 elapsed_sec
string detail
