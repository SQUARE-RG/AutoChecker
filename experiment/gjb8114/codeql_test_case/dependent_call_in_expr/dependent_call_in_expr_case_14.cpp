#include <stdio.h>

const int READ_ONLY_DATA = 100;

int get_data_a(void) {
    return READ_ONLY_DATA;
}

int get_data_b(void) {
    return READ_ONLY_DATA * 2;
}

int main(void) {
    int result = get_data_a() + get_data_b();  // 符合：只读函数无数据修改
    return result;
}