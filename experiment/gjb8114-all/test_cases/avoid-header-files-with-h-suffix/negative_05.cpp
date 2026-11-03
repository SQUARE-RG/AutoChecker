#include <time.h>  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-4]

int main() {
    time_t now = time(nullptr);
    return now < static_cast<time_t>(0) ? 1 : 0;
}
