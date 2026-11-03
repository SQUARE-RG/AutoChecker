#include <cstdlib>

int main() {
    int* arr[2]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]
    arr[0] = static_cast<int*>(std::malloc(sizeof(int)));
    if (arr[0] != nullptr) {
        *arr[0] = 1;
        std::free(arr[0]);
    }
    return 0;
}
