#include <algorithm>
#include <array>
#include <cstdio>

int main() {
    std::array<char, 4> buf;
    buf.fill('x');
    std::copy("abc", "abc" + 3, buf.begin()); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::puts(buf.data());
    return 0;
}
