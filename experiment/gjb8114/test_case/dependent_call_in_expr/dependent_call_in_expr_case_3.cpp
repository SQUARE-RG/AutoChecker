#include <stdio.h>

struct Data {
    int count;
    int total;
};

int update_count(struct Data *data) {
    data->count++;
    return data->count;
}

int calculate_total(struct Data *data) {
    data->total = data->count * 10;
    return data->total;
}

int main(void) {
    struct Data my_data = {5, 0};
    int result = update_count(&my_data) + calculate_total(&my_data);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}