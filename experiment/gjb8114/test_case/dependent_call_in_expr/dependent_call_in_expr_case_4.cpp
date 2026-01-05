#include <stdio.h>

int modify_array(int arr[], int index) {
    arr[index] += 10;
    return arr[index];
}

int get_array_value(int arr[], int index) {
    return arr[index];
}

int main(void) {
    int numbers[3] = {1, 2, 3};
    int result = modify_array(numbers, 0) - get_array_value(numbers, 0);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}