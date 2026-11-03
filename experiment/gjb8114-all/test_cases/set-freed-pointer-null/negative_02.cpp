#include <stdlib.h>

int main() {
    int* buffer = (int*)calloc(8, sizeof(int));
    if (buffer == NULL) {
        return 1;
    }
    buffer[3] = 9;
    free(buffer); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-6]
    return 0;
}
