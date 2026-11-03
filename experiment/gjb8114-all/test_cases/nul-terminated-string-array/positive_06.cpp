#include <algorithm>
#include <array>
#include <cstdio>
#include <string>

int main() {
    std::array<char, 4> buf;
    buf.fill('x');
    std::string s = "abc";
    std::copy(s.c_str(), s.c_str() + s.size() + 1, buf.begin());
    std::puts(buf.data());
    return 0;
}
