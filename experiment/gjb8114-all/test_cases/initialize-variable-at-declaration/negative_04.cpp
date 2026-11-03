#include <string>

std::string describe(bool flag) {
    std::string text;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
    if (flag) {
        text = "enabled";
    } else {
        text = "disabled";
    }
    return text;
}

int main() {
    return describe(false) == "disabled" ? 0 : 1;
}
