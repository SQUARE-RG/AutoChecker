#include <cstdio>
#include <cstdlib>

int compute(int n) {
    int* data = static_cast<int*>(std::malloc(sizeof(int) * 8));
    if (data == nullptr) {
        return 0;
    }
    int sum = 0;
    if (n <= 0) {
        goto release;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-5-1]
    }
    for (int i = 0; i < n && i < 8; ++i) {
        data[i] = i * i;
        sum += data[i];
    }
release:
    std::free(data);
    return sum;
}

int main() {
    std::printf("%d\n", compute(4));
    return 0;
}
