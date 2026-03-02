#include <stdio.h>

int total_records = 0;     // 全局变量
float average_score = 0.0f; // 全局变量

void process_records(int record_count) {  // 符合：参数与全局变量不同名
    int processed = 0;  // 符合：局部变量与全局变量不同名
    for (processed = 0; processed < record_count; processed++) {
        total_records++;
    }
    printf("Processed %d records, total: %d\n", processed, total_records);
}

void calculate_average(float sum, int count) {  // 符合：参数与全局变量不同名
    if (count > 0) {
        average_score = sum / count;
    }
    printf("Average: %.2f\n", average_score);
}

int main(void) {
    process_records(5);
    calculate_average(45.5f, 5);
    return 0;
}