#include <stdio.h>
#include <time.h>

int get_current_hour(void) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    return tm_info->tm_hour;
}

int get_current_minute(void) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    return tm_info->tm_min;
}

int main(void) {
    int result = get_current_hour() * 60 + get_current_minute();  // 符合：时间函数调用
    return result;
}