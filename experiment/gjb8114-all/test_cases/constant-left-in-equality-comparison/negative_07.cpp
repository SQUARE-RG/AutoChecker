#include <string>

int main() {
    std::string status = "ready";
    if (status != "ready") { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
        return 1;
    }
    return 0;
}
