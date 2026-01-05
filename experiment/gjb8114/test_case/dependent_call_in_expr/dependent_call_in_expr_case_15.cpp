#include <stdio.h>

int calculate_area(int width, int height) {
    return width * height;
}

int calculate_perimeter(int width, int height) {
    return 2 * (width + height);
}

int main(void) {
    int w = 5, h = 10;
    int result = calculate_area(w, h) + calculate_perimeter(w, h);  // 符合：操作局部变量
    return result;
}