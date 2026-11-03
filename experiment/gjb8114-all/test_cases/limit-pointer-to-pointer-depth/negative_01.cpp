#include <cstddef>

int main() {
    unsigned int array[5] = {0, 1, 2, 3, 4};
    unsigned int *p1_ptr = array;
    unsigned int **p2_ptr = &p1_ptr;
    unsigned int ***p3_ptr = &p2_ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-1]
    unsigned int data[5] = {};

    for (unsigned int i = 0; i < 5; ++i) {
        data[i] = *(**p3_ptr + i);
    }

    return 0;
}
