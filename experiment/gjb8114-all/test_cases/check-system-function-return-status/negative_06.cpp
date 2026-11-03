#include <cstdio>

int main() {
    std::remove("temp_test_file.txt"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
    return 0;
}
