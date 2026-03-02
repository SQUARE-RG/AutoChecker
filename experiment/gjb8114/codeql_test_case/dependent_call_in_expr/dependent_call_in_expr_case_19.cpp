#include <stdio.h>

int get_file_size_a(void) {
    FILE *file = fopen("test1.txt", "r");
    if (!file) return 0;
    fseek(file, 0, SEEK_END);
    int size = ftell(file);
    fclose(file);
    return size;
}

int get_file_size_b(void) {
    FILE *file = fopen("test2.txt", "r");
    if (!file) return 0;
    fseek(file, 0, SEEK_END);
    int size = ftell(file);
    fclose(file);
    return size;
}

int main(void) {
    int result = get_file_size_a() + get_file_size_b();  // 符合：操作不同文件
    return result;
}