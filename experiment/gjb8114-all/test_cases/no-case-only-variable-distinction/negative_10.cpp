#include <cstdlib>

int main() {
    int threshold = 10;
    if (int Threshold = 5; threshold > Threshold) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]
        threshold -= Threshold;
    }
    return threshold;
}
