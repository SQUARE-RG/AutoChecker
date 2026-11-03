#include <cstring>

int main() {
    char buffer[32] = "start";
    using std::strcat;
    strcat(buffer, "-more");  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
    return 0;
}
