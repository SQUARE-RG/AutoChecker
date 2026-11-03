#include <cstdio>
#include <string>

std::string label(int flag) {
    std::string base;
    if (flag > 0) {
        base = "on";
    } else {
        base = "off";
    }
    std::string result = base + "-state";  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-4]
    return result;
}

int main() {
    std::string text = label(1);
    std::printf("%s\n", text.c_str());
    return 0;
}
